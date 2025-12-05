"""
模板管理路由
"""
from flask import Blueprint, request
import logging

from services.template_service import TemplateService
from ..utils.response import success_response, error_response

logger = logging.getLogger(__name__)

template_bp = Blueprint('template', __name__)


@template_bp.route('/templates', methods=['POST'])
def create_template():
    """
    创建模板
    
    请求体:
    {
        "name": "模板名称",
        "category": "分类",
        "structure": {...},
        "parameters": [{...}],
        "type": "system|user",
        "description": "描述",
        "tags": ["标签"],
        "example": {...},
        "preview": "预览图URL",
        "thumbnail": "缩略图URL"
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['name', 'category', 'structure']
        for field in required_fields:
            if field not in data:
                return error_response(f'缺少必填字段: {field}', 400)
        
        service = TemplateService()
        
        # 验证模板数据
        is_valid, error_msg = service.validate_template_data(
            structure=data['structure'],
            parameters=data.get('parameters', [])
        )
        
        if not is_valid:
            return error_response(error_msg, 400)
        
        template_id = service.create_template(
            name=data['name'],
            category=data['category'],
            structure=data['structure'],
            parameters=data.get('parameters', []),
            template_type=data.get('type', 'user'),
            description=data.get('description', ''),
            tags=data.get('tags', []),
            example=data.get('example', {}),
            preview=data.get('preview', ''),
            thumbnail=data.get('thumbnail', '')
        )
        
        if template_id:
            return success_response({'template_id': template_id}, '模板创建成功', 201)
        else:
            return error_response('模板创建失败', 500)
            
    except Exception as e:
        logger.error(f'创建模板异常: {e}', exc_info=True)
        return error_response(str(e), 500)


@template_bp.route('/templates', methods=['GET'])
def get_templates():
    """
    获取模板列表
    
    查询参数:
    - type: 模板类型（system|user）
    - category: 分类
    - tags: 标签（逗号分隔）
    - page: 页码（默认1）
    - page_size: 每页数量（默认20）
    - keyword: 搜索关键词
    """
    try:
        service = TemplateService()
        
        template_type = request.args.get('type')
        category = request.args.get('category')
        tags_str = request.args.get('tags')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        keyword = request.args.get('keyword')
        
        tags = tags_str.split(',') if tags_str else None
        
        if keyword:
            items = service.search_templates(keyword)
            return success_response({
                'items': items,
                'pagination': {
                    'page': 1,
                    'page_size': len(items),
                    'total': len(items),
                    'total_pages': 1,
                    'has_more': False
                }
            })
        
        result = service.get_templates(
            template_type=template_type,
            category=category,
            tags=tags,
            page=page,
            page_size=page_size
        )
        
        return success_response(result)
        
    except Exception as e:
        logger.error(f'获取模板列表异常: {e}', exc_info=True)
        return error_response(str(e), 500)


@template_bp.route('/templates/<template_id>', methods=['GET'])
def get_template(template_id):
    """获取单个模板详情"""
    try:
        service = TemplateService()
        template = service.get_template(template_id)
        
        if not template:
            return error_response('模板不存在', 404)
        
        return success_response(template)
        
    except Exception as e:
        logger.error(f'获取模板详情异常: {e}', exc_info=True)
        return error_response(str(e), 500)


@template_bp.route('/templates/<template_id>', methods=['PUT'])
def update_template(template_id):
    """
    更新模板
    
    请求体:
    {
        "name": "新名称",
        "structure": {...},
        "parameters": [{...}],
        "description": "描述",
        "tags": ["标签"],
        "example": {...},
        "preview": "预览图URL",
        "thumbnail": "缩略图URL"
    }
    """
    try:
        data = request.get_json()
        service = TemplateService()
        
        if 'structure' in data and 'parameters' in data:
            is_valid, error_msg = service.validate_template_data(
                structure=data['structure'],
                parameters=data['parameters']
            )
            
            if not is_valid:
                return error_response(error_msg, 400)
        
        success = service.update_template(
            template_id=template_id,
            name=data.get('name'),
            structure=data.get('structure'),
            parameters=data.get('parameters'),
            tags=data.get('tags'),
            description=data.get('description'),
            example=data.get('example'),
            preview=data.get('preview'),
            thumbnail=data.get('thumbnail')
        )
        
        if success:
            return success_response(message='模板更新成功')
        else:
            return error_response('模板更新失败', 500)
            
    except Exception as e:
        logger.error(f'更新模板异常: {e}', exc_info=True)
        return error_response(str(e), 500)


@template_bp.route('/templates/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """删除模板"""
    try:
        service = TemplateService()
        
        template = service.get_template(template_id)
        if not template:
            return error_response('模板不存在', 404)
        
        if service.delete_template(template_id):
            return success_response(message='模板删除成功')
        else:
            return error_response('模板删除失败', 500)
            
    except Exception as e:
        logger.error(f'删除模板异常: {e}', exc_info=True)
        return error_response(str(e), 500)


@template_bp.route('/templates/<template_id>/use', methods=['POST'])
def use_template(template_id):
    """
    使用模板（填充参数）
    
    请求体:
    {
        "parameters": {
            "param_name1": "value1",
            "param_name2": "value2"
        }
    }
    """
    try:
        data = request.get_json()
        parameters = data.get('parameters', {})
        
        if not parameters:
            return error_response('参数不能为空', 400)
        
        service = TemplateService()
        result = service.use_template(template_id, parameters)
        
        if result:
            return success_response(result, '模板使用成功')
        else:
            return error_response('模板使用失败', 500)
            
    except Exception as e:
        logger.error(f'使用模板异常: {e}', exc_info=True)
        return error_response(str(e), 500)


@template_bp.route('/templates/popular', methods=['GET'])
def get_popular_templates():
    """
    获取热门模板
    
    查询参数:
    - limit: 数量限制（默认10）
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        service = TemplateService()
        templates = service.get_popular_templates(limit)
        
        return success_response(templates)
        
    except Exception as e:
        logger.error(f'获取热门模板异常: {e}', exc_info=True)
        return error_response(str(e), 500)


@template_bp.route('/templates/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    try:
        service = TemplateService()
        categories = service.get_categories()
        return success_response(categories)
        
    except Exception as e:
        logger.error(f'获取分类列表异常: {e}', exc_info=True)
        return error_response(str(e), 500)


@template_bp.route('/templates/tags', methods=['GET'])
def get_tags():
    """获取所有标签"""
    try:
        service = TemplateService()
        tags = service.get_tags()
        return success_response(tags)
        
    except Exception as e:
        logger.error(f'获取标签列表异常: {e}', exc_info=True)
        return error_response(str(e), 500)