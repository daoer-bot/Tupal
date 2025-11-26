"""
图片生成服务
处理批量图片生成的业务逻辑，支持并发生成和实时进度追踪
"""
import logging
import threading
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from generators.factory import get_image_generator
from .progress_service import ProgressService

logger = logging.getLogger(__name__)


class ImageService:
    """图片生成服务类"""
    
    def __init__(
        self,
        generator_type: str = 'mock',
        max_workers: int = 25
    ):
        """
        初始化服务
        
        Args:
            generator_type: 生成器类型 (mock/image_api/openai)
            max_workers: 最大并发数
        """
        self.generator_type = generator_type
        self.max_workers = max_workers
        self.generator = None
        self.progress_service = ProgressService()
        
        logger.info(f"图片生成服务已初始化: 生成器={generator_type}, 最大并发={max_workers}")
    
    def generate_batch(
        self,
        task_id: str,
        pages: List[Dict[str, Any]],
        topic: str = '',
        reference_image: Optional[str] = None,
        width: int = 1080,
        height: int = 1440
    ) -> None:
        """
        批量生成图片（异步后台任务）
        
        Args:
            task_id: 任务ID
            pages: 页面列表，每页包含 page_number, title, description
            topic: 主题
            reference_image: 参考图片URL
            width: 图片宽度
            height: 图片高度
        """
        # 在新线程中运行，不阻塞主线程
        thread = threading.Thread(
            target=self._generate_batch_worker,
            args=(task_id, pages, topic, reference_image, width, height),
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
        height: int
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
            
            # 获取生成器
            self.generator = get_image_generator(self.generator_type)
            
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
                        height
                    )
                    future_to_page[future] = page
                
                # 处理完成的任务
                for future in as_completed(future_to_page):
                    page = future_to_page[future]
                    page_number = page.get('page_number', 0)
                    
                    try:
                        result = future.result()
                        
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
                            
                    except Exception as e:
                        # 异常情况也记录为失败
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
        height: int
    ) -> Dict[str, Any]:
        """
        生成单张图片
        
        Args:
            page: 页面信息
            reference_image: 参考图片
            width: 宽度
            height: 高度
            
        Returns:
            生成结果
        """
        try:
            # 构建提示词
            prompt = self._build_prompt(page)
            
            # 生成图片
            result = self.generator.generate_image(
                prompt=prompt,
                width=width,
                height=height,
                reference_image=reference_image
            )
            
            return result
            
        except Exception as e:
            logger.error(f"生成图片失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_prompt(self, page: Dict[str, Any]) -> str:
        """
        根据页面信息构建提示词
        
        Args:
            page: 页面信息
            
        Returns:
            提示词
        """
        title = page.get('title', '')
        description = page.get('description', '')
        
        # 构建详细的提示词
        prompt = f"{title}. {description}"
        
        # 添加小红书风格提示
        prompt += " 小红书风格，简洁美观，适合社交媒体分享"
        
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
            
            required_fields = ['page_number', 'title', 'description']
            for field in required_fields:
                if field not in page:
                    return False, f'第{i+1}页缺少必需字段: {field}'
                
                if not page[field]:
                    return False, f'第{i+1}页的{field}不能为空'
        
        return True, ''