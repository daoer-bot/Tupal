"""
进度管理服务
管理图片生成任务的实时进度
"""
import logging
import threading
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'


class ProgressService:
    """进度管理服务类 - 线程安全的单例模式"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化服务"""
        if not hasattr(self, '_initialized'):
            self._tasks: Dict[str, Dict[str, Any]] = {}
            self._tasks_lock = threading.Lock()
            self._initialized = True
            self._max_tasks = 1000  # 最大任务数限制
            self._cleanup_hours = 24  # 自动清理24小时前的完成任务
            
            # 启动自动清理线程
            self._start_cleanup_thread()
            logger.info("进度管理服务已初始化")
    
    def _start_cleanup_thread(self):
        """启动自动清理线程"""
        def cleanup_worker():
            import time
            while True:
                try:
                    # 每小时执行一次清理
                    time.sleep(3600)
                    cleared = self.clear_completed_tasks(self._cleanup_hours)
                    if cleared > 0:
                        logger.info(f"自动清理了 {cleared} 个过期任务")
                    
                    # 检查任务数是否超限
                    with self._tasks_lock:
                        if len(self._tasks) > self._max_tasks:
                            # 超限时，删除最旧的已完成任务
                            completed_tasks = [
                                (task_id, task['updated_at'])
                                for task_id, task in self._tasks.items()
                                if task['status'] in ['completed', 'failed']
                            ]
                            completed_tasks.sort(key=lambda x: x[1])
                            
                            # 删除最旧的任务直到低于限制
                            to_remove = len(self._tasks) - int(self._max_tasks * 0.8)
                            for task_id, _ in completed_tasks[:to_remove]:
                                del self._tasks[task_id]
                            
                            if to_remove > 0:
                                logger.warning(f"任务数超限，清理了 {to_remove} 个最旧的已完成任务")
                
                except Exception as e:
                    logger.error(f"自动清理任务异常: {e}", exc_info=True)
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("自动清理线程已启动")
    
    def create_task(
        self,
        task_id: str,
        total_pages: int,
        topic: str = ''
    ) -> Dict[str, Any]:
        """
        创建新任务
        
        Args:
            task_id: 任务ID
            total_pages: 总页数
            topic: 主题
            
        Returns:
            任务信息
        """
        with self._tasks_lock:
            task_data = {
                'task_id': task_id,
                'status': TaskStatus.PENDING.value,
                'topic': topic,
                'total_pages': total_pages,
                'completed_pages': 0,
                'current_page': 0,
                'progress': 0,
                'images': [],
                'failed_pages': [],  # 新增：失败的页面列表
                'message': '任务已创建，等待开始...',
                'error': None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            self._tasks[task_id] = task_data
            logger.info(f"任务已创建: {task_id}, 总页数: {total_pages}")
            
            return task_data
    
    def start_task(self, task_id: str) -> bool:
        """
        开始任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功
        """
        with self._tasks_lock:
            if task_id not in self._tasks:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            self._tasks[task_id]['status'] = TaskStatus.RUNNING.value
            self._tasks[task_id]['message'] = '开始生成图片...'
            self._tasks[task_id]['updated_at'] = datetime.now().isoformat()
            
            logger.info(f"任务已启动: {task_id}")
            return True
    
    def update_progress(
        self,
        task_id: str,
        current_page: int,
        image_url: Optional[str] = None,
        message: Optional[str] = None
    ) -> bool:
        """
        更新任务进度
        
        Args:
            task_id: 任务ID
            current_page: 当前页码
            image_url: 生成的图片URL
            message: 进度消息
            
        Returns:
            是否成功
        """
        with self._tasks_lock:
            if task_id not in self._tasks:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            task = self._tasks[task_id]
            task['current_page'] = current_page
            task['completed_pages'] = current_page
            task['progress'] = int((current_page / task['total_pages']) * 100)
            task['updated_at'] = datetime.now().isoformat()
            
            if image_url:
                task['images'].append({
                    'page_number': current_page,
                    'url': image_url,
                    'created_at': datetime.now().isoformat()
                })
            
            if message:
                task['message'] = message
            else:
                task['message'] = f'正在生成第 {current_page}/{task["total_pages"]} 页...'
            
            logger.info(f"任务进度更新: {task_id}, 进度: {task['progress']}%")
            return True
    
    def record_failed_page(
        self,
        task_id: str,
        page_number: int,
        error: str
    ) -> bool:
        """
        记录失败的页面
        
        Args:
            task_id: 任务ID
            page_number: 页码
            error: 错误信息
            
        Returns:
            是否成功
        """
        with self._tasks_lock:
            if task_id not in self._tasks:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            task = self._tasks[task_id]
            
            # 添加失败记录
            failed_info = {
                'page_number': page_number,
                'error': error,
                'failed_at': datetime.now().isoformat()
            }
            task['failed_pages'].append(failed_info)
            task['updated_at'] = datetime.now().isoformat()
            
            logger.warning(f"记录失败页面: {task_id}, 页码: {page_number}, 错误: {error}")
            return True
    
    def complete_task(
        self,
        task_id: str,
        message: str = '所有图片生成完成！'
    ) -> bool:
        """
        完成任务
        
        Args:
            task_id: 任务ID
            message: 完成消息
            
        Returns:
            是否成功
        """
        with self._tasks_lock:
            if task_id not in self._tasks:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            task = self._tasks[task_id]
            task['status'] = TaskStatus.COMPLETED.value
            task['progress'] = 100
            task['message'] = message
            task['updated_at'] = datetime.now().isoformat()
            
            logger.info(f"任务已完成: {task_id}")
            return True
    
    def fail_task(
        self,
        task_id: str,
        error: str
    ) -> bool:
        """
        标记任务失败
        
        Args:
            task_id: 任务ID
            error: 错误信息
            
        Returns:
            是否成功
        """
        with self._tasks_lock:
            if task_id not in self._tasks:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            task = self._tasks[task_id]
            task['status'] = TaskStatus.FAILED.value
            task['error'] = error
            task['message'] = f'生成失败: {error}'
            task['updated_at'] = datetime.now().isoformat()
            
            logger.error(f"任务失败: {task_id}, 错误: {error}")
            return True
    
    def get_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务进度
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务信息，如果不存在则返回None
        """
        with self._tasks_lock:
            if task_id not in self._tasks:
                return None
            
            # 返回任务数据的副本
            return dict(self._tasks[task_id])
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有任务
        
        Returns:
            所有任务的字典
        """
        with self._tasks_lock:
            # 返回所有任务的副本
            return {task_id: dict(task_data) 
                    for task_id, task_data in self._tasks.items()}
    
    def delete_task(self, task_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功
        """
        with self._tasks_lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                logger.info(f"任务已删除: {task_id}")
                return True
            return False
    
    def task_exists(self, task_id: str) -> bool:
        """
        检查任务是否存在
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否存在
        """
        with self._tasks_lock:
            return task_id in self._tasks
    
    def is_task_running(self, task_id: str) -> bool:
        """
        检查任务是否正在运行
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否正在运行
        """
        with self._tasks_lock:
            if task_id not in self._tasks:
                return False
            return self._tasks[task_id]['status'] == TaskStatus.RUNNING.value
    
    def is_task_completed(self, task_id: str) -> bool:
        """
        检查任务是否已完成
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否已完成
        """
        with self._tasks_lock:
            if task_id not in self._tasks:
                return False
            status = self._tasks[task_id]['status']
            return status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]
    
    def clear_completed_tasks(self, max_age_hours: int = 24) -> int:
        """
        清理完成的旧任务
        
        Args:
            max_age_hours: 最大保留时间（小时）
            
        Returns:
            清理的任务数量
        """
        from datetime import timedelta
        
        cleared_count = 0
        current_time = datetime.now()
        
        with self._tasks_lock:
            tasks_to_remove = []
            
            for task_id, task_data in self._tasks.items():
                if not self.is_task_completed(task_id):
                    continue
                
                updated_at = datetime.fromisoformat(task_data['updated_at'])
                age = current_time - updated_at
                
                if age > timedelta(hours=max_age_hours):
                    tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                del self._tasks[task_id]
                cleared_count += 1
            
            if cleared_count > 0:
                logger.info(f"清理了 {cleared_count} 个过期任务")
        
        return cleared_count