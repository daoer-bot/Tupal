"""
文件操作工具
处理文件上传、保存和管理
"""
import os
import uuid
import logging
import base64
import requests
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
    
    def download_and_save_image(
        self,
        image_url: str,
        subdir: str = 'generated',
        timeout: int = 60
    ) -> Tuple[bool, str, str]:
        """
        从 URL 下载图片并保存到本地
        
        支持两种格式：
        1. HTTP/HTTPS URL - 从网络下载
        2. Base64 Data URL - 直接解码保存
        
        Args:
            image_url: 图片 URL（HTTP URL 或 base64 Data URL）
            subdir: 子目录名称 (references/generated/temp)
            timeout: 下载超时时间（秒）
            
        Returns:
            (是否成功, 本地文件路径, 错误信息)
        """
        try:
            # 处理 base64 Data URL
            if image_url.startswith('data:image'):
                return self._save_base64_image(image_url, subdir)
            
            # 处理 HTTP/HTTPS URL
            if image_url.startswith(('http://', 'https://')):
                return self._download_http_image(image_url, subdir, timeout)
            
            # 如果已经是本地路径，直接返回
            if self.file_exists(image_url):
                return True, image_url, ''
            
            return False, '', f'不支持的图片 URL 格式: {image_url[:100]}...'
            
        except Exception as e:
            logger.error(f"下载保存图片失败: {e}", exc_info=True)
            return False, '', str(e)
    
    def _save_base64_image(
        self,
        data_url: str,
        subdir: str
    ) -> Tuple[bool, str, str]:
        """
        保存 base64 编码的图片
        
        Args:
            data_url: base64 Data URL (data:image/png;base64,...)
            subdir: 子目录
            
        Returns:
            (是否成功, 本地文件路径, 错误信息)
        """
        try:
            # 解析 Data URL
            # 格式: data:image/png;base64,iVBORw0KGgo...
            header, base64_data = data_url.split(',', 1)
            
            # 提取 MIME 类型
            mime_type = header.split(':')[1].split(';')[0]
            
            # 根据 MIME 类型确定扩展名
            ext_map = {
                'image/png': 'png',
                'image/jpeg': 'jpg',
                'image/jpg': 'jpg',
                'image/gif': 'gif',
                'image/webp': 'webp',
                'image/bmp': 'bmp'
            }
            ext = ext_map.get(mime_type, 'png')
            
            # 解码 base64
            image_data = base64.b64decode(base64_data)
            
            # 生成唯一文件名
            unique_filename = f"{uuid.uuid4().hex}.{ext}"
            
            # 构建完整路径
            save_dir = self.upload_dir / subdir
            file_path = save_dir / unique_filename
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"Base64 图片保存成功: {file_path}")
            
            # 返回相对路径
            relative_path = f"{subdir}/{unique_filename}"
            return True, relative_path, ''
            
        except Exception as e:
            logger.error(f"保存 base64 图片失败: {e}", exc_info=True)
            return False, '', str(e)
    
    def _download_http_image(
        self,
        url: str,
        subdir: str,
        timeout: int
    ) -> Tuple[bool, str, str]:
        """
        从 HTTP URL 下载图片
        
        Args:
            url: HTTP/HTTPS URL
            subdir: 子目录
            timeout: 超时时间
            
        Returns:
            (是否成功, 本地文件路径, 错误信息)
        """
        try:
            # 发送请求下载图片
            response = requests.get(
                url,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                },
                stream=True
            )
            response.raise_for_status()
            
            # 从 Content-Type 或 URL 确定扩展名
            content_type = response.headers.get('Content-Type', '')
            ext = self._get_extension_from_content_type(content_type)
            
            if not ext:
                # 尝试从 URL 获取扩展名
                ext = self._get_extension_from_url(url)
            
            if not ext:
                ext = 'png'  # 默认扩展名
            
            # 生成唯一文件名
            unique_filename = f"{uuid.uuid4().hex}.{ext}"
            
            # 构建完整路径
            save_dir = self.upload_dir / subdir
            file_path = save_dir / unique_filename
            
            # 保存文件
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"HTTP 图片下载保存成功: {file_path}")
            
            # 返回相对路径
            relative_path = f"{subdir}/{unique_filename}"
            return True, relative_path, ''
            
        except requests.exceptions.Timeout:
            return False, '', '下载图片超时，请稍后重试'
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else 0
            if status_code == 403:
                return False, '', '图片链接已过期或无权访问'
            elif status_code == 404:
                return False, '', '图片不存在'
            else:
                return False, '', f'下载图片失败 (HTTP {status_code})'
        except Exception as e:
            logger.error(f"下载 HTTP 图片失败: {e}", exc_info=True)
            return False, '', str(e)
    
    @staticmethod
    def _get_extension_from_content_type(content_type: str) -> Optional[str]:
        """从 Content-Type 获取文件扩展名"""
        type_map = {
            'image/png': 'png',
            'image/jpeg': 'jpg',
            'image/jpg': 'jpg',
            'image/gif': 'gif',
            'image/webp': 'webp',
            'image/bmp': 'bmp'
        }
        
        for mime, ext in type_map.items():
            if mime in content_type.lower():
                return ext
        return None
    
    @staticmethod
    def _get_extension_from_url(url: str) -> Optional[str]:
        """从 URL 获取文件扩展名"""
        # 移除查询参数
        path = url.split('?')[0]
        
        # 获取文件名部分
        filename = path.split('/')[-1]
        
        # 检查是否有扩展名
        if '.' in filename:
            ext = filename.rsplit('.', 1)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                return ext
        
        return None