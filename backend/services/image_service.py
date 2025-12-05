"""
图片生成服务
处理批量图片生成的业务逻辑，支持并发生成和实时进度追踪
"""
import logging
import threading
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from datetime import datetime

from generators.factory import get_image_generator
from generators.base import BaseGenerator, ContentType
from .progress_service import ProgressService

logger = logging.getLogger(__name__)


class ImageService:
    """图片生成服务类"""
    
    def __init__(
        self,
        generator_type: str = 'mock',
        max_workers: int = 25,
        model_config: Dict[str, Any] = None
    ):
        """
        初始化服务
        
        Args:
            generator_type: 生成器类型 (mock/image_api/openai)
            max_workers: 最大并发数
            model_config: 模型配置 (url, apiKey, model)
        """
        self.generator_type = generator_type
        self.max_workers = max_workers
        self.model_config = model_config or {}
        self.generator = None
        self.progress_service = ProgressService()
        
        logger.info(f"图片生成服务已初始化: 生成器={generator_type}, 最大并发={max_workers}, 配置={bool(model_config)}")
    
    def generate_batch(
        self,
        task_id: str,
        pages: List[Dict[str, Any]],
        topic: str = '',
        reference_image: Optional[str] = None,
        width: int = 1080,
        height: int = 1440,
        image_generation_config: Optional[Dict[str, Any]] = None,
        full_outline: str = ''
    ) -> None:
        """
        批量生成图片（异步后台任务）
        
        Args:
            task_id: 任务ID
            pages: 页面列表，每页包含 page_number, title, description
            topic: 主题
            reference_image: 参考图片URL
            width: 图片宽度（已弃用，使用 image_generation_config）
            height: 图片高度（已弃用，使用 image_generation_config）
            image_generation_config: 图片生成配置 (quality, aspectRatio)
            full_outline: 完整内容大纲（用于保持风格一致性）
        """
        # 计算实际宽高
        actual_width, actual_height = self._calculate_dimensions(image_generation_config)
        
        # 在新线程中运行，不阻塞主线程
        thread = threading.Thread(
            target=self._generate_batch_worker,
            args=(task_id, pages, topic, reference_image, actual_width, actual_height, full_outline),
            daemon=True
        )
        thread.start()
        logger.info(f"批量生成任务已启动: {task_id}, 共 {len(pages)} 页")
    
    def _generate_batch_worker(
        self,
        task_id: str,
        pages: List[Dict[str, Any]],
        topic: str,
        reference_image: Optional[str],
        width: int,
        height: int,
        full_outline: str = ''
    ):
        """
        批量生成工作线程
        """
        try:
            # 创建进度任务
            self.progress_service.create_task(
                task_id=task_id,
                total_pages=len(pages),
                topic=topic
            )
            
            # 启动任务
            self.progress_service.start_task(task_id)
            
            # 获取生成器（传递模型配置）
            self.generator = self._create_generator_with_config()
            
            if not self.generator:
                error_msg = f'无法创建生成器: {self.generator_type}'
                logger.error(error_msg)
                self.progress_service.fail_task(task_id, error_msg)
                return
            
            # 验证生成器配置
            if not self.generator.validate_config():
                error_msg = f'生成器配置无效: {self.generator_type}'
                logger.error(error_msg)
                self.progress_service.fail_task(task_id, error_msg)
                return
            
            # 使用线程池并发生成图片
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交所有生成任务
                future_to_page = {}
                for page in pages:
                    future = executor.submit(
                        self._generate_single_image,
                        page,
                        reference_image,
                        width,
                        height,
                        topic,
                        pages,
                        full_outline
                    )
                    future_to_page[future] = page
                
                # 处理完成的任务（添加超时机制：每个图片最多5分钟）
                for future in as_completed(future_to_page):
                    page = future_to_page[future]
                    page_number = page.get('page_number', 0)
                    
                    try:
                        result = future.result(timeout=600)  # 5分钟超时
                        
                        if result['success']:
                            # 更新进度
                            self.progress_service.update_progress(
                                task_id=task_id,
                                current_page=page_number,
                                image_url=result['image_url'],
                                message=f'第 {page_number} 页生成完成'
                            )
                            logger.info(f"页面 {page_number} 生成成功")
                        else:
                            # 记录失败页面
                            error_msg = result.get('error', '未知错误')
                            self.progress_service.record_failed_page(
                                task_id=task_id,
                                page_number=page_number,
                                error=error_msg
                            )
                            logger.error(f"页面 {page_number} 生成失败: {error_msg}")
                            # 继续生成其他页面，不中断整个任务
                            
                    except TimeoutError:
                        # 超时异常
                        error_msg = "图片生成超时（超过5分钟）"
                        self.progress_service.record_failed_page(
                            task_id=task_id,
                            page_number=page_number,
                            error=error_msg
                        )
                        logger.error(f"页面 {page_number} 生成超时")
                    except Exception as e:
                        # 其他异常情况也记录为失败
                        error_msg = f"处理结果异常: {str(e)}"
                        self.progress_service.record_failed_page(
                            task_id=task_id,
                            page_number=page_number,
                            error=error_msg
                        )
                        logger.error(f"处理页面 {page_number} 结果时出错: {e}", exc_info=True)
            
            # 检查是否所有图片都生成成功
            progress = self.progress_service.get_progress(task_id)
            if progress and progress['completed_pages'] == len(pages):
                self.progress_service.complete_task(
                    task_id=task_id,
                    message='所有图片生成完成！'
                )
                logger.info(f"任务完成: {task_id}")
            else:
                completed = progress['completed_pages'] if progress else 0
                self.progress_service.complete_task(
                    task_id=task_id,
                    message=f'生成完成，成功 {completed}/{len(pages)} 页'
                )
                logger.warning(f"任务部分完成: {task_id}, 成功 {completed}/{len(pages)}")
            
        except Exception as e:
            error_msg = f'批量生成失败: {str(e)}'
            logger.error(f"任务失败: {task_id}, {error_msg}", exc_info=True)
            self.progress_service.fail_task(task_id, error_msg)
    
    def _generate_single_image(
        self,
        page: Dict[str, Any],
        reference_image: Optional[str],
        width: int,
        height: int,
        topic: str = '',
        all_pages: List[Dict[str, Any]] = None,
        full_outline: str = ''
    ) -> Dict[str, Any]:
        """
        生成单张图片
        
        Args:
            page: 页面信息
            reference_image: 参考图片
            width: 宽度
            height: 高度
            topic: 用户原始需求
            all_pages: 所有页面列表（用于获取封面信息）
            full_outline: 完整内容大纲
            
        Returns:
            生成结果
        """
        try:
            # 如果有参考图片且是本地路径，转换为 base64 Data URL
            processed_reference = self._process_reference_image(reference_image)
            
            # 构建提示词
            prompt = self._build_prompt(page, topic, all_pages, full_outline, processed_reference)
            
            # 生成图片 - 使用统一的 generate 接口
            generation_result = self.generator.generate(
                content_type=ContentType.IMAGE,
                prompt=prompt,
                width=width,
                height=height,
                reference_image=processed_reference
            )
            
            # 转换为旧格式以保持兼容性
            if generation_result.success:
                return {
                    'success': True,
                    'image_url': generation_result.url
                }
            else:
                return {
                    'success': False,
                    'error': generation_result.error
                }
            
        except Exception as e:
            logger.error(f"生成图片失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_dimensions(self, config: Optional[Dict[str, Any]]) -> tuple[int, int]:
        """
        根据配置计算图片尺寸
        
        Args:
            config: 图片生成配置 {quality: '1k|2k|4k', aspectRatio: '4:3|...'}
            
        Returns:
            (width, height) 元组
        """
        if not config:
            # 默认配置：2K 质量，3:4 比例（小红书常用）
            return (1080, 1440)
        
        quality = config.get('quality', '2k')
        aspect_ratio = config.get('aspectRatio', '3:4')
        
        # 定义质量等级对应的像素数（短边）
        quality_map = {
            '1k': 720,   # 1K
            '2k': 1080,  # 2K
            '4k': 2160   # 4K
        }
        
        base_size = quality_map.get(quality, 1080)
        
        # 解析宽高比
        try:
            ratio_parts = aspect_ratio.split(':')
            if len(ratio_parts) != 2:
                logger.warning(f"无效的宽高比格式: {aspect_ratio}，使用默认3:4")
                ratio_w, ratio_h = 3, 4
            else:
                ratio_w = int(ratio_parts[0])
                ratio_h = int(ratio_parts[1])
        except Exception as e:
            logger.error(f"解析宽高比失败: {e}，使用默认3:4")
            ratio_w, ratio_h = 3, 4
        
        # 根据比例计算实际尺寸
        if ratio_w < ratio_h:
            # 竖版：短边是宽度
            width = base_size
            height = int(base_size * ratio_h / ratio_w)
        elif ratio_w > ratio_h:
            # 横版：短边是高度
            height = base_size
            width = int(base_size * ratio_w / ratio_h)
        else:
            # 正方形
            width = height = base_size
        
        logger.info(f"计算图片尺寸: 质量={quality}, 比例={aspect_ratio}, 尺寸={width}x{height}")
        return (width, height)
    
    def _build_prompt(
        self,
        page: Dict[str, Any],
        user_topic: str = '',
        all_pages: List[Dict[str, Any]] = None,
        full_outline: str = '',
        reference_image: Optional[str] = None
    ) -> str:
        """
        根据页面信息构建图片生成提示词（精简版）
        
        Args:
            page: 当前页面信息
            user_topic: 用户原始需求
            all_pages: 所有页面列表
            full_outline: 完整内容大纲
            reference_image: 参考图片URL
            
        Returns:
            简洁的图片生成提示词
        """
        page_content = page.get('description', '')
        page_number = page.get('page_number', 1)
        title = page.get('title', '')
        
        # 判断页面类型
        page_type = '内容页'
        if '[封面]' in title or '[封面]' in page_content or page_number == 1:
            page_type = '封面'
        elif '[总结]' in title or '[总结]' in page_content:
            page_type = '总结页'
        
        # 精简版提示词 - 控制在1000字符以内
        prompt_parts = []
        
        # 1. 核心内容（最重要）
        prompt_parts.append(f"小红书风格图文内容 - {page_type}")
        
        # 2. 页面具体内容（限制长度）
        content_limit = 500
        if len(page_content) > content_limit:
            page_content = page_content[:content_limit] + "..."
        prompt_parts.append(f"内容: {page_content}")
        
        # 3. 设计要求（精简）
        if page_type == '封面':
            prompt_parts.append("设计: 标题大而醒目，副标题清晰，吸引眼球，竖版3:4比例")
        elif page_type == '总结页':
            prompt_parts.append("设计: 总结性文字突出，完成感，鼓励性，竖版3:4比例")
        else:
            prompt_parts.append("设计: 信息层次分明，列表清晰，重点突出，竖版3:4比例")
        
        # 4. 风格要求（精简）
        prompt_parts.append("风格: 小红书爆款风格，清新精致，年轻人审美，配色和谐，高清画质")
        
        # 5. 合规要求（重要）
        prompt_parts.append("注意: 不要小红书logo，不要用户id，不要水印，不要手机边框")
        
        # 6. 风格一致性（仅在非封面时添加，且精简）
        if page_type != '封面' and all_pages and len(all_pages) > 0:
            cover_page = all_pages[0]
            cover_title = cover_page.get('title', '')
            prompt_parts.append(f"保持与封面({cover_title})风格一致")
        
        # 组合提示词
        prompt = " | ".join(prompt_parts)
        
        # 最终检查长度（确保不超过1000字符）
        if len(prompt) > 1000:
            logger.warning(f"提示词长度 {len(prompt)} 超过1000，进行截断")
            prompt = prompt[:1000]
        
        logger.info(f"生成提示词长度: {len(prompt)} 字符")
        
        return prompt
    
    def get_supported_generators(self) -> List[str]:
        """
        获取支持的生成器列表
        
        Returns:
            生成器类型列表
        """
        from generators.factory import GeneratorFactory
        available = GeneratorFactory.get_available_generators()
        return available.get('image_generators', [])
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务（标记为失败）
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功
        """
        if not self.progress_service.task_exists(task_id):
            return False
        
        if self.progress_service.is_task_completed(task_id):
            logger.warning(f"任务已完成，无法取消: {task_id}")
            return False
        
        return self.progress_service.fail_task(task_id, '用户取消任务')
    
    def get_task_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务进度
        
        Args:
            task_id: 任务ID
            
        Returns:
            进度信息
        """
        return self.progress_service.get_progress(task_id)
    
    def validate_pages(self, pages: List[Dict[str, Any]]) -> tuple[bool, str]:
        """
        验证页面数据格式
        
        Args:
            pages: 页面列表
            
        Returns:
            (是否有效, 错误信息)
        """
        if not pages or not isinstance(pages, list):
            return False, '页面列表不能为空'
        
        if len(pages) == 0:
            return False, '至少需要一页内容'
        
        if len(pages) > 50:
            return False, '页面数量不能超过50页'
        
        # 检查每一页的格式
        for i, page in enumerate(pages):
            if not isinstance(page, dict):
                return False, f'第{i+1}页数据格式错误'
            
            # 检查必需字段（兼容 page_number 和 page 两种格式）
            page_num = page.get('page_number') or page.get('page')
            if page_num is None:
                return False, f'第{i+1}页缺少必需字段: page_number 或 page'
            
            # 自动规范化：如果只有 page 字段，补充 page_number
            if 'page_number' not in page and 'page' in page:
                page['page_number'] = page['page']
            
            if 'title' not in page:
                return False, f'第{i+1}页缺少必需字段: title'
                
            if 'description' not in page:
                return False, f'第{i+1}页缺少必需字段: description'
            
            # 验证字段值
            if not isinstance(page['title'], str) or not page['title'].strip():
                return False, f'第{i+1}页的title不能为空'
            
            if not isinstance(page['description'], str) or not page['description'].strip():
                return False, f'第{i+1}页的description不能为空'
        
        return True, ''
    
    def _create_generator_with_config(self) -> Optional[BaseGenerator]:
        """
        根据配置创建生成器
        
        Returns:
            生成器实例
        """
        try:
            # 检查是否有有效的自定义配置（非空字符串）
            has_custom_config = (
                self.model_config and
                self.model_config.get('url') and
                self.model_config.get('url').strip() and
                self.model_config.get('apiKey') and
                self.model_config.get('apiKey').strip()
            )
            
            if has_custom_config:
                logger.info(f"使用自定义配置创建图片生成器: {self.generator_type}")
                logger.info(f"自定义配置 - URL: {self.model_config['url']}, Model: {self.model_config.get('model', 'dall-e-3')}")
                
                if self.generator_type == 'image_api':
                    from generators.generators.image_generator import ImageGenerator
                    return ImageGenerator(
                        provider='image_api',
                        api_key=self.model_config['apiKey'],
                        api_url=self.model_config['url'],
                        model=self.model_config.get('model', 'dall-e-3'),
                        apiFormat=self.model_config.get('apiFormat', 'openai_dalle')
                    )
                elif self.generator_type == 'openai':
                    from generators.generators.image_generator import ImageGenerator
                    return ImageGenerator(
                        provider='openai',
                        api_key=self.model_config['apiKey'],
                        base_url=self.model_config['url'],
                        model=self.model_config.get('model', 'dall-e-3')
                    )
            
            # 否则使用默认配置
            logger.info(f"使用默认配置创建图片生成器: {self.generator_type}")
            return get_image_generator(self.generator_type)
            
        except Exception as e:
            logger.error(f"创建图片生成器失败: {e}", exc_info=True)
            return None
    
    def _process_reference_image(self, reference_image: Optional[str]) -> Optional[str]:
        """
        处理参考图片：将本地文件路径转换为 base64 Data URL
        
        Args:
            reference_image: 参考图片路径或URL
            
        Returns:
            处理后的图片（base64 Data URL 或 HTTP URL）
        """
        if not reference_image:
            return None
        
        # 如果已经是 Data URL 或 HTTP URL，直接返回
        if reference_image.startswith('data:image') or \
           reference_image.startswith('http://') or \
           reference_image.startswith('https://'):
            return reference_image
        
        # 本地文件路径，需要转换为 base64
        try:
            import base64
            import mimetypes
            from pathlib import Path
            
            # 构建完整文件路径
            if reference_image.startswith('/uploads/'):
                file_path = Path('uploads') / reference_image.replace('/uploads/', '')
            elif reference_image.startswith('uploads/'):
                file_path = Path(reference_image)
            else:
                file_path = Path('uploads') / reference_image
            
            if not file_path.exists():
                logger.warning(f"参考图片文件不存在: {file_path}")
                return None
            
            # 读取文件内容
            with open(file_path, 'rb') as f:
                image_data = f.read()
            
            # 编码为 base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # 获取 MIME 类型
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                mime_type = 'image/jpeg'  # 默认
            
            # 构建 Data URL
            data_url = f"data:{mime_type};base64,{base64_data}"
            
            logger.info(f"参考图片转换为 base64 成功: {file_path} -> {len(base64_data)} 字符")
            
            return data_url
            
        except Exception as e:
            logger.error(f"处理参考图片失败: {e}", exc_info=True)
            return None