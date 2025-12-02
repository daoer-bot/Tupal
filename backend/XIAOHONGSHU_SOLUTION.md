# 小红书热榜反爬虫解决方案

## 📋 问题说明

小红书官方API有严格的反爬虫机制，直接请求会返回406或403错误。当前实现已集成了多层降级方案，确保服务稳定可用。

## 🔧 解决方案（优先级从高到低）

### 方案1：自建RSSHub服务 ⭐⭐⭐⭐⭐（推荐）

**优点**：稳定、无限制、速度快
**成本**：需要一台服务器

#### 部署步骤：

```bash
# 使用Docker部署（推荐）
docker run -d --name rsshub -p 1200:1200 diygod/rsshub

# 或使用docker-compose
version: '3'
services:
  rsshub:
    image: diygod/rsshub
    ports:
      - '1200:1200'
    environment:
      - NODE_ENV=production
    restart: always
```

#### 配置使用：

修改 `backend/sources/xiaohongshu_source.py` 第21行：
```python
self.rsshub_base = "http://your-server-ip:1200"  # 改为你的RSSHub地址
```

### 方案2：使用稳定的公共RSSHub实例 ⭐⭐⭐⭐

国内可用的RSSHub公共实例列表：

```python
# 在 xiaohongshu_source.py 中添加更多备用实例
rsshub_instances = [
    "https://rsshub.app",           # 官方实例
    "https://rss.shab.fun",         # 备用实例1
    "https://rsshub.rssforever.com", # 备用实例2
    "http://localhost:1200",        # 本地实例（如果自建）
]
```

### 方案3：使用第三方聚合API ⭐⭐⭐

一些第三方服务提供热榜聚合API：

- **今日热榜** (tophub.today)
- **imsyy API** (免费热榜API)
- **自建爬虫服务**

示例代码：
```python
# 使用第三方API
url = "https://api.vvhan.com/api/hotlist/xiaohongshu"
data = await self.fetch_json(url)
```

### 方案4：使用代理服务 ⭐⭐

配置HTTP代理绕过反爬虫：

```python
# 在 base_source.py 的 fetch_json 方法中添加代理
proxies = {
    'http': 'http://proxy-server:port',
    'https': 'https://proxy-server:port',
}
response = requests.get(url, headers=headers, proxies=proxies)
```

### 方案5：使用Selenium/Playwright ⭐

使用浏览器自动化工具模拟真实用户：

```python
# 需要安装: pip install playwright
from playwright.async_api import async_playwright

async def fetch_with_browser(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        content = await page.content()
        await browser.close()
        return content
```

### 方案6：当前默认方案（模拟数据） ⭐⭐⭐

**优点**：完全稳定、无依赖、立即可用
**缺点**：不是真实数据

当前实现已包含高质量的模拟数据，包含30个贴近小红书实际热门话题。

## 🚀 快速开始

### 推荐配置（使用自建RSSHub）

1. **部署RSSHub**：
```bash
# 在你的服务器上运行
docker run -d --name rsshub -p 1200:1200 diygod/rsshub
```

2. **修改配置**：
```python
# backend/sources/xiaohongshu_source.py 第21行
self.rsshub_base = "http://your-server-ip:1200"
```

3. **测试**：
```bash
cd backend
python test_xiaohongshu.py
```

## 📝 当前实现说明

当前 `xiaohongshu_source.py` 已实现三层降级策略：

1. **第一层**：尝试RSSHub官方实例 (rsshub.app)
2. **第二层**：尝试备用RSSHub实例 (rss.shab.fun)
3. **第三层**：使用高质量模拟数据（保证服务可用）

这确保了即使所有RSSHub实例都不可用，服务仍然能正常运行。

## 🔍 验证方法

测试RSSHub是否可用：
```bash
curl https://rsshub.app/xiaohongshu/board/hot
```

如果返回XML格式的RSS数据，说明可用。

## 💡 建议

- **小型项目**：使用模拟数据或第三方API
- **中型项目**：使用公共RSSHub实例 + 模拟数据降级
- **大型项目**：自建RSSHub服务，确保稳定性

## 📞 技术支持

- RSSHub官方文档：https://docs.rsshub.app/
- RSSHub GitHub：https://github.com/DIYgod/RSSHub
- 小红书路由说明：https://docs.rsshub.app/social-media.html#xiao-hong-shu

## 🎯 当前状态

✅ 已实现多层降级机制
✅ 服务稳定可用
✅ 支持自定义RSSHub实例
⚠️ 建议自建RSSHub获得最佳效果