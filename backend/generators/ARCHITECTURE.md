# 大模型生成架构文档

## 📋 架构概述

本项目采用**能力导向的生成器架构**，支持多种AI服务商和内容类型的统一管理。

## 🎯 核心设计理念

### 1. 内容类型枚举（ContentType）
```python
class ContentType(Enum):
    TEXT = "text"      # 文本生成（大纲、文案等）
    IMAGE = "image"    # 图片生成（静态图、动图等）
    VIDEO = "video"    # 视频生成（短视频、动画等）
```

### 2. 统一生成结果（GenerationResult）
```python
class GenerationResult:
    success: bool           # 是否成功
    content_type: ContentType  # 内容类型
    url: str               # 生成内容的URL
    format: str            # 文件格式
    metadata: Dict         # 元数据
    error: str             # 错误信息
```

### 3. 能力声明系统
每个生成器通过 `SUPPORTED_TYPES` 声明支持的内容类型：

```python
class GeminiGenerator(BaseGenerator):
    SUPPORTED_TYPES = {ContentType.TEXT}

class OpenAIGenerator(BaseGenerator):
    SUPPORTED_TYPES = {ContentType.TEXT, ContentType.IMAGE}

class ImageAPIGenerator(BaseGenerator):
    SUPPORTED_TYPES = {ContentType.IMAGE}
```

## 🏗️ 架构层次

```
┌─────────────────────────────────────────┐
│           Service Layer                 │
│  (outline_service, image_service)       │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│       GeneratorFactory                  │
│  ┌──────────────────────────────┐      │
│  │ create_generator(provider)   │      │
│  │ get_available_providers()    │      │
│  │ get_provider_capabilities()  │      │
│  └──────────────────────────────┘      │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴─────────┬─────────┬─────────┐
    ▼                   ▼         ▼         ▼
┌────────┐      ┌──────────┐  ┌──────┐  ┌──────┐
│ Gemini │      │ OpenAI   │  │Image │  │ Mock │
│(TEXT)  │      │(TEXT+IMG)│  │(IMG) │  │(ALL) │
└────────┘      └──────────┘  └──────┘  └──────┘
```

## 📦 生成器能力矩阵

| 服务商 | TEXT | IMAGE | VIDEO | 用途 |
|--------|------|-------|-------|------|
| Gemini | ✅ | ❌ | ❌ | 大纲生成 |
| OpenAI | ✅ | ✅ | ❌ | 全能型 |
| ImageAPI | ❌ | ✅ | ❌ | 图片生成 |
| Mock | ✅ | ✅ | ❌ | 开发测试 |

## 🔧 使用方式

### 方式1：使用统一接口（推荐）

```python
from generators.factory import GeneratorFactory
from generators.base_generator import ContentType

# 创建生成器
generator = GeneratorFactory.create_generator('openai', ContentType.TEXT)

# 统一调用
result = generator.generate(
    content_type=ContentType.TEXT,
    prompt="健康饮食指南",
    reference_image="https://..."
)

# 处理结果
if result.success:
    pages = result.metadata.get('pages', [])
    print(f"生成了 {len(pages)} 页内容")
else:
    print(f"生成失败: {result.error}")
```

### 方式2：使用兼容接口（向后兼容）

```python
from generators.factory import get_outline_generator, get_image_generator

# 获取大纲生成器
outline_gen = get_outline_generator('gemini')
result = outline_gen.generate_outline(topic="健康饮食")

# 获取图片生成器
image_gen = get_image_generator('image_api')
result = image_gen.generate_image(prompt="健康食物", width=1080, height=1440)
```

## 🎨 能力查询

### 查询可用服务商

```python
# 查询支持TEXT的服务商
text_providers = GeneratorFactory.get_available_providers(ContentType.TEXT)
# 返回: ['gemini', 'openai', 'mock']

# 查询支持IMAGE的服务商
image_providers = GeneratorFactory.get_available_providers(ContentType.IMAGE)
# 返回: ['openai', 'image_api', 'mock']
```

### 查询服务商能力

```python
# 查询OpenAI支持的内容类型
capabilities = GeneratorFactory.get_provider_capabilities('openai')
# 返回: ['text', 'image']

# 获取所有服务商能力
all_caps = GeneratorFactory.get_all_capabilities()
# 返回: {
#   'gemini': ['text'],
#   'openai': ['text', 'image'],
#   'image_api': ['image'],
#   'mock': ['text', 'image']
# }
```

## 🔌 扩展新服务商

### 步骤1：创建生成器类

```python
from .base_generator import BaseGenerator, ContentType, GenerationResult

class NewGenerator(BaseGenerator):
    # 声明支持的类型
    SUPPORTED_TYPES = {ContentType.IMAGE}
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        # 初始化API客户端
    
    def generate(self, content_type: ContentType, prompt: str, **kwargs) -> GenerationResult:
        if not self.supports(content_type):
            return self._create_unsupported_result(content_type)
        
        if content_type == ContentType.IMAGE:
            return self._generate_image(prompt, **kwargs)
        
        return self._create_unsupported_result(content_type)
    
    def _generate_image(self, prompt: str, **kwargs) -> GenerationResult:
        try:
            # 调用API生成图片
            image_url = self._call_api(prompt, **kwargs)
            
            return self._create_success_result(
                content_type=ContentType.IMAGE,
                url=image_url,
                format="png"
            )
        except Exception as e:
            return self._create_error_result(ContentType.IMAGE, str(e))
```

### 步骤2：注册到工厂

```python
# 在 factory.py 中添加
from .new_generator import NewGenerator

class GeneratorFactory:
    GENERATOR_TYPES = {
        'gemini': GeminiGenerator,
        'openai': OpenAIGenerator,
        'image_api': ImageAPIGenerator,
        'new_provider': NewGenerator,  # 新增
        'mock': MockGenerator
    }
```

### 步骤3：添加配置支持

```python
# 在 create_generator 方法中添加
elif provider == 'new_provider':
    api_key = current_app.config.get('NEW_PROVIDER_API_KEY')
    if not api_key:
        logger.error("NEW_PROVIDER_API_KEY 未配置")
        return None
    generator = NewGenerator(api_key=api_key)
```

## 🛡️ 适配不同厂家格式

### 问题：不同厂家返回格式不一致

ImageAPI 的响应可能是：
- `{"image_url": "..."}`
- `{"url": "..."}`
- `{"images": ["..."]}`

### 解决方案：在生成器内部适配

```python
def _generate_image(self, prompt: str, **kwargs) -> GenerationResult:
    response = self._call_api(prompt, **kwargs)
    
    # 适配多种返回格式
    image_url = None
    if 'image_url' in response:
        image_url = response['image_url']
    elif 'url' in response:
        image_url = response['url']
    elif 'images' in response and len(response['images']) > 0:
        image_url = response['images'][0]
    
    if image_url:
        return self._create_success_result(
            content_type=ContentType.IMAGE,
            url=image_url,
            format="png"
        )
    else:
        return self._create_error_result(
            ContentType.IMAGE,
            '无法从响应中获取图片URL'
        )
```

## 📊 架构优势

### ✅ 优点

1. **统一接口**：所有生成器使用相同的调用方式
2. **能力透明**：通过 `SUPPORTED_TYPES` 清晰声明能力
3. **易于扩展**：添加新服务商只需3步
4. **格式适配**：每个生成器内部处理厂家差异
5. **向后兼容**：保留旧接口，平滑迁移
6. **类型安全**：使用枚举避免字符串错误

### 🎯 适用场景

- ✅ 需要支持多个AI服务商
- ✅ 不同服务商能力不同
- ✅ 需要动态切换服务商
- ✅ 服务商API格式差异大
- ✅ 未来可能添加更多内容类型

## 🔄 迁移指南

### 旧代码

```python
generator = GeminiGenerator(api_key="...")
result = generator.generate_outline(topic="健康饮食")
if result['success']:
    pages = result['pages']
```

### 新代码（推荐）

```python
generator = GeneratorFactory.create_generator('gemini', ContentType.TEXT)
result = generator.generate(ContentType.TEXT, prompt="健康饮食")
if result.success:
    pages = result.metadata['pages']
```

### 新代码（兼容方式）

```python
# 仍然可以使用旧接口，内部自动适配
generator = get_outline_generator('gemini')
result = generator.generate_outline(topic="健康饮食")
if result['success']:
    pages = result['pages']
```

## 📝 注意事项

1. **能力检查**：使用前通过 `supports()` 检查能力
2. **错误处理**：始终检查 `result.success`
3. **配置验证**：确保API Key等配置完整
4. **格式适配**：新服务商需处理其特定的响应格式
5. **元数据使用**：不同内容类型的元数据结构可能不同

## 🚀 未来扩展

可以轻松添加：
- 🎵 音频生成（AUDIO类型）
- 🎬 长视频生成（扩展VIDEO类型）
- 📄 文档生成（DOCUMENT类型）
- 🎨 3D模型生成（MODEL_3D类型）

只需：
1. 在 `ContentType` 枚举中添加新类型
2. 创建支持该类型的生成器
3. 在工厂中注册

---

**更新时间**: 2025-01-26  
**架构版本**: v2.0