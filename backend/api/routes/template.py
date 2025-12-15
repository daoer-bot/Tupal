"""
模板管理路由
"""
from flask import Blueprint, request
import logging
import uuid

from services.template_service import TemplateService
from services.outline_service import OutlineService
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
    使用模板创建大纲

    请求体:
    {
        "topic": "创作主题",
        "parameters": {
            "param_name1": "value1",
            "param_name2": "value2"
        }
    }
    
    如果提供了 topic，会基于模板结构和主题生成大纲
    如果提供了 parameters，会直接填充模板参数
    """
    try:
        data = request.get_json()
        topic = data.get('topic')
        parameters = data.get('parameters', {})

        service = TemplateService()
        
        # 获取模板
        template = service.get_template(template_id)
        if not template:
            return error_response('模板不存在', 404)

        # 如果提供了主题，基于模板生成大纲
        if topic:
            task_id = f"task_{uuid.uuid4().hex[:12]}"
            
            # 从模板结构中提取页面信息
            structure = template.get('structure', {})
            template_pages = structure.get('pages', [])
            
            # 如果模板有预定义的页面结构，使用它
            if template_pages:
                pages = []
                for i, page in enumerate(template_pages):
                    # 替换主题占位符
                    title = page.get('title', f'第{i+1}页').replace('{{topic}}', topic)
                    description = page.get('description', '').replace('{{topic}}', topic)
                    content = page.get('xiaohongshu_content', '').replace('{{topic}}', topic)
                    
                    pages.append({
                        'page_number': i + 1,
                        'title': title,
                        'description': description,
                        'xiaohongshu_content': content
                    })
            else:
                # 如果模板没有预定义页面，使用AI生成
                try:
                    outline_service = OutlineService()
                    outline_result = outline_service.generate(topic=topic)
                    
                    if outline_result.get('success') and 'pages' in outline_result:
                        pages = outline_result['pages']
                    else:
                        # 默认生成4页
                        pages = _generate_default_pages(topic, template)
                except Exception as e:
                    logger.warning(f'使用AI生成大纲失败，使用默认结构: {e}')
                    pages = _generate_default_pages(topic, template)
            
            # 增加模板使用次数
            service.storage.increment_usage_count(template_id)
            
            return success_response({
                'task_id': task_id,
                'topic': topic,
                'template_id': template_id,
                'template_name': template.get('name', ''),
                'pages': pages
            }, '模板使用成功')
        
        # 如果提供了参数，使用传统的参数填充方式
        elif parameters:
            result = service.use_template(template_id, parameters)

            if result:
                return success_response(result, '模板使用成功')
            else:
                return error_response('模板使用失败', 500)
        
        else:
            return error_response('请提供 topic 或 parameters 参数', 400)

    except Exception as e:
        logger.error(f'使用模板异常: {e}', exc_info=True)
        return error_response(str(e), 500)


def _generate_default_pages(topic: str, template: dict) -> list:
    """
    生成默认页面结构
    
    Args:
        topic: 主题
        template: 模板信息
        
    Returns:
        页面列表
    """
    category = template.get('category', '')
    
    # 根据模板分类生成不同的默认结构
    if category in ['穿搭', 'OOTD', '时尚']:
        return [
            {'page_number': 1, 'title': f'{topic} - 整体造型', 'description': '展示完整穿搭效果', 'xiaohongshu_content': ''},
            {'page_number': 2, 'title': f'{topic} - 单品详情', 'description': '介绍各个单品', 'xiaohongshu_content': ''},
            {'page_number': 3, 'title': f'{topic} - 搭配技巧', 'description': '分享搭配心得', 'xiaohongshu_content': ''},
            {'page_number': 4, 'title': f'{topic} - 购买链接', 'description': '提供购买信息', 'xiaohongshu_content': ''},
        ]
    elif category in ['美食', '探店', '餐厅']:
        return [
            {'page_number': 1, 'title': f'{topic} - 店铺环境', 'description': '展示店铺氛围', 'xiaohongshu_content': ''},
            {'page_number': 2, 'title': f'{topic} - 招牌菜品', 'description': '介绍必点美食', 'xiaohongshu_content': ''},
            {'page_number': 3, 'title': f'{topic} - 口味评价', 'description': '分享真实体验', 'xiaohongshu_content': ''},
            {'page_number': 4, 'title': f'{topic} - 店铺信息', 'description': '地址和营业时间', 'xiaohongshu_content': ''},
        ]
    elif category in ['旅行', '旅游', '攻略']:
        return [
            {'page_number': 1, 'title': f'{topic} - 目的地介绍', 'description': '景点概览', 'xiaohongshu_content': ''},
            {'page_number': 2, 'title': f'{topic} - 行程安排', 'description': '详细行程规划', 'xiaohongshu_content': ''},
            {'page_number': 3, 'title': f'{topic} - 必打卡景点', 'description': '推荐景点', 'xiaohongshu_content': ''},
            {'page_number': 4, 'title': f'{topic} - 实用攻略', 'description': '交通住宿美食', 'xiaohongshu_content': ''},
        ]
    elif category in ['好物', '种草', '推荐']:
        return [
            {'page_number': 1, 'title': f'{topic} - 产品展示', 'description': '产品外观', 'xiaohongshu_content': ''},
            {'page_number': 2, 'title': f'{topic} - 使用体验', 'description': '真实使用感受', 'xiaohongshu_content': ''},
            {'page_number': 3, 'title': f'{topic} - 优缺点分析', 'description': '客观评价', 'xiaohongshu_content': ''},
            {'page_number': 4, 'title': f'{topic} - 购买建议', 'description': '适合人群和购买渠道', 'xiaohongshu_content': ''},
        ]
    else:
        # 通用默认结构
        return [
            {'page_number': 1, 'title': f'{topic} - 开篇', 'description': '引入主题，吸引注意', 'xiaohongshu_content': ''},
            {'page_number': 2, 'title': f'{topic} - 详情', 'description': '详细介绍内容', 'xiaohongshu_content': ''},
            {'page_number': 3, 'title': f'{topic} - 亮点', 'description': '特色展示', 'xiaohongshu_content': ''},
            {'page_number': 4, 'title': f'{topic} - 总结', 'description': '结尾总结，引导互动', 'xiaohongshu_content': ''},
        ]


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