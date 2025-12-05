"""
模板数据模型
支持系统模板和用户自定义模板
"""
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict


class TemplateType(str, Enum):
    """模板类型"""
    SYSTEM = "system"  # 系统预置模板
    USER = "user"      # 用户创建模板


@dataclass
class TemplateParameter:
    """模板参数定义"""
    name: str              # 参数名（如 "product_name"）
    label: str             # 显示标签（如 "产品名称"）
    type: str              # 类型（text/image/number）
    required: bool = True  # 是否必填
    default: Any = None    # 默认值
    placeholder: str = ""  # 占位符提示
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateParameter':
        return cls(**data)


@dataclass
class Template:
    """模板实体"""
    
    # 核心字段
    id: str
    name: str
    type: TemplateType
    category: str
    description: str = ""
    
    # 模板内容
    structure: Dict[str, Any] = field(default_factory=dict)  # 模板结构
    parameters: List[TemplateParameter] = field(default_factory=list)  # 参数定义
    
    # 示例和预览
    example: Dict[str, Any] = field(default_factory=dict)  # 使用示例
    preview: str = ""       # 预览图URL
    thumbnail: str = ""     # 缩略图URL
    
    # 管理字段
    tags: List[str] = field(default_factory=list)
    usage_count: int = 0
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        """初始化处理"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        
        if isinstance(self.type, str):
            self.type = TemplateType(self.type)
        
        # 转换参数列表
        if self.parameters and isinstance(self.parameters[0], dict):
            self.parameters = [
                TemplateParameter.from_dict(p) if isinstance(p, dict) else p
                for p in self.parameters
            ]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['type'] = self.type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template':
        """从字典创建实例"""
        # 处理参数列表
        params = data.get('parameters', [])
        if params and isinstance(params[0], dict):
            params = [TemplateParameter.from_dict(p) for p in params]
        
        return cls(
            id=data['id'],
            name=data['name'],
            type=TemplateType(data['type']),
            category=data['category'],
            description=data.get('description', ''),
            structure=data.get('structure', {}),
            parameters=params,
            example=data.get('example', {}),
            preview=data.get('preview', ''),
            thumbnail=data.get('thumbnail', ''),
            tags=data.get('tags', []),
            usage_count=data.get('usage_count', 0),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', '')
        )
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """验证模板数据"""
        if not self.id or not self.name:
            return False, "ID和名称不能为空"
        
        if not self.structure:
            return False, "模板结构不能为空"
        
        # 验证参数定义
        param_names = set()
        for param in self.parameters:
            if not param.name:
                return False, "参数名称不能为空"
            if param.name in param_names:
                return False, f"参数名称重复: {param.name}"
            param_names.add(param.name)
        
        return True, None


def create_template(
    name: str,
    category: str,
    structure: Dict[str, Any],
    template_type: TemplateType = TemplateType.USER,
    **kwargs
) -> Template:
    """创建模板"""
    import uuid
    return Template(
        id=f"tpl_{uuid.uuid4().hex[:12]}",
        name=name,
        type=template_type,
        category=category,
        structure=structure,
        **kwargs
    )