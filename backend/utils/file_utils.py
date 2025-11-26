"""
文件操作工具
处理文件上传、保存和管理
"""
import os
import uuid
import logging
from pathlib import Path
from typing import Optional, Tuple
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from datetime import datetime

logger = logging.getLogger(__name__)

# 允许的图片文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

# 最大文件大小（10MB）
MAX_FILE_SIZE = 10 * 1024 * 1024


class FileUtils:
    """文件工具类"""
    
    def __init__(self, upload_dir: str = 'uploads'):
        """
        初始化文件工具
        
        Args:
            upload_dir: 上传文件保存目录
        """
        self.upload_dir = Path(upload_dir)
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        """确保上传目录存在"""
        if not self.upload_dir.exists():
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建上传目录: {self.upload_dir}")
        
        # 创建子目录
        subdirs = ['references', 'generated', 'temp']
        for subdir in subdirs:
            subdir_path = self.upload_dir / subdir
            if not subdir_path.exists():
                subdir_path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """
        检查文件扩展名是否允许
        
        Args:
            filename: 文件名
            
        Returns:
            是否允许
        """
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def save_upload_file(
        self,
        file: FileStorage,
        subdir: str = 'references'
    ) -> Tuple[bool, str, str]:
        """
        保存上传的文件
        
        Args:
            file: 上传的文件对象
            subdir: 子目录名称 (references/generated/temp)
            
        Returns:
            (是否成功, 文件路径, 错误信息)
        """
        try:
            # 检查文件是否存在
            if not file or file.filename == '':
                return False, '', '没有选择文件'
            
            # 检查文件扩展名
            if not self.allowed_file(file.filename):
                return False, '', f'不支持的文件类型，仅支持: {", ".join(ALLOWED_EXTENSIONS)}'
            
            # 检查文件大小
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                return False, '', f'文件大小超过限制 ({MAX_FILE_SIZE / 1024 / 1024}MB)'
            
            # 生成安全的文件名
            original_filename = secure_filename(file.filename)
            ext = original_filename.rsplit('.', 1)[1].lower()
            
            # 使用UUID生成唯一文件名
            unique_filename = f"{uuid.uuid4().hex}.{ext}"
            
            # 构建完整路径
            save_dir = self.upload_dir / subdir
            file_path = save_dir / unique_filename
            
            # 保存文件
            file.save(str(file_path))
            
            logger.info(f"文件保存成功: {file_path}")
            
            # 返回相对路径
            relative_path = f"{subdir}/{unique_filename}"
            return True, relative_path, ''
            
        except Exception as e:
            logger.error(f"保存文件失败: {e}", exc_info=True)
            return False, '', str(e)
    
    def delete_file(self, file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径（相对于upload_dir）
            
        Returns:
            是否成功
        """
        try:
            full_path = self.upload_dir / file_path
            
            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                logger.info(f"文件删除成功: {full_path}")
                return True
            else:
                logger.warning(f"文件不存在: {full_path}")
                return False
                
        except Exception as e:
            logger.error(f"删除文件失败: {e}", exc_info=True)
            return False
    
    def get_file_url(self, file_path: str, base_url: str = '') -> str:
        """
        获取文件访问URL
        
        Args:
            file_path: 文件路径
            base_url: 基础URL
            
        Returns:
            完整URL
        """
        if not file_path:
            return ''
        
        # 如果已经是完整URL，直接返回
        if file_path.startswith('http://') or file_path.startswith('https://'):
            return file_path
        
        # 构建URL
        if base_url:
            return f"{base_url.rstrip('/')}/uploads/{file_path}"
        else:
            return f"/uploads/{file_path}"
    
    def file_exists(self, file_path: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否存在
        """
        full_path = self.upload_dir / file_path
        return full_path.exists() and full_path.is_file()
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        try:
            full_path = self.upload_dir / file_path
            
            if not full_path.exists():
                return None
            
            stat = full_path.stat()
            
            return {
                'path': file_path,
                'size': stat.st_size,
                'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取文件信息失败: {e}", exc_info=True)
            return None
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        清理临时文件
        
        Args:
            max_age_hours: 最大保留时间（小时）
            
        Returns:
            删除的文件数量
        """
        try:
            temp_dir = self.upload_dir / 'temp'
            if not temp_dir.exists():
                return 0
            
            deleted_count = 0
            current_time = datetime.now().timestamp()
            max_age_seconds = max_age_hours * 3600
            
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"清理临时文件: {file_path}")
            
            logger.info(f"临时文件清理完成，删除 {deleted_count} 个文件")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}", exc_info=True)
            return 0