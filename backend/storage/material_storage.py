"""
素材存储层
使用JSON文件进行本地数据持久化
"""
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import threading

from models.material import Material, MaterialType

logger = logging.getLogger(__name__)


class MaterialStorage:
    """素材存储类"""
    
    def __init__(self, storage_dir: str = None):
        """
        初始化存储
        
        Args:
            storage_dir: 存储目录路径
        """
        if storage_dir is None:
            # 使用项目根目录的 storage/materials
            backend_dir = Path(__file__).resolve().parent.parent
            project_root = backend_dir.parent
            storage_dir = project_root / 'storage' / 'materials'
        self.storage_dir = Path(storage_dir)
        self.index_file = self.storage_dir / 'index.json'
        self.lock = threading.Lock()
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        if not self.storage_dir.exists():
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建素材存储目录: {self.storage_dir}")
        
        # 如果索引文件不存在，创建空索引
        if not self.index_file.exists():
            self._save_index([])
    
    def _load_index(self) -> List[Dict[str, Any]]:
        """
        加载索引文件
        
        Returns:
            素材索引列表
        """
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载素材索引失败: {e}", exc_info=True)
            return []
    
    def _save_index(self, index: List[Dict[str, Any]]) -> bool:
        """
        保存索引文件
        
        Args:
            index: 素材索引列表
            
        Returns:
            是否成功
        """
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存素材索引失败: {e}", exc_info=True)
            return False
    
    def save(self, material: Material) -> bool:
        """
        保存素材
        
        Args:
            material: 素材实例
            
        Returns:
            是否成功
        """
        with self.lock:
            try:
                # 验证素材
                is_valid, error_msg = material.validate()
                if not is_valid:
                    logger.error(f"素材验证失败: {error_msg}")
                    return False
                
                # 保存详细数据到单独文件
                detail_file = self.storage_dir / f"{material.id}.json"
                with open(detail_file, 'w', encoding='utf-8') as f:
                    json.dump(material.to_dict(), f, ensure_ascii=False, indent=2)
                
                # 更新索引
                index = self._load_index()
                
                # 创建索引项（只包含摘要信息）
                index_item = {
                    'id': material.id,
                    'name': material.name,
                    'type': material.type.value,
                    'tags': material.tags,
                    'description': material.description,
                    'created_at': material.created_at,
                    'updated_at': material.updated_at
                }
                
                # 检查是否已存在，如果存在则更新
                existing_index = next((i for i, item in enumerate(index) if item['id'] == material.id), None)
                
                if existing_index is not None:
                    index[existing_index] = index_item
                    logger.info(f"更新素材索引: {material.id}")
                else:
                    index.insert(0, index_item)  # 新素材插入到开头
                    logger.info(f"添加素材索引: {material.id}")
                
                # 保存索引
                if self._save_index(index):
                    logger.info(f"素材保存成功: {material.id}")
                    return True
                else:
                    return False
                    
            except Exception as e:
                logger.error(f"保存素材失败: {e}", exc_info=True)
                return False
    
    def get(self, material_id: str) -> Optional[Material]:
        """
        获取素材详情
        
        Args:
            material_id: 素材ID
            
        Returns:
            素材实例
        """
        try:
            detail_file = self.storage_dir / f"{material_id}.json"
            
            if not detail_file.exists():
                logger.warning(f"素材不存在: {material_id}")
                return None
            
            with open(detail_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Material.from_dict(data)
                
        except Exception as e:
            logger.error(f"获取素材失败: {e}", exc_info=True)
            return None
    
    def get_all(
        self,
        material_type: Optional[MaterialType] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Material]:
        """
        获取素材列表
        
        Args:
            material_type: 按类型筛选
            tags: 按标签筛选
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            素材列表
        """
        try:
            index = self._load_index()
            
            # 按更新时间倒序排列
            index.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            # 筛选
            filtered_items = index
            
            if material_type:
                filtered_items = [
                    item for item in filtered_items
                    if item.get('type') == material_type.value
                ]
            
            if tags:
                filtered_items = [
                    item for item in filtered_items
                    if any(tag in item.get('tags', []) for tag in tags)
                ]
            
            # 分页
            if limit:
                filtered_items = filtered_items[offset:offset + limit]
            else:
                filtered_items = filtered_items[offset:]
            
            # 加载完整数据
            materials = []
            for item in filtered_items:
                material = self.get(item['id'])
                if material:
                    materials.append(material)
            
            return materials
                
        except Exception as e:
            logger.error(f"获取素材列表失败: {e}", exc_info=True)
            return []
    
    def get_by_ids(self, material_ids: List[str]) -> List[Material]:
        """
        批量获取素材
        
        Args:
            material_ids: 素材ID列表
            
        Returns:
            素材列表
        """
        materials = []
        for material_id in material_ids:
            material = self.get(material_id)
            if material:
                materials.append(material)
        return materials
    
    def delete(self, material_id: str) -> bool:
        """
        删除素材
        
        Args:
            material_id: 素材ID
            
        Returns:
            是否成功
        """
        with self.lock:
            try:
                # 删除详细数据文件
                detail_file = self.storage_dir / f"{material_id}.json"
                if detail_file.exists():
                    detail_file.unlink()
                    logger.info(f"删除素材文件: {material_id}")
                
                # 更新索引
                index = self._load_index()
                index = [item for item in index if item['id'] != material_id]
                
                if self._save_index(index):
                    logger.info(f"素材删除成功: {material_id}")
                    return True
                else:
                    return False
                    
            except Exception as e:
                logger.error(f"删除素材失败: {e}", exc_info=True)
                return False
    
    def exists(self, material_id: str) -> bool:
        """
        检查素材是否存在
        
        Args:
            material_id: 素材ID
            
        Returns:
            是否存在
        """
        detail_file = self.storage_dir / f"{material_id}.json"
        return detail_file.exists()
    
    def count(
        self,
        material_type: Optional[MaterialType] = None
    ) -> int:
        """
        获取素材总数
        
        Args:
            material_type: 按类型筛选
            
        Returns:
            素材数量
        """
        try:
            index = self._load_index()
            
            if material_type:
                index = [item for item in index if item.get('type') == material_type.value]
            
            return len(index)
        except Exception as e:
            logger.error(f"获取素材数量失败: {e}", exc_info=True)
            return 0
    
    def search(self, keyword: str) -> List[Material]:
        """
        搜索素材
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的素材列表
        """
        try:
            index = self._load_index()
            keyword_lower = keyword.lower()
            
            # 在名称、描述、标签中搜索
            results = []
            for item in index:
                if (keyword_lower in item.get('name', '').lower() or
                    keyword_lower in item.get('description', '').lower() or
                    any(keyword_lower in tag.lower() for tag in item.get('tags', []))):
                    material = self.get(item['id'])
                    if material:
                        results.append(material)
            
            return results
            
        except Exception as e:
            logger.error(f"搜索素材失败: {e}", exc_info=True)
            return []
    
    def get_tags(self) -> List[str]:
        """
        获取所有使用中的标签
        
        Returns:
            标签列表
        """
        try:
            index = self._load_index()
            tags = set()
            for item in index:
                tags.update(item.get('tags', []))
            return sorted(list(tags))
        except Exception as e:
            logger.error(f"获取标签列表失败: {e}", exc_info=True)
            return []