# 图宝 (Tupal) - AI小红书图文生成器

一句话生成完整的小红书图文内容，让创作变得简单高效。

## 项目简介

图宝是一个基于 AI 的小红书图文生成器，通过输入一句话主题描述，系统自动生成 6-9 页完整的小红书图文内容，包括文案大纲和配套图片。

### 核心功能

| 功能模块 | 描述 | 技术 |
|---------|------|------|
| 智能大纲生成 | 基于用户输入自动生成内容大纲 | Gemini 3 API |
| 批量图片生成 | 并发生成所有页面配图 | 多服务商支持 |
| 实时进度追踪 | 通过 SSE 流式传输显示进度 | Flask SSE |
| 个性化定制 | 支持上传参考图片，保持风格一致 | 图片分析 |
| 历史管理 | 保存和管理创作历史 | 本地存储 |

## 技术架构

### 后端技术栈
- **框架**: Flask 3.0.0
- **AI 服务**: Gemini 3, OpenAI
- **图片处理**: Pillow
- **异步支持**: gevent

### 前端技术栈
- **框架**: Vue 3.3.8
- **语言**: TypeScript 5.3.2
- **构建工具**: Vite 5.0.5
- **状态管理**: Pinia 2.1.7
- **路由**: Vue Router 4.2.5

## 项目结构

```
Tupal/
├── backend/              # 后端 Flask 应用
│   ├── app.py           # 主应用
│   ├── config.py        # 配置文件
│   ├── requirements.txt # Python 依赖
│   ├── api/            # API 路由层
│   ├── services/       # 业务逻辑层
│   ├── generators/     # AI 服务商层
│   ├── utils/          # 工具函数
│   └── storage/        # 存储管理
│
├── frontend/            # 前端 Vue 应用
│   ├── src/
│   │   ├── main.ts     # 应用入口
│   │   ├── App.vue     # 根组件
│   │   ├── router/     # 路由配置
│   │   ├── store/      # 状态管理
│   │   ├── services/   # API 服务
│   │   └── views/      # 页面组件
│   ├── package.json
│   └── vite.config.ts
│
├── project_architecture.md  # 架构设计文档
├── req.md                   # 需求文档
└── README.md               # 项目说明
```

## 快速开始

### 前置要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 1. 后端设置

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API Keys

# 启动后端服务
python app.py
```

后端服务将在 `http://localhost:5000` 启动。

### 2. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 `http://localhost:5173` 启动。

## 工作流程

1. **输入阶段**: 用户输入创作主题，可选择上传参考图片
2. **大纲生成**: Gemini 3 分析输入，生成结构化大纲
3. **内容确认**: 用户编辑页面顺序和描述
4. **图片生成**: 系统并发生成所有页面配图（最高 25 并发）
5. **实时更新**: 通过 SSE 技术实时推送进度
6. **结果交付**: 提供一键下载功能

## API 端点

### 后端 API

- `POST /api/generate-outline` - 生成内容大纲
- `POST /api/generate-images` - 生成图片
- `GET /api/progress/{task_id}` - 获取任务进度（SSE）
- `GET /api/history` - 获取历史记录
- `DELETE /api/history/{id}` - 删除历史记录
- `POST /api/upload-reference` - 上传参考图片

## 开发进度

### ✅ 第一阶段：基础架构（已完成）
- [x] 项目目录结构创建
- [x] Flask 后端基础搭建
- [x] Vue3 前端项目初始化
- [x] API 路由定义
- [x] 状态管理配置

### 🚧 第二阶段：核心功能（进行中）
- [ ] AI 服务商工厂模式实现
- [ ] 智能大纲生成功能
- [ ] 基础图片生成功能

### 📋 第三阶段：高级功能（待开始）
- [ ] SSE 实时进度推送
- [ ] 并发图片生成优化
- [ ] 参考图片上传和风格匹配

### 📋 第四阶段：界面和完善（待开始）
- [ ] 前端核心组件开发
- [ ] 历史管理系统
- [ ] 项目测试和优化

## 环境变量配置

### 后端环境变量 (.env)

```env
# Flask 配置
SECRET_KEY=your-secret-key
FLASK_DEBUG=True

# AI 服务配置
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
IMAGE_API_KEY=your-image-api-key

# 并发配置
MAX_CONCURRENT_GENERATIONS=25
```

### 前端环境变量 (.env)

```env
VITE_API_URL=http://localhost:5000/api
```

## 支持的 AI 服务商

| 服务商类型 | 模型 | 特点 |
|-----------|------|------|
| Image API | Nano banana Pro | 高质量，支持并发 |
| Google GenAI | 官方模型 | 稳定可靠 |
| OpenAI 兼容 | DALL-E 3 | 通用性强 |

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，欢迎提交 Issue。

---

**让创作更简单 - 图宝团队**