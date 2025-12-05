"""
模板服务层
处理模板相关的业务逻辑
"""
import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.template import Template, TemplateType, TemplateParameter, create_template
from storage.template_storage import TemplateStorage

logger = logging.getLogger(__name__)


class TemplateService:
    """模板服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.storage = TemplateStorage()
    
    def create_template(
        self,
        name: str,
        category: str,
        structure: Dict[str, Any],
        parameters: List[Dict[str, Any]] = None,
        template_type: str = "user",
        **kwargs
    ) -> Optional[str]:
        """
        创建模板
        
        Args:
            name: 模板名称
            category: 分类
            structure: 模板结构
            parameters: 参数定义列表
            template_type: 模板类型
            **kwargs: 其他字段
            
        Returns:
            模板ID，失败返回None
        """
        try:
            tpl_type = TemplateType(template_type)
            
            # 转换参数定义
            param_objects = []
            if parameters:
                for p in parameters:
                    param_objects.append(TemplateParameter(
                        name=p.get('name', ''),
                        label=p.get('label', ''),
                        type=p.get('type', 'text'),
                        required=p.get('required', True),
                        default=p.get('default'),
                        placeholder=p.get('placeholder', '')
                    ))
            
            template = create_template(
                name=name,
                category=category,
                structure=structure,
                template_type=tpl_type,
                parameters=param_objects,
                **kwargs
            )
            
            if self.storage.save(template):
                logger.info(f"模板创建成功: {template.id}")
                return template.id
            else:
                logger.error("模板保存失败")
                return None
                
        except ValueError as e:
            logger.error(f"无效的模板类型: {e}")
            return None
        except Exception as e:
            logger.error(f"创建模板失败: {e}", exc_info=True)
            return None
    
    def update_template(
        self,
        template_id: str,
        name: Optional[str] = None,
        structure: Optional[Dict[str, Any]] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> bool:
        """更新模板"""
        try:
            template = self.storage.get(template_id)
            if not template:
                logger.error(f"模板不存在: {template_id}")
                return False
            
            if name is not None:
                template.name = name
            if structure is not None:
                template.structure = structure
            if parameters is not None:
                template.parameters = [
                    TemplateParameter(**p) for p in parameters
                ]
            if tags is not None:
                template.tags = tags
            if description is not None:
                template.description = description
            
            # 更新其他字段
            for key, value in kwargs.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            template.updated_at = datetime.now().isoformat()
            
            if self.storage.save(template):
                logger.info(f"模板更新成功: {template_id}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"更新模板失败: {e}", exc_info=True)
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """删除模板"""
        try:
            return self.storage.delete(template_id)
        except Exception as e:
            logger.error(f"删除模板失败: {e}", exc_info=True)
            return False
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """获取模板详情"""
        try:
            template = self.storage.get(template_id)
            if template:
                return template.to_dict()
            return None
        except Exception as e:
            logger.error(f"获取模板失败: {e}", exc_info=True)
            return None
    
    def get_templates(
        self,
        template_type: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取模板列表（分页）"""
        try:
            tpl_type = TemplateType(template_type) if template_type else None
            
            offset = (page - 1) * page_size
            
            templates = self.storage.get_all(
                template_type=tpl_type,
                category=category,
                tags=tags,
                limit=page_size,
                offset=offset
            )
            
            total = self.storage.count(
                template_type=tpl_type,
                category=category
            )
            
            items = [template.to_dict() for template in templates]
            
            return {
                'items': items,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total': total,
                    'total_pages': (total + page_size - 1) // page_size,
                    'has_more': offset + len(items) < total
                }
            }
            
        except Exception as e:
            logger.error(f"获取模板列表失败: {e}", exc_info=True)
            return {
                'items': [],
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total': 0,
                    'total_pages': 0,
                    'has_more': False
                }
            }
    
    def search_templates(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索模板"""
        try:
            templates = self.storage.search(keyword)
            return [template.to_dict() for template in templates]
        except Exception as e:
            logger.error(f"搜索模板失败: {e}", exc_info=True)
            return []
    
    def get_popular_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门模板"""
        try:
            templates = self.storage.get_popular(limit)
            return [template.to_dict() for template in templates]
        except Exception as e:
            logger.error(f"获取热门模板失败: {e}", exc_info=True)
            return []
    
    def use_template(
        self,
        template_id: str,
        parameters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        使用模板（填充参数）
        
        Args:
            template_id: 模板ID
            parameters: 参数值字典 {param_name: value}
            
        Returns:
            填充后的内容
        """
        try:
            template = self.storage.get(template_id)
            if not template:
                logger.error(f"模板不存在: {template_id}")
                return None
            
            # 验证必填参数
            for param in template.parameters:
                if param.required and param.name not in parameters:
                    logger.error(f"缺少必填参数: {param.name}")
                    return None
            
            # 填充参数
            filled_structure = self._fill_parameters(
                template.structure,
                parameters
            )
            
            # 增加使用次数
            self.storage.increment_usage_count(template_id)
            
            logger.info(f"模板使用成功: {template_id}")
            
            return {
                'template_id': template_id,
                'template_name': template.name,
                'filled_structure': filled_structure,
                'parameters_used': parameters
            }
            
        except Exception as e:
            logger.error(f"使用模板失败: {e}", exc_info=True)
            return None
    
    def _fill_parameters(
        self,
        structure: Any,
        parameters: Dict[str, Any]
    ) -> Any:
        """
        递归填充参数占位符
        
        占位符格式: {{param_name}}
        """
        if isinstance(structure, str):
            # 替换字符串中的占位符
            for param_name, param_value in parameters.items():
                placeholder = f"{{{{{param_name}}}}}"
                structure = structure.replace(placeholder, str(param_value))
            return structure
        
        elif isinstance(structure, dict):
            # 递归处理字典
            return {
                key: self._fill_parameters(value, parameters)
                for key, value in structure.items()
            }
        
        elif isinstance(structure, list):
            # 递归处理列表
            return [
                self._fill_parameters(item, parameters)
                for item in structure
            ]
        
        else:
            # 其他类型直接返回
            return structure
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        try:
            return self.storage.get_categories()
        except Exception as e:
            logger.error(f"获取分类列表失败: {e}", exc_info=True)
            return []
    
    def get_tags(self) -> List[str]:
        """获取所有标签"""
        try:
            return self.storage.get_tags()
        except Exception as e:
            logger.error(f"获取标签列表失败: {e}", exc_info=True)
            return []
    
    def validate_template_data(
        self,
        structure: Dict[str, Any],
        parameters: List[Dict[str, Any]]
    ) -> tuple[bool, Optional[str]]:
        """验证模板数据"""
        try:
            if not structure:
                return False, "模板结构不能为空"
            
            # 验证参数定义
            param_names = set()
            for param in parameters:
                if not param.get('name'):
                    return False, "参数名称不能为空"
                if param['name'] in param_names:
                    return False, f"参数名称重复: {param['name']}"
                param_names.add(param['name'])
            
            return True, None
            
        except Exception as e:
            return False, str(e)