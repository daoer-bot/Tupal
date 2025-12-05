"""
模板存储层
使用JSON文件进行本地数据持久化
"""
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import threading

from models.template import Template, TemplateType

logger = logging.getLogger(__name__)


class TemplateStorage:
    """模板存储类"""
    
    def __init__(self, storage_dir: str = None):
        """
        初始化存储
        
        Args:
            storage_dir: 存储目录路径
        """
        if storage_dir is None:
            backend_dir = Path(__file__).resolve().parent.parent
            project_root = backend_dir.parent
            storage_dir = project_root / 'storage' / 'templates'
        self.storage_dir = Path(storage_dir)
        self.index_file = self.storage_dir / 'index.json'
        self.lock = threading.Lock()
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        if not self.storage_dir.exists():
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建模板存储目录: {self.storage_dir}")
        
        if not self.index_file.exists():
            self._save_index([])
    
    def _load_index(self) -> List[Dict[str, Any]]:
        """加载索引文件"""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载模板索引失败: {e}", exc_info=True)
            return []
    
    def _save_index(self, index: List[Dict[str, Any]]) -> bool:
        """保存索引文件"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存模板索引失败: {e}", exc_info=True)
            return False
    
    def save(self, template: Template) -> bool:
        """保存模板"""
        with self.lock:
            try:
                is_valid, error_msg = template.validate()
                if not is_valid:
                    logger.error(f"模板验证失败: {error_msg}")
                    return False
                
                detail_file = self.storage_dir / f"{template.id}.json"
                with open(detail_file, 'w', encoding='utf-8') as f:
                    json.dump(template.to_dict(), f, ensure_ascii=False, indent=2)
                
                index = self._load_index()
                
                index_item = {
                    'id': template.id,
                    'name': template.name,
                    'type': template.type.value,
                    'category': template.category,
                    'tags': template.tags,
                    'description': template.description,
                    'thumbnail': template.thumbnail,
                    'usage_count': template.usage_count,
                    'created_at': template.created_at,
                    'updated_at': template.updated_at
                }
                
                existing_index = next((i for i, item in enumerate(index) if item['id'] == template.id), None)
                
                if existing_index is not None:
                    index[existing_index] = index_item
                    logger.info(f"更新模板索引: {template.id}")
                else:
                    index.insert(0, index_item)
                    logger.info(f"添加模板索引: {template.id}")
                
                if self._save_index(index):
                    logger.info(f"模板保存成功: {template.id}")
                    return True
                else:
                    return False
                    
            except Exception as e:
                logger.error(f"保存模板失败: {e}", exc_info=True)
                return False
    
    def get(self, template_id: str) -> Optional[Template]:
        """获取模板详情"""
        try:
            detail_file = self.storage_dir / f"{template_id}.json"
            
            if not detail_file.exists():
                logger.warning(f"模板不存在: {template_id}")
                return None
            
            with open(detail_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Template.from_dict(data)
                
        except Exception as e:
            logger.error(f"获取模板失败: {e}", exc_info=True)
            return None
    
    def get_all(
        self,
        template_type: Optional[TemplateType] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Template]:
        """获取模板列表"""
        try:
            index = self._load_index()
            
            index.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            filtered_items = index
            
            if template_type:
                filtered_items = [
                    item for item in filtered_items
                    if item.get('type') == template_type.value
                ]
            
            if category:
                filtered_items = [
                    item for item in filtered_items
                    if item.get('category') == category
                ]
            
            if tags:
                filtered_items = [
                    item for item in filtered_items
                    if any(tag in item.get('tags', []) for tag in tags)
                ]
            
            if limit:
                filtered_items = filtered_items[offset:offset + limit]
            else:
                filtered_items = filtered_items[offset:]
            
            templates = []
            for item in filtered_items:
                template = self.get(item['id'])
                if template:
                    templates.append(template)
            
            return templates
                
        except Exception as e:
            logger.error(f"获取模板列表失败: {e}", exc_info=True)
            return []
    
    def get_by_ids(self, template_ids: List[str]) -> List[Template]:
        """批量获取模板"""
        templates = []
        for template_id in template_ids:
            template = self.get(template_id)
            if template:
                templates.append(template)
        return templates
    
    def delete(self, template_id: str) -> bool:
        """删除模板"""
        with self.lock:
            try:
                detail_file = self.storage_dir / f"{template_id}.json"
                if detail_file.exists():
                    detail_file.unlink()
                    logger.info(f"删除模板文件: {template_id}")
                
                index = self._load_index()
                index = [item for item in index if item['id'] != template_id]
                
                if self._save_index(index):
                    logger.info(f"模板删除成功: {template_id}")
                    return True
                else:
                    return False
                    
            except Exception as e:
                logger.error(f"删除模板失败: {e}", exc_info=True)
                return False
    
    def exists(self, template_id: str) -> bool:
        """检查模板是否存在"""
        detail_file = self.storage_dir / f"{template_id}.json"
        return detail_file.exists()
    
    def count(
        self,
        template_type: Optional[TemplateType] = None,
        category: Optional[str] = None
    ) -> int:
        """获取模板总数"""
        try:
            index = self._load_index()
            
            if template_type:
                index = [item for item in index if item.get('type') == template_type.value]
            
            if category:
                index = [item for item in index if item.get('category') == category]
            
            return len(index)
        except Exception as e:
            logger.error(f"获取模板数量失败: {e}", exc_info=True)
            return 0
    
    def search(self, keyword: str) -> List[Template]:
        """搜索模板"""
        try:
            index = self._load_index()
            keyword_lower = keyword.lower()
            
            results = []
            for item in index:
                if (keyword_lower in item.get('name', '').lower() or
                    keyword_lower in item.get('description', '').lower() or
                    any(keyword_lower in tag.lower() for tag in item.get('tags', []))):
                    template = self.get(item['id'])
                    if template:
                        results.append(template)
            
            return results
            
        except Exception as e:
            logger.error(f"搜索模板失败: {e}", exc_info=True)
            return []
    
    def get_popular(self, limit: int = 10) -> List[Template]:
        """获取热门模板（按使用次数排序）"""
        try:
            index = self._load_index()
            index.sort(key=lambda x: x.get('usage_count', 0), reverse=True)
            
            popular_items = index[:limit]
            
            templates = []
            for item in popular_items:
                template = self.get(item['id'])
                if template:
                    templates.append(template)
            
            return templates
            
        except Exception as e:
            logger.error(f"获取热门模板失败: {e}", exc_info=True)
            return []
    
    def increment_usage_count(self, template_id: str) -> bool:
        """增加模板使用次数"""
        with self.lock:
            try:
                template = self.get(template_id)
                if not template:
                    return False
                
                template.usage_count += 1
                return self.save(template)
                
            except Exception as e:
                logger.error(f"增加使用次数失败: {e}", exc_info=True)
                return False
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        try:
            index = self._load_index()
            categories = set()
            for item in index:
                if item.get('category'):
                    categories.add(item['category'])
            return sorted(list(categories))
        except Exception as e:
            logger.error(f"获取分类列表失败: {e}", exc_info=True)
            return []
    
    def get_tags(self) -> List[str]:
        """获取所有标签"""
        try:
            index = self._load_index()
            tags = set()
            for item in index:
                tags.update(item.get('tags', []))
            return sorted(list(tags))
        except Exception as e:
            logger.error(f"获取标签列表失败: {e}", exc_info=True)
            return []