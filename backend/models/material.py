"""
素材数据模型 - 最终极简版
图文生成工具的核心素材：文本 + 图片 + 参考案例
"""
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict


class MaterialType(str, Enum):
    """只有3种核心素材"""
    TEXT = "text"           # 文本：标题、文案、话术、数据
    IMAGE = "image"         # 图片：产品图、配图、截图
    REFERENCE = "reference" # 参考：优秀案例、对标账号、风格参考


@dataclass
class Material:
    """极简素材实体"""
    
    # 核心字段
    id: str
    name: str                # 素材名称
    type: MaterialType       # 素材类型
    content: Dict[str, Any]  # 素材内容
    
    # 标签
    tags: List[str] = field(default_factory=list)  # 美妆/穿搭/美食等
    
    # 管理字段
    description: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        """初始化处理"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        
        if isinstance(self.type, str):
            self.type = MaterialType(self.type)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['type'] = self.type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Material':
        """从字典创建实例"""
        return cls(
            id=data['id'],
            name=data['name'],
            type=MaterialType(data['type']),
            content=data['content'],
            tags=data.get('tags', []),
            description=data.get('description', ''),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', '')
        )
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """简单验证"""
        if not self.id or not self.name:
            return False, "ID和名称不能为空"
        
        if not self.content:
            return False, "内容不能为空"
        
        # 检查必需字段
        if self.type == MaterialType.TEXT:
            if 'text' not in self.content:
                return False, "文本素材需要text字段"
        
        elif self.type == MaterialType.IMAGE:
            if 'url' not in self.content:
                return False, "图片素材需要url字段"
        
        elif self.type == MaterialType.REFERENCE:
            if 'reference_type' not in self.content:
                return False, "参考素材需要reference_type字段"
        
        return True, None


# ===== 一键创建函数 =====

def create_text(name: str, text: str, **kwargs) -> Material:
    """创建文本素材"""
    import uuid
    return Material(
        id=f"mat_{uuid.uuid4().hex[:12]}",
        name=name,
        type=MaterialType.TEXT,
        content={"text": text, **kwargs}
    )


def create_image(name: str, url: str, **kwargs) -> Material:
    """创建图片素材"""
    import uuid
    return Material(
        id=f"mat_{uuid.uuid4().hex[:12]}",
        name=name,
        type=MaterialType.IMAGE,
        content={"url": url, **kwargs}
    )


def create_reference(name: str, reference_type: str, **kwargs) -> Material:
    """创建参考素材"""
    import uuid
    return Material(
        id=f"mat_{uuid.uuid4().hex[:12]}",
        name=name,
        type=MaterialType.REFERENCE,
        content={"reference_type": reference_type, **kwargs}
    )