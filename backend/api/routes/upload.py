"""
文件上传路由
"""
from flask import Blueprint, request
import logging

from utils.file_utils import FileUtils
from ..utils.response import success_response, error_response

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/upload-reference', methods=['POST'])
def upload_reference():
    """上传参考图片"""
    try:
        if 'file' not in request.files:
            return error_response('没有上传文件', 400)
        
        file = request.files['file']
        
        if file.filename == '':
            return error_response('文件名为空', 400)
        
        file_utils = FileUtils()
        
        success, file_path, error_msg = file_utils.save_upload_file(
            file=file,
            subdir='references'
        )
        
        if not success:
            return error_response(error_msg, 400)
        
        file_url = file_utils.get_file_url(file_path)
        
        return success_response({
            'file_url': file_url,
            'file_path': file_path
        }, '上传成功')
        
    except Exception as e:
        logger.error(f'Error uploading file: {e}', exc_info=True)
        return error_response(str(e), 500)