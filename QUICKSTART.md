# 图宝 - 快速启动指南

## 📋 前置要求

- Python 3.8+
- Node.js 16+
- Gemini API Key（必需）或 OpenAI API Key

## 🚀 快速启动

### 1. 后端设置

```bash
# 进入后端目录
cd backend

# 安装 Python 依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
```

编辑 `.env` 文件，至少配置以下内容：

```env
# 必需：Gemini API Key（用于生成大纲）
GEMINI_API_KEY=your-gemini-api-key-here

# 可选：OpenAI API Key
OPENAI_API_KEY=your-openai-api-key-here

# 可选：图片生成服务
IMAGE_API_KEY=your-image-api-key
IMAGE_API_URL=https://your-image-api-url
```

#### 获取 Gemini API Key

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 点击 "Create API Key"
3. 复制生成的 API Key 到 `.env` 文件

### 2. 测试后端配置

```bash
# 在 backend 目录下运行测试脚本
python test_outline.py
```

测试脚本会验证：
- ✓ API Key 配置是否正确
- ✓ 生成器能否正常创建
- ✓ 大纲生成功能是否工作

如果测试通过，继续下一步。

### 3. 启动后端服务

```bash
# 在 backend 目录下
python app.py
```

后端服务将在 `http://localhost:5000` 启动。

打开浏览器访问：`http://localhost:5000` 应该看到：
```json
{
  "success": true,
  "message": "图宝 API is running",
  "version": "1.0.0"
}
```

### 4. 前端设置

打开新的终端窗口：

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 `http://localhost:5173` 启动。

### 5. 测试完整流程

1. 打开浏览器访问 `http://localhost:5173`
2. 在首页输入框中输入主题，例如："如何提高工作效率的10个小技巧"
3. 点击"开始生成"按钮
4. 等待大纲生成完成
5. 查看生成的内容大纲

## 🔧 故障排除

### 后端问题

#### 问题：提示 "找不到模块"
```bash
# 解决方案：确保在 backend 目录下安装依赖
cd backend
pip install -r requirements.txt
```

#### 问题：API Key 错误
```bash
# 解决方案：检查 .env 文件中的 API Key 是否正确
cat .env  # Linux/Mac
type .env # Windows

# 重新运行测试脚本验证
python test_outline.py
```

#### 问题：端口被占用
```bash
# 解决方案：修改端口
PORT=5001 python app.py
```

### 前端问题

#### 问题：依赖安装失败
```bash
# 解决方案：清理缓存后重新安装
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### 问题：TypeScript 错误
这些错误是正常的，会在 `npm install` 后自动解决。如果持续存在：
```bash
# 重新构建 TypeScript 配置
npm run build
```

#### 问题：无法连接后端
- 确保后端服务正在 `http://localhost:5000` 运行
- 检查浏览器控制台是否有 CORS 错误
- Vite 已配置代理，`/api` 请求会自动转发到后端

## 📊 当前功能状态

### ✅ 已完成
- [x] 项目基础架构
- [x] Flask 后端 API
- [x] Vue3 前端框架
- [x] AI 服务商工厂模式
- [x] Gemini 大纲生成
- [x] OpenAI 兼容接口
- [x] 首页界面

### 🚧 开发中
- [ ] 批量图片生成
- [ ] 实时进度显示（SSE）
- [ ] 图片上传和风格匹配
- [ ] 历史管理功能

## 🎯 下一步开发

如果您想继续开发：

1. **批量图片生成**：实现 `backend/services/image_service.py`
2. **SSE 实时推送**：完善进度追踪系统
3. **前端组件**：开发生成器界面和进度显示
4. **历史管理**：实现本地存储和管理功能

## 📚 更多信息

- 完整文档：查看 [README.md](README.md)
- 架构设计：查看 [project_architecture.md](project_architecture.md)
- 后端文档：查看 [backend/README.md](backend/README.md)
- 前端文档：查看 [frontend/README.md](frontend/README.md)

## 💡 提示

- 首次使用 Gemini API 可能需要等待几秒钟
- 如果生成失败，检查 API Key 配额和网络连接
- 开发时建议同时打开浏览器开发者工具查看网络请求

---

**祝您使用愉快！** 🎉