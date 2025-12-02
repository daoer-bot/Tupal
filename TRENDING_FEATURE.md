# 灵感与发现 - 热榜功能说明

## 功能概述

【灵感与发现】是图宝项目的全新板块，集成了主流社交媒体平台的实时热榜数据，为用户提供创作灵感来源。

## 已实现的平台

- ✅ **微博热搜** - 实时更新的微博热搜榜
- ✅ **知乎热榜** - 知乎站内热门话题
- ✅ **抖音热点** - 抖音平台热门话题
- ✅ **B站热门** - B站热门视频排行
- ✅ **百度热搜** - 百度搜索热榜

## 技术实现

### 后端架构

```
backend/
├── sources/                    # 数据源模块
│   ├── __init__.py
│   ├── base_source.py         # 数据源基类
│   ├── source_manager.py      # 数据源管理器
│   ├── weibo_source.py        # 微博数据源
│   ├── zhihu_source.py        # 知乎数据源
│   ├── douyin_source.py       # 抖音数据源
│   ├── bilibili_source.py     # B站数据源
│   └── baidu_source.py        # 百度数据源
├── services/
│   └── trending_service.py    # 热榜服务（含缓存）
└── api/
    └── routes.py              # API路由（新增热榜接口）
```

### 前端架构

```
frontend/src/
├── views/
│   └── TrendingView.vue       # 热榜主页面
├── services/
│   └── api.ts                 # API服务（新增热榜方法）
├── router/
│   └── index.ts               # 路由配置
└── App.vue                    # 导航菜单
```

## API 接口

### 1. 获取所有数据源列表
```
GET /api/trending/sources
```

**响应示例：**
```json
{
  "success": true,
  "data": [
    {
      "id": "weibo",
      "name": "微博热搜",
      "icon": "/icons/weibo.png",
      "interval": 300
    }
  ]
}
```

### 2. 获取指定平台热榜
```
GET /api/trending/{source_id}?force_refresh=false
```

**参数：**
- `source_id`: 平台ID（weibo/zhihu/douyin/bilibili/baidu）
- `force_refresh`: 是否强制刷新缓存（可选，默认false）

**响应示例：**
```json
{
  "success": true,
  "data": {
    "source_id": "weibo",
    "source_name": "微博热搜",
    "icon": "/icons/weibo.png",
    "items": [
      {
        "id": "weibo_1_xxx",
        "title": "热搜标题",
        "url": "https://s.weibo.com/xxx",
        "hot_value": "1234567",
        "index": 1,
        "extra": {
          "tag": "热"
        }
      }
    ],
    "updated_time": "2024-01-01T12:00:00",
    "from_cache": false
  }
}
```

### 3. 获取所有平台热榜
```
GET /api/trending?force_refresh=false
```

**响应示例：**
```json
{
  "success": true,
  "data": [
    // 多个平台的热榜数据数组
  ]
}
```

## 核心特性

### 1. 智能缓存机制
- **缓存时长**: 30分钟（1800秒）
- **更新策略**: 
  - 缓存未过期时返回缓存数据
  - 支持强制刷新（force_refresh=true）
  - 获取失败时降级返回过期缓存
- **性能优化**: 避免频繁请求，减轻服务器压力

### 2. 异步并发抓取
- 使用Python asyncio实现异步数据获取
- 多平台数据并发抓取，提升响应速度
- 单个平台失败不影响其他平台

### 3. 优雅降级
- 数据抓取失败时返回缓存数据
- 单个数据源异常不影响整体功能
- 完善的错误处理和日志记录

### 4. 响应式UI设计
- 卡片式网格布局，自适应屏幕
- 实时显示更新时间
- 支持移动端适配
- 前三名特殊高亮显示

## 安装部署

### 1. 安装依赖

**后端：**
```bash
cd backend
pip install -r requirements.txt
```

新增依赖包：
- `beautifulsoup4==4.12.2` - HTML解析
- `lxml==4.9.3` - XML/HTML解析器

**前端：**
```bash
cd frontend
npm install
```
（无需额外依赖）

### 2. 启动服务

**后端：**
```bash
cd backend
python app.py
```

**前端：**
```bash
cd frontend
npm run dev
```

### 3. 访问功能

打开浏览器访问：`http://localhost:5173/trending`

或点击侧边栏的【灵感与发现】导航。

## 使用说明

1. **查看热榜**
   - 进入【灵感与发现】页面
   - 自动加载所有平台的热榜数据
   - 每个平台显示前10条热门内容

2. **刷新数据**
   - 点击右上角【刷新全部】按钮
   - 强制刷新所有平台的最新数据
   - 刷新过程中显示加载动画

3. **查看详情**
   - 点击任意热榜条目
   - 在新标签页打开原文链接
   - 支持跳转到对应平台查看完整内容

4. **缓存标识**
   - 卡片右上角显示"缓存数据"标识
   - 表示当前显示的是缓存内容
   - 可通过刷新获取最新数据

## 数据源扩展

如需添加新的数据源，请按以下步骤操作：

### 1. 创建数据源类

在 `backend/sources/` 目录下创建新文件，例如 `toutiao_source.py`:

```python
from typing import List
from .base_source import BaseSource, TrendingItem

class ToutiaoSource(BaseSource):
    def __init__(self):
        super().__init__()
        self.source_id = "toutiao"
        self.source_name = "今日头条"
        self.icon = "/icons/toutiao.png"
        self.interval = 600  # 10分钟
    
    async def fetch_data(self) -> List[TrendingItem]:
        # 实现数据抓取逻辑
        pass
```

### 2. 注册数据源

在 `backend/services/trending_service.py` 的 `_initialize_sources` 方法中添加：

```python
from sources.toutiao_source import ToutiaoSource

def _initialize_sources(self):
    sources = [
        # ... 现有数据源
        ToutiaoSource(),  # 新增
    ]
```

### 3. 添加图标

将平台图标放置在 `newsnow/public/icons/` 目录下。

## 注意事项

### 1. 反爬虫策略
- 各平台可能有反爬虫机制
- 建议设置合理的请求间隔
- 必要时添加User-Agent和Cookie

### 2. 数据时效性
- 热榜数据实时性要求高
- 建议根据平台特性调整缓存时间
- 微博等快速更新的平台可设置更短缓存

### 3. 错误处理
- 网络请求可能失败
- 页面结构可能变化
- 建议定期检查数据源可用性

### 4. 性能优化
- 使用缓存减少请求频率
- 并发抓取提升响应速度
- 避免在高峰期频繁刷新

## 故障排查

### 问题1：数据源返回空数据

**可能原因：**
- 平台API变更
- 网络连接问题
- 反爬虫限制

**解决方案：**
1. 检查后端日志
2. 验证URL是否可访问
3. 更新数据源爬虫逻辑

### 问题2：前端显示错误

**可能原因：**
- API请求失败
- 数据格式不匹配
- 网络超时

**解决方案：**
1. 打开浏览器控制台查看错误
2. 检查API响应格式
3. 验证后端服务是否运行

### 问题3：缓存不更新

**可能原因：**
- 缓存时间未过期
- 强制刷新参数未生效

**解决方案：**
1. 等待缓存过期（30分钟）
2. 使用强制刷新功能
3. 重启后端服务清除缓存

## 未来优化方向

- [ ] 添加更多平台支持（GitHub、掘金、StackOverflow等）
- [ ] 实现用户自定义平台订阅
- [ ] 添加热榜数据趋势分析
- [ ] 支持关键词搜索和过滤
- [ ] 实现热榜数据持久化存储
- [ ] 添加数据可视化图表
- [ ] 支持消息推送通知

## 技术支持

如有问题或建议，请通过以下方式联系：

- GitHub Issues
- 项目文档
- 开发团队

---

**版本**: v1.0.0  
**最后更新**: 2024-12-02  
**维护者**: Tupal Team