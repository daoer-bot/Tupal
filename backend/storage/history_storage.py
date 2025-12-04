"""
历史记录存储
使用JSON文件进行本地数据持久化
"""
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import threading

logger = logging.getLogger(__name__)


class HistoryStorage:
    """历史记录存储类"""
    
    def __init__(self, storage_dir: str = None):
        """
        初始化存储
        
        Args:
            storage_dir: 存储目录路径
        """
        if storage_dir is None:
            # 使用项目根目录的 storage/history
            backend_dir = Path(__file__).resolve().parent.parent
            project_root = backend_dir.parent
            storage_dir = project_root / 'storage' / 'history'
        self.storage_dir = Path(storage_dir)
        self.index_file = self.storage_dir / 'index.json'
        self.lock = threading.Lock()
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        if not self.storage_dir.exists():
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建存储目录: {self.storage_dir}")
        
        # 如果索引文件不存在，创建空索引
        if not self.index_file.exists():
            self._save_index([])
    
    def _load_index(self) -> List[Dict[str, Any]]:
        """
        加载索引文件
        
        Returns:
            历史记录列表
        """
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载索引失败: {e}", exc_info=True)
            return []
    
    def _save_index(self, index: List[Dict[str, Any]]) -> bool:
        """
        保存索引文件
        
        Args:
            index: 历史记录列表
            
        Returns:
            是否成功
        """
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存索引失败: {e}", exc_info=True)
            return False
    
    def save(self, history_data: Dict[str, Any]) -> bool:
        """
        保存历史记录
        
        Args:
            history_data: 历史记录数据，必须包含id字段
            
        Returns:
            是否成功
        """
        with self.lock:
            try:
                history_id = history_data.get('id')
                if not history_id:
                    logger.error("历史记录缺少id字段")
                    return False
                
                # 保存详细数据到单独文件
                detail_file = self.storage_dir / f"{history_id}.json"
                with open(detail_file, 'w', encoding='utf-8') as f:
                    json.dump(history_data, f, ensure_ascii=False, indent=2)
                
                # 更新索引
                index = self._load_index()
                
                # 创建索引项（只包含摘要信息）
                index_item = {
                    'id': history_id,
                    'topic': history_data.get('topic', ''),
                    'created_at': history_data.get('created_at', ''),
                    'total_pages': history_data.get('total_pages', 0),
                    'status': history_data.get('status', 'completed'),
                    'thumbnail': history_data.get('thumbnail', '')
                }
                
                # 检查是否已存在，如果存在则更新
                existing_index = next((i for i, item in enumerate(index) if item['id'] == history_id), None)
                
                if existing_index is not None:
                    index[existing_index] = index_item
                    logger.info(f"更新历史记录索引: {history_id}")
                else:
                    index.insert(0, index_item)  # 新记录插入到开头
                    logger.info(f"添加历史记录索引: {history_id}")
                
                # 保存索引
                if self._save_index(index):
                    logger.info(f"历史记录保存成功: {history_id}")
                    return True
                else:
                    return False
                    
            except Exception as e:
                logger.error(f"保存历史记录失败: {e}", exc_info=True)
                return False
    
    def get(self, history_id: str) -> Optional[Dict[str, Any]]:
        """
        获取历史记录详情
        
        Args:
            history_id: 历史记录ID
            
        Returns:
            历史记录数据
        """
        try:
            detail_file = self.storage_dir / f"{history_id}.json"
            
            if not detail_file.exists():
                logger.warning(f"历史记录不存在: {history_id}")
                return None
            
            with open(detail_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"获取历史记录失败: {e}", exc_info=True)
            return None
    
    def get_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取所有历史记录（完整数据）
        
        Args:
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            历史记录列表（包含完整的pages数据）
        """
        try:
            index = self._load_index()
            
            # 按创建时间倒序排列（最新的在前面）
            index.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            # 分页
            if limit:
                index_items = index[offset:offset + limit]
            else:
                index_items = index[offset:]
            
            # 加载每个记录的完整数据
            full_records = []
            for index_item in index_items:
                history_id = index_item.get('id')
                if history_id:
                    full_data = self.get(history_id)
                    if full_data:
                        full_records.append(full_data)
                    else:
                        # 如果无法加载完整数据，使用索引数据作为后备
                        full_records.append(index_item)
            
            return full_records
                
        except Exception as e:
            logger.error(f"获取历史记录列表失败: {e}", exc_info=True)
            return []
    
    def delete(self, history_id: str) -> bool:
        """
        删除历史记录
        
        Args:
            history_id: 历史记录ID
            
        Returns:
            是否成功
        """
        with self.lock:
            try:
                # 删除详细数据文件
                detail_file = self.storage_dir / f"{history_id}.json"
                if detail_file.exists():
                    detail_file.unlink()
                    logger.info(f"删除历史记录文件: {history_id}")
                
                # 更新索引
                index = self._load_index()
                index = [item for item in index if item['id'] != history_id]
                
                if self._save_index(index):
                    logger.info(f"历史记录删除成功: {history_id}")
                    return True
                else:
                    return False
                    
            except Exception as e:
                logger.error(f"删除历史记录失败: {e}", exc_info=True)
                return False
    
    def exists(self, history_id: str) -> bool:
        """
        检查历史记录是否存在
        
        Args:
            history_id: 历史记录ID
            
        Returns:
            是否存在
        """
        detail_file = self.storage_dir / f"{history_id}.json"
        return detail_file.exists()
    
    def count(self) -> int:
        """
        获取历史记录总数
        
        Returns:
            记录数量
        """
        try:
            index = self._load_index()
            return len(index)
        except Exception as e:
            logger.error(f"获取记录数量失败: {e}", exc_info=True)
            return 0
    
    def search(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索历史记录
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的历史记录列表
        """
        try:
            index = self._load_index()
            keyword_lower = keyword.lower()
            
            # 在topic中搜索
            results = [
                item for item in index
                if keyword_lower in item.get('topic', '').lower()
            ]
            
            return results
            
        except Exception as e:
            logger.error(f"搜索历史记录失败: {e}", exc_info=True)
            return []
    
    def cleanup_old_records(self, max_records: int = 100) -> int:
        """
        清理旧记录（保留最新的N条）
        
        Args:
            max_records: 最大保留数量
            
        Returns:
            删除的记录数量
        """
        with self.lock:
            try:
                index = self._load_index()
                
                if len(index) <= max_records:
                    return 0
                
                # 按创建时间排序
                index.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                
                # 需要删除的记录
                to_delete = index[max_records:]
                deleted_count = 0
                
                for item in to_delete:
                    if self.delete(item['id']):
                        deleted_count += 1
                
                logger.info(f"清理旧记录完成，删除 {deleted_count} 条")
                return deleted_count
                
            except Exception as e:
                logger.error(f"清理旧记录失败: {e}", exc_info=True)
                return 0