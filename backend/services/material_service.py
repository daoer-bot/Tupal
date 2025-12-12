"""
素材服务层
处理素材相关的业务逻辑
"""
import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.material import (
    Material, MaterialType,
    create_text, create_image, create_reference
)
from storage.material_storage import MaterialStorage

logger = logging.getLogger(__name__)


class MaterialService:
    """素材服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.storage = MaterialStorage()
    
    def create_material(
        self,
        name: str,
        material_type: str,
        content: Dict[str, Any],
        category: str = "",
        tags: List[str] = None,
        description: str = ""
    ) -> Optional[str]:
        """
        创建素材

        Args:
            name: 素材名称
            material_type: 素材类型
            content: 素材内容
            category: 素材分类
            tags: 标签列表
            description: 描述

        Returns:
            素材ID，失败返回None
        """
        try:
            # 类型转换
            mat_type = MaterialType(material_type)
            
            # 根据类型创建素材实例
            if mat_type == MaterialType.TEXT:
                material = create_text(name, content.get('text', ''), **content)
            elif mat_type == MaterialType.IMAGE:
                material = create_image(name, content.get('url', ''), **content)
            elif mat_type == MaterialType.REFERENCE:
                ref_type = content.get('reference_type', '')
                # 避免重复传递reference_type
                content_copy = {k: v for k, v in content.items() if k != 'reference_type'}
                material = create_reference(name, ref_type, **content_copy)
            else:
                logger.error(f"不支持的素材类型: {material_type}")
                return None
            
            # 设置标签和描述
            if tags:
                material.tags = tags
            if description:
                material.description = description
            
            # 保存
            if self.storage.save(material):
                logger.info(f"素材创建成功: {material.id}")
                return material.id
            else:
                logger.error("素材保存失败")
                return None
                
        except ValueError as e:
            logger.error(f"无效的素材类型或分类: {e}")
            return None
        except Exception as e:
            logger.error(f"创建素材失败: {e}", exc_info=True)
            return None
    
    def update_material(
        self,
        material_id: str,
        name: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> bool:
        """
        更新素材
        
        Args:
            material_id: 素材ID
            name: 新名称
            content: 新内容
            tags: 新标签列表
            description: 新描述
            
        Returns:
            是否成功
        """
        try:
            # 获取现有素材
            material = self.storage.get(material_id)
            if not material:
                logger.error(f"素材不存在: {material_id}")
                return False
            
            # 更新字段
            if name is not None:
                material.name = name
            if content is not None:
                material.content = content
            if tags is not None:
                material.tags = tags
            if description is not None:
                material.description = description
            
            # 更新时间戳
            material.updated_at = datetime.now().isoformat()
            
            # 保存
            if self.storage.save(material):
                logger.info(f"素材更新成功: {material_id}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"更新素材失败: {e}", exc_info=True)
            return False
    
    def delete_material(self, material_id: str) -> bool:
        """
        删除素材
        
        Args:
            material_id: 素材ID
            
        Returns:
            是否成功
        """
        try:
            return self.storage.delete(material_id)
        except Exception as e:
            logger.error(f"删除素材失败: {e}", exc_info=True)
            return False
    
    def get_material(self, material_id: str) -> Optional[Dict[str, Any]]:
        """
        获取素材详情
        
        Args:
            material_id: 素材ID
            
        Returns:
            素材数据字典
        """
        try:
            material = self.storage.get(material_id)
            if material:
                return material.to_dict()
            return None
        except Exception as e:
            logger.error(f"获取素材失败: {e}", exc_info=True)
            return None
    
    def get_materials(
        self,
        material_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取素材列表（分页）
        
        Args:
            material_type: 按类型筛选
            tags: 按标签筛选
            page: 页码
            page_size: 每页数量
            
        Returns:
            包含素材列表和分页信息的字典
        """
        try:
            # 类型转换
            mat_type = MaterialType(material_type) if material_type else None
            
            # 计算偏移量
            offset = (page - 1) * page_size
            
            # 获取素材列表
            materials = self.storage.get_all(
                material_type=mat_type,
                tags=tags,
                limit=page_size,
                offset=offset
            )
            
            # 获取总数
            total = self.storage.count(material_type=mat_type)
            
            # 转换为字典
            items = [material.to_dict() for material in materials]
            
            return {
                'items': items,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total': total,
                    'total_pages': (total + page_size - 1) // page_size,
                    'has_more': offset + len(items) < total
                }
            }
            
        except Exception as e:
            logger.error(f"获取素材列表失败: {e}", exc_info=True)
            return {
                'items': [],
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total': 0,
                    'total_pages': 0,
                    'has_more': False
                }
            }
    
    def search_materials(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索素材
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            素材列表
        """
        try:
            materials = self.storage.search(keyword)
            return [material.to_dict() for material in materials]
        except Exception as e:
            logger.error(f"搜索素材失败: {e}", exc_info=True)
            return []
    
    def get_materials_by_ids(self, material_ids: List[str]) -> List[Dict[str, Any]]:
        """
        批量获取素材（用于引用处理）
        
        Args:
            material_ids: 素材ID列表
            
        Returns:
            素材列表
        """
        try:
            materials = self.storage.get_by_ids(material_ids)
            return [material.to_dict() for material in materials]
        except Exception as e:
            logger.error(f"批量获取素材失败: {e}", exc_info=True)
            return []
    
    def get_tags(self) -> List[str]:
        """
        获取所有标签
        
        Returns:
            标签列表
        """
        try:
            return self.storage.get_tags()
        except Exception as e:
            logger.error(f"获取标签列表失败: {e}", exc_info=True)
            return []
    
    @staticmethod
    def extract_mention_ids(text: str) -> List[str]:
        """
        从文本中提取 @[素材名](material_id) 格式的素材ID
        
        Args:
            text: 包含 @mention 的文本
            
        Returns:
            素材ID列表
            
        Example:
            >>> text = "使用 @[iPhone素材](mat_001) 和 @[风格模板](mat_002)"
            >>> extract_mention_ids(text)
            ['mat_001', 'mat_002']
        """
        pattern = r'@\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, text)
        # matches 是 [(name1, id1), (name2, id2), ...]
        material_ids = [match[1] for match in matches]
        return material_ids
    
    @staticmethod
    def replace_mentions_with_content(text: str, materials: List[Dict[str, Any]]) -> str:
        """
        将文本中的 @mention 标记替换为实际素材内容引用
        
        Args:
            text: 包含 @mention 的文本
            materials: 素材数据列表
            
        Returns:
            替换后的文本
            
        Example:
            >>> text = "产品介绍：@[iPhone素材](mat_001)"
            >>> materials = [{'id': 'mat_001', 'name': 'iPhone素材', 'content': {...}}]
            >>> replace_mentions_with_content(text, materials)
            "产品介绍：【引用：iPhone素材】"
        """
        # 创建 ID 到素材的映射
        material_map = {m['id']: m for m in materials}
        
        def replacer(match):
            material_name = match.group(1)
            material_id = match.group(2)
            
            if material_id in material_map:
                return f"【引用：{material_name}】"
            else:
                # 如果素材不存在，保持原样
                return match.group(0)
        
        pattern = r'@\[([^\]]+)\]\(([^)]+)\)'
        return re.sub(pattern, replacer, text)
    
    def process_material_references(
        self,
        material_ids: List[str],
        base_prompt: str = ""
    ) -> Dict[str, Any]:
        """
        处理素材引用，组装增强后的提示词和参考资源
        
        支持两种引用方式：
        1. 直接传入 material_ids 列表
        2. 在 base_prompt 中使用 @[素材名](material_id) 格式
        
        Args:
            material_ids: 素材ID列表
            base_prompt: 基础提示词（可包含 @mention 标记）
            
        Returns:
            包含增强提示词、参考图片、风格参数的字典
        """
        try:
            # 从 base_prompt 中提取 @mention 的素材ID
            mentioned_ids = self.extract_mention_ids(base_prompt)
            
            # 合并两种方式的素材ID（去重）
            all_material_ids = list(set(material_ids + mentioned_ids))
            
            # 获取所有素材
            materials = self.storage.get_by_ids(all_material_ids)
            
            # 将 @mention 标记替换为引用标记
            enhanced_prompt = self.replace_mentions_with_content(
                base_prompt,
                [m.to_dict() for m in materials]
            )
            
            reference_images = []
            style_params = {}
            
            for material in materials:
                if material.type == MaterialType.TEXT:
                    # 文本素材：注入到提示词
                    text_content = material.content.get('text', '')
                    if text_content:
                        enhanced_prompt += f"\n\n【参考信息-{material.name}】\n{text_content}"
                
                elif material.type == MaterialType.IMAGE:
                    # 图片素材：添加到参考图片列表
                    image_url = material.content.get('url')
                    if image_url:
                        reference_images.append(image_url)
                
                elif material.type == MaterialType.REFERENCE:
                    # 参考素材：提取参考信息
                    reference_type = material.content.get('reference_type', '')
                    if reference_type:
                        enhanced_prompt += f"\n\n【参考-{material.name}】类型：{reference_type}"
                    
                    # 其他参考内容
                    if 'content' in material.content:
                        enhanced_prompt += f"\n{material.content['content']}"
                    if 'account' in material.content:
                        enhanced_prompt += f"\n账号：{material.content['account']}"
            
            logger.info(f"素材引用处理完成，引用了 {len(materials)} 个素材")
            
            return {
                'enhanced_prompt': enhanced_prompt.strip(),
                'reference_images': reference_images,
                'style_params': style_params,
                'materials_used': [m.to_dict() for m in materials]
            }
            
        except Exception as e:
            logger.error(f"处理素材引用失败: {e}", exc_info=True)
            return {
                'enhanced_prompt': base_prompt,
                'reference_images': [],
                'style_params': {},
                'materials_used': []
            }
    
    def validate_material_data(
        self,
        material_type: str,
        content: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        验证素材数据
        
        Args:
            material_type: 素材类型
            content: 素材内容
            
        Returns:
            (是否有效, 错误信息)
        """
        try:
            mat_type = MaterialType(material_type)
            
            if mat_type == MaterialType.TEXT:
                if 'text' not in content or not content['text']:
                    return False, "文本素材必须包含非空的text字段"
            
            elif mat_type == MaterialType.IMAGE:
                if 'url' not in content or not content['url']:
                    return False, "图片素材必须包含非空的url字段"
            
            elif mat_type == MaterialType.REFERENCE:
                if 'reference_type' not in content:
                    return False, "参考素材必须包含reference_type字段"
            
            return True, None
            
        except ValueError:
            return False, f"无效的素材类型: {material_type}"
        except Exception as e:
            return False, str(e)