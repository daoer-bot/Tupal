"""
素材数据模型
定义素材的数据结构和类型
"""
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict


class MaterialType(str, Enum):
    """素材类型枚举"""
    TEXT = "text"           # 文本素材（产品介绍、品牌故事等）
    IMAGE = "image"         # 图片素材（产品图片、参考图等）
    STYLE = "style"         # 风格素材（语言风格、语调设置等）
    PRODUCT = "product"     # 产品素材（组合型，包含文本+图片）
    DATA = "data"           # 数据素材（测评数据、参数等）


class MaterialCategory(str, Enum):
    """素材分类枚举 - 5大核心类型"""
    VISUAL_CORE = "视觉核心素材"        # 封面图、场景图、生活片段
    DETAIL_SHOWCASE = "细节展示素材"    # 产品特写、使用效果、材质纹理
    INFO_STRUCTURE = "信息结构素材"     # 表格、流程图、结构图、截图
    COMPARISON_PROOF = "对比验证素材"   # 前后对比、数据验证、测评参数
    TEXT_GRAPHIC = "文案配图素材"       # 金句、标题、引导文案
    OTHER = "其他"


# 旧分类到新分类的映射字典（用于向后兼容）
CATEGORY_MIGRATION_MAP = {
    "封面素材": "视觉核心素材",
    "场景素材": "视觉核心素材",
    "生活碎片素材": "视觉核心素材",
    "细节特写素材": "细节展示素材",
    "信息型素材": "信息结构素材",
    "对比素材": "对比验证素材",
    "数据类素材": "对比验证素材",
    "文案素材": "文案配图素材",
}


@dataclass
class Material:
    """素材实体类"""
    
    # 必填字段
    id: str
    name: str
    type: MaterialType
    category: MaterialCategory
    content: Dict[str, Any]
    
    # 可选字段
    tags: List[str] = field(default_factory=list)
    description: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保时间戳
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        
        # 类型转换
        if isinstance(self.type, str):
            self.type = MaterialType(self.type)
        if isinstance(self.category, str):
            # 向后兼容：自动映射旧分类到新分类
            category_str = self.category
            if category_str in CATEGORY_MIGRATION_MAP:
                category_str = CATEGORY_MIGRATION_MAP[category_str]
            self.category = MaterialCategory(category_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 枚举类型转换为字符串
        data['type'] = self.type.value
        data['category'] = self.category.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Material':
        """从字典创建实例"""
        return cls(
            id=data['id'],
            name=data['name'],
            type=MaterialType(data['type']),
            category=MaterialCategory(data['category']),
            content=data['content'],
            tags=data.get('tags', []),
            description=data.get('description', ''),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', '')
        )
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        验证素材数据的有效性
        
        Returns:
            (是否有效, 错误信息)
        """
        # 验证基本字段
        if not self.id or not self.id.strip():
            return False, "素材ID不能为空"
        
        if not self.name or not self.name.strip():
            return False, "素材名称不能为空"
        
        if not self.content:
            return False, "素材内容不能为空"
        
        # 根据类型验证内容结构
        if self.type == MaterialType.TEXT:
            if 'text' not in self.content or not self.content['text'].strip():
                return False, "文本素材必须包含非空的text字段"
        
        elif self.type == MaterialType.IMAGE:
            if 'url' not in self.content or not self.content['url'].strip():
                return False, "图片素材必须包含非空的url字段"
        
        elif self.type == MaterialType.STYLE:
            if 'tone' not in self.content and 'style_guide' not in self.content:
                return False, "风格素材必须包含tone或style_guide字段"
        
        elif self.type == MaterialType.PRODUCT:
            if 'description' not in self.content or not self.content['description'].strip():
                return False, "产品素材必须包含非空的description字段"

        elif self.type == MaterialType.DATA:
            if 'items' not in self.content or not self.content['items']:
                return False, "数据素材必须包含非空的items字段"
        
        return True, None


@dataclass
class TextMaterialContent:
    """文本素材内容结构"""
    text: str
    variables: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ImageMaterialContent:
    """图片素材内容结构"""
    url: str
    thumbnail: str = ""
    width: int = 0
    height: int = 0
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StyleMaterialContent:
    """风格素材内容结构"""
    tone: str
    style_guide: str = ""
    examples: List[str] = field(default_factory=list)
    temperature: float = 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProductMaterialContent:
    """产品素材内容结构（组合型）"""
    description: str
    images: List[str] = field(default_factory=list)  # 图片素材ID列表
    specs: Dict[str, Any] = field(default_factory=dict)
    selling_points: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DataMaterialContent:
    """数据素材内容结构"""
    items: List[Dict[str, str]] = field(default_factory=list)  # [{'key': '续航', 'value': '10小时'}]
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def create_material(
    name: str,
    material_type: MaterialType,
    category: MaterialCategory,
    content: Dict[str, Any],
    tags: List[str] = None,
    description: str = ""
) -> Material:
    """
    创建素材实例的辅助函数
    
    Args:
        name: 素材名称
        material_type: 素材类型
        category: 素材分类
        content: 素材内容
        tags: 标签列表
        description: 描述
        
    Returns:
        Material实例
    """
    import uuid
    
    material_id = f"mat_{uuid.uuid4().hex[:12]}"
    
    return Material(
        id=material_id,
        name=name,
        type=material_type,
        category=category,
        content=content,
        tags=tags or [],
        description=description
    )