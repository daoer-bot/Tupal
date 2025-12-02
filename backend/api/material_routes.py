"""
素材管理API路由
提供素材的CRUD操作接口
"""
from flask import Blueprint, request, jsonify
import logging

from services.material_service import MaterialService

logger = logging.getLogger(__name__)

# 创建蓝图
material_bp = Blueprint('material', __name__)


@material_bp.route('/materials', methods=['POST'])
def create_material():
    """
    创建素材
    
    请求体:
    {
        "name": "素材名称",
        "type": "text|image|style|product",
        "category": "产品介绍|产品图片|...",
        "content": {...},
        "tags": ["标签1", "标签2"],
        "description": "描述"
    }
    """
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'type', 'category', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必填字段: {field}'
                }), 400
        
        service = MaterialService()
        
        # 验证素材数据
        is_valid, error_msg = service.validate_material_data(
            material_type=data['type'],
            content=data['content']
        )
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # 创建素材
        material_id = service.create_material(
            name=data['name'],
            material_type=data['type'],
            category=data['category'],
            content=data['content'],
            tags=data.get('tags', []),
            description=data.get('description', '')
        )
        
        if material_id:
            return jsonify({
                'success': True,
                'message': '素材创建成功',
                'material_id': material_id
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': '素材创建失败'
            }), 500
            
    except Exception as e:
        logger.error(f'创建素材异常: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@material_bp.route('/materials', methods=['GET'])
def get_materials():
    """
    获取素材列表
    
    查询参数:
    - type: 素材类型（可选）
    - category: 素材分类（可选）
    - tags: 标签（可选，逗号分隔）
    - page: 页码（默认1）
    - page_size: 每页数量（默认20）
    - keyword: 搜索关键词（可选）
    """
    try:
        service = MaterialService()
        
        # 获取查询参数
        material_type = request.args.get('type')
        category = request.args.get('category')
        tags_str = request.args.get('tags')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        keyword = request.args.get('keyword')
        
        # 处理标签
        tags = tags_str.split(',') if tags_str else None
        
        # 如果有搜索关键词，执行搜索
        if keyword:
            items = service.search_materials(keyword)
            return jsonify({
                'success': True,
                'data': {
                    'items': items,
                    'pagination': {
                        'page': 1,
                        'page_size': len(items),
                        'total': len(items),
                        'total_pages': 1,
                        'has_more': False
                    }
                }
            })
        
        # 获取分页列表
        result = service.get_materials(
            material_type=material_type,
            category=category,
            tags=tags,
            page=page,
            page_size=page_size
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f'获取素材列表异常: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@material_bp.route('/materials/<material_id>', methods=['GET'])
def get_material(material_id):
    """
    获取单个素材详情
    """
    try:
        service = MaterialService()
        material = service.get_material(material_id)
        
        if not material:
            return jsonify({
                'success': False,
                'error': '素材不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': material
        })
        
    except Exception as e:
        logger.error(f'获取素材详情异常: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@material_bp.route('/materials/<material_id>', methods=['PUT'])
def update_material(material_id):
    """
    更新素材
    
    请求体:
    {
        "name": "新名称（可选）",
        "content": {...}（可选）,
        "tags": ["标签"]（可选）,
        "description": "描述"（可选）,
        "category": "分类"（可选）
    }
    """
    try:
        data = request.get_json()
        service = MaterialService()
        
        # 如果更新了content，需要验证
        if 'content' in data:
            # 先获取现有素材以获取类型
            existing = service.get_material(material_id)
            if not existing:
                return jsonify({
                    'success': False,
                    'error': '素材不存在'
                }), 404
            
            is_valid, error_msg = service.validate_material_data(
                material_type=existing['type'],
                content=data['content']
            )
            
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 400
        
        # 更新素材
        success = service.update_material(
            material_id=material_id,
            name=data.get('name'),
            content=data.get('content'),
            tags=data.get('tags'),
            description=data.get('description'),
            category=data.get('category')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '素材更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '素材更新失败'
            }), 500
            
    except Exception as e:
        logger.error(f'更新素材异常: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@material_bp.route('/materials/<material_id>', methods=['DELETE'])
def delete_material(material_id):
    """
    删除素材
    """
    try:
        service = MaterialService()
        
        # 先检查素材是否存在
        material = service.get_material(material_id)
        if not material:
            return jsonify({
                'success': False,
                'error': '素材不存在'
            }), 404
        
        # 执行删除
        if service.delete_material(material_id):
            return jsonify({
                'success': True,
                'message': '素材删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '素材删除失败'
            }), 500
            
    except Exception as e:
        logger.error(f'删除素材异常: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@material_bp.route('/materials/batch', methods=['POST'])
def get_materials_batch():
    """
    批量获取素材（用于引用处理）
    
    请求体:
    {
        "material_ids": ["id1", "id2", ...]
    }
    """
    try:
        data = request.get_json()
        material_ids = data.get('material_ids', [])
        
        if not material_ids:
            return jsonify({
                'success': False,
                'error': '素材ID列表不能为空'
            }), 400
        
        service = MaterialService()
        materials = service.get_materials_by_ids(material_ids)
        
        return jsonify({
            'success': True,
            'data': materials
        })
        
    except Exception as e:
        logger.error(f'批量获取素材异常: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@material_bp.route('/materials/categories', methods=['GET'])
def get_categories():
    """
    获取所有分类
    """
    try:
        service = MaterialService()
        categories = service.get_categories()
        
        return jsonify({
            'success': True,
            'data': categories
        })
        
    except Exception as e:
        logger.error(f'获取分类列表异常: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@material_bp.route('/materials/tags', methods=['GET'])
def get_tags():
    """
    获取所有标签
    """
    try:
        service = MaterialService()
        tags = service.get_tags()
        
        return jsonify({
            'success': True,
            'data': tags
        })
        
    except Exception as e:
        logger.error(f'获取标签列表异常: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@material_bp.route('/materials/process-references', methods=['POST'])
def process_references():
    """
    处理素材引用
    
    请求体:
    {
        "material_ids": ["id1", "id2", ...],
        "base_prompt": "基础提示词"
    }
    
    返回:
    {
        "enhanced_prompt": "增强后的提示词",
        "reference_images": ["url1", "url2", ...],
        "style_params": {...},
        "materials_used": [...]
    }
    """
    try:
        data = request.get_json()
        material_ids = data.get('material_ids', [])
        base_prompt = data.get('base_prompt', '')
        
        if not material_ids:
            return jsonify({
                'success': False,
                'error': '素材ID列表不能为空'
            }), 400
        
        service = MaterialService()
        result = service.process_material_references(
            material_ids=material_ids,
            base_prompt=base_prompt
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f'处理素材引用异常: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500