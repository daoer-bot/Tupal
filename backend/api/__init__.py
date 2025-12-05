"""
API模块
统一导出所有蓝图
"""
from .routes import (
    outline_bp,
    image_bp,
    history_bp,
    trending_bp,
    upload_bp,
    material_bp,
    template_bp
)

__all__ = [
    'outline_bp',
    'image_bp',
    'history_bp',
    'trending_bp',
    'upload_bp',
    'material_bp',
    'template_bp'
]