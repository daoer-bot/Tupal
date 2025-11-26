"""
历史管理服务
处理历史记录的业务逻辑
"""
import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from storage.history_storage import HistoryStorage

logger = logging.getLogger(__name__)


class HistoryService:
    """历史管理服务类"""
    
    def __init__(self, storage_dir: str = 'storage/history'):
        """
        初始化服务
        
        Args:
            storage_dir: 存储目录
        """
        self.storage = HistoryStorage(storage_dir)
        logger.info("历史管理服务已初始化")
    
    def save_generation(
        self,
        task_id: str,
        topic: str,
        pages: List[Dict[str, Any]],
        reference_image: Optional[str] = None,
        generator_type: str = 'mock',
        status: str = 'completed'
    ) -> Optional[str]:
        """
        保存生成记录
        
        Args:
            task_id: 任务ID
            topic: 主题
            pages: 页面列表（包含图片URL）
            reference_image: 参考图片
            generator_type: 生成器类型
            status: 状态
            
        Returns:
            历史记录ID，失败返回None
        """
        try:
            # 生成历史记录ID（可以使用task_id或生成新ID）
            history_id = task_id if task_id else str(uuid.uuid4())
            
            # 提取缩略图（使用第一页的图片）
            thumbnail = ''
            if pages and len(pages) > 0:
                thumbnail = pages[0].get('image_url', '')
            
            # 构建历史记录数据
            history_data = {
                'id': history_id,
                'task_id': task_id,
                'topic': topic,
                'pages': pages,
                'reference_image': reference_image,
                'generator_type': generator_type,
                'status': status,
                'total_pages': len(pages),
                'thumbnail': thumbnail,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # 保存到存储
            if self.storage.save(history_data):
                logger.info(f"生成记录保存成功: {history_id}")
                return history_id
            else:
                logger.error(f"生成记录保存失败: {history_id}")
                return None
                
        except Exception as e:
            logger.error(f"保存生成记录失败: {e}", exc_info=True)
            return None
    
    def get_history(self, history_id: str) -> Optional[Dict[str, Any]]:
        """
        获取历史记录详情
        
        Args:
            history_id: 历史记录ID
            
        Returns:
            历史记录数据
        """
        try:
            return self.storage.get(history_id)
        except Exception as e:
            logger.error(f"获取历史记录失败: {e}", exc_info=True)
            return None
    
    def get_history_list(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取历史记录列表（分页）
        
        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            包含列表和分页信息的字典
        """
        try:
            offset = (page - 1) * page_size
            
            # 获取列表
            items = self.storage.get_all(limit=page_size, offset=offset)
            
            # 获取总数
            total = self.storage.count()
            
            # 计算总页数
            total_pages = (total + page_size - 1) // page_size
            
            return {
                'items': items,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total': total,
                    'total_pages': total_pages,
                    'has_more': page < total_pages
                }
            }
            
        except Exception as e:
            logger.error(f"获取历史记录列表失败: {e}", exc_info=True)
            return {
                'items': [],
                'pagination': {
                    'page': 1,
                    'page_size': page_size,
                    'total': 0,
                    'total_pages': 0,
                    'has_more': False
                }
            }
    
    def delete_history(self, history_id: str) -> bool:
        """
        删除历史记录
        
        Args:
            history_id: 历史记录ID
            
        Returns:
            是否成功
        """
        try:
            if not self.storage.exists(history_id):
                logger.warning(f"历史记录不存在: {history_id}")
                return False
            
            return self.storage.delete(history_id)
            
        except Exception as e:
            logger.error(f"删除历史记录失败: {e}", exc_info=True)
            return False
    
    def update_history(
        self,
        history_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        更新历史记录
        
        Args:
            history_id: 历史记录ID
            updates: 更新的字段
            
        Returns:
            是否成功
        """
        try:
            # 获取现有记录
            history_data = self.storage.get(history_id)
            
            if not history_data:
                logger.warning(f"历史记录不存在: {history_id}")
                return False
            
            # 更新字段
            history_data.update(updates)
            history_data['updated_at'] = datetime.now().isoformat()
            
            # 保存
            return self.storage.save(history_data)
            
        except Exception as e:
            logger.error(f"更新历史记录失败: {e}", exc_info=True)
            return False
    
    def search_history(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索历史记录
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的历史记录列表
        """
        try:
            return self.storage.search(keyword)
        except Exception as e:
            logger.error(f"搜索历史记录失败: {e}", exc_info=True)
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计数据
        """
        try:
            total = self.storage.count()
            
            # 获取所有记录来计算统计
            all_records = self.storage.get_all()
            
            # 按状态统计
            status_counts = {}
            for record in all_records:
                status = record.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # 总页面数
            total_pages = sum(record.get('total_pages', 0) for record in all_records)
            
            return {
                'total_records': total,
                'total_pages': total_pages,
                'status_counts': status_counts,
                'average_pages': total_pages / total if total > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}", exc_info=True)
            return {
                'total_records': 0,
                'total_pages': 0,
                'status_counts': {},
                'average_pages': 0
            }
    
    def cleanup_old_records(self, max_records: int = 100) -> int:
        """
        清理旧记录
        
        Args:
            max_records: 最大保留数量
            
        Returns:
            删除的记录数量
        """
        try:
            return self.storage.cleanup_old_records(max_records)
        except Exception as e:
            logger.error(f"清理旧记录失败: {e}", exc_info=True)
            return 0
    
    def export_history(self, history_id: str) -> Optional[Dict[str, Any]]:
        """
        导出历史记录（用于下载或分享）
        
        Args:
            history_id: 历史记录ID
            
        Returns:
            导出的数据
        """
        try:
            history_data = self.storage.get(history_id)
            
            if not history_data:
                return None
            
            # 构建导出数据
            export_data = {
                'topic': history_data.get('topic', ''),
                'created_at': history_data.get('created_at', ''),
                'pages': history_data.get('pages', []),
                'total_pages': history_data.get('total_pages', 0)
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"导出历史记录失败: {e}", exc_info=True)
            return None