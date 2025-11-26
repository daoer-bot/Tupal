# 图宝后端服务

基于 Flask 的 RESTful API 服务，提供 AI 图文生成功能。

## 功能特性

- ✅ RESTful API 接口
- ✅ SSE 实时进度推送
- ✅ CORS 跨域支持
- ✅ 模块化架构设计
- 🚧 AI 大纲生成（待实现）
- 🚧 批量图片生成（待实现）
- 🚧 历史记录管理（待实现）

## 项目结构

```
backend/
├── app.py                 # Flask 主应用
├── config.py             # 配置文件
├── requirements.txt      # Python 依赖
├── .env.example         # 环境变量模板
├── api/                 # API 层
│   ├── __init__.py
│   └── routes.py        # 路由定义
├── services/            # 服务层
│   └── __init__.py
├── generators/          # AI 服务商层
│   └── __init__.py
├── utils/              # 工具层
│   └── __init__.py
└── storage/            # 存储层
    └── __init__.py
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的 API Key：

```env
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
IMAGE_API_KEY=your-image-api-key
```

### 3. 运行服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

## API 端点

### 健康检查

```http
GET /
GET /health
```

### 生成大纲

```http
POST /api/generate-outline
Content-Type: application/json

{
  "topic": "如何提高工作效率",
  "reference_image": "https://example.com/image.jpg"
}
```

### 生成图片

```http
POST /api/generate-images
Content-Type: application/json

{
  "task_id": "task_20231126",
  "pages": [
    {
      "page_number": 1,
      "title": "封面",
      "description": "吸引眼球的标题"
    }
  ]
}
```

### 获取进度（SSE）

```http
GET /api/progress/{task_id}
```

### 历史记录

```http
GET /api/history                    # 获取所有历史
GET /api/history/{history_id}       # 获取特定历史
DELETE /api/history/{history_id}    # 删除历史
```

### 上传参考图片

```http
POST /api/upload-reference
Content-Type: multipart/form-data

file: [binary]
```

## 开发状态

### ✅ 已完成
- [x] Flask 基础架构
- [x] API 路由定义
- [x] CORS 配置
- [x] 配置管理
- [x] 错误处理

### 🚧 进行中
- [ ] AI 服务商工厂模式
- [ ] Gemini 大纲生成
- [ ] 图片生成服务
- [ ] SSE 实时推送
- [ ] 历史管理服务

## 技术栈

- **Web 框架**: Flask 3.0.0
- **CORS**: Flask-CORS 4.0.0
- **AI 服务**: google-generativeai, openai
- **图片处理**: Pillow
- **异步支持**: gevent

## 环境要求

- Python 3.8+
- pip

## 注意事项

1. 确保所有 API Key 已正确配置
2. 生产环境请修改 `SECRET_KEY`
3. 根据需要调整 `MAX_CONCURRENT_GENERATIONS` 并发数
4. 图片上传大小限制为 16MB

## 下一步开发计划

1. 实现 AI 服务商工厂模式
2. 集成 Gemini 3 API
3. 开发图片生成服务
4. 实现 SSE 实时推送
5. 完善历史管理功能