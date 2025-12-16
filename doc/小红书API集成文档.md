# 小红书 API 集成技术文档

## 概述

xhs_mcp_agent 是一个将小红书 Web API 封装成可复用服务的完整解决方案。它提供了两种使用方式:
1. **MCP Server 模式**: 基于 Model Context Protocol,与 AI 工具集成
2. **REST API 模式**: 标准的 RESTful API 服务

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                   使用层                                  │
│  ┌──────────────┐           ┌──────────────┐            │
│  │ MCP Server   │           │ REST API     │            │
│  │ (mcp_server) │           │ (FastAPI)    │            │
│  └──────┬───────┘           └──────┬───────┘            │
└─────────┼──────────────────────────┼─────────────────────┘
          │                          │
          │    ┌──────────────┐      │
          └────┤ ClientManager│──────┘
               │  (共享层)     │
               └──────┬───────┘
                      │
          ┌───────────┴───────────┐
          │                       │
    ┌─────▼─────┐         ┌──────▼─────┐
    │ ApiClient │         │  XhsClient │
    │ (异步包装) │         │  (核心SDK) │
    └───────────┘         └────────────┘
                                │
                    ┌───────────┴───────────┐
                    │  小红书 Web API        │
                    │  - edith.xiaohongshu   │
                    │  - creator.xiaohongshu │
                    └───────────────────────┘
```

### 核心组件

#### 1. XhsClient (核心 SDK 层)

**位置**: `xhs_mcp_server/xhs/api.py`

**功能**: 与小红书 API 的直接交互层

**关键特性**:
- **请求签名**: 通过 `_pre_headers()` 方法生成 `x-s`, `x-t`, `x-s-common` 等签名头
- **Session 管理**: 使用 `requests.Session` 维护 Cookie 和连接
- **多端点支持**:
  - `https://edith.xiaohongshu.com` - 主 API
  - `https://creator.xiaohongshu.com` - 创作者 API
  - `https://customer.xiaohongshu.com` - 客服 API

**核心方法**:
```python
class XhsClient:
    def __init__(self, cookie, user_agent, timeout, proxies, sign):
        """初始化客户端"""

    def get(self, uri, params, is_creator, is_customer):
        """GET 请求"""

    def post(self, uri, data, is_creator, is_customer):
        """POST 请求"""

    # 笔记相关
    def get_note_by_id(self, note_id, xsec_token, xsec_source)
    def get_note_by_id_from_html(self, note_id, xsec_token, xsec_source)
    def get_note_by_keyword(self, keyword, page, page_size, sort, note_type)

    # 用户相关
    def get_user_info(self, user_id)
    def get_user_notes(self, user_id, cursor)
    def get_user_by_keyword(self, keyword, page, page_size)

    # Feed 相关
    def get_home_feed_category(self)
    def get_home_feed(self, feed_type)
```

**关键技术点**:

1. **请求签名机制**:
```python
def _pre_headers(self, url: str, data=None, quick_sign: bool = False):
    if quick_sign:
        signs = sign(url, data, a1=self.cookie_dict.get("a1"))
        self.__session.headers.update({
            "x-s": signs["x-s"],
            "x-t": signs["x-t"],
            "x-s-common": signs["x-s-common"]
        })
```

2. **Cookie 管理**:
```python
@property
def cookie(self):
    return cookie_jar_to_cookie_str(self.__session.cookies)

@cookie.setter
def cookie(self, cookie: str):
    update_session_cookies_from_cookie(self.__session, cookie)
```

3. **错误处理**:
```python
def request(self, method, url, **kwargs):
    response = self.__session.request(method, url, ...)

    if response.status_code == 471 or response.status_code == 461:
        raise NeedVerifyError("出现验证码")
    elif data.get("code") == ErrorEnum.IP_BLOCK.value.code:
        raise IPBlockError("IP被封")
    elif data.get("code") == ErrorEnum.SIGN_FAULT.value.code:
        raise SignError("签名错误")
```

#### 2. ApiClient (异步包装层)

**位置**: `xhs_mcp_server/shared/api.py`

**功能**: 将同步的 XhsClient 包装成异步接口

**关键特性**:
- 异步上下文管理
- 统一的请求/响应类型
- 异常转换和错误处理

**实现示例**:
```python
class ApiClient:
    def __init__(self, request: CreateClientRequest):
        self._client = XhsClient(
            cookie=request.cookie,
            user_agent=request.user_agent,
            timeout=request.timeout,
            proxies=request.proxies
        )

    async def get_note(self, request: NoteRequest) -> NoteResponse:
        """获取笔记详情 - 异步方法"""
        try:
            note = self._client.get_note_by_id(
                note_id=request.note_id,
                xsec_token=request.xsec_token,
                xsec_source=request.xsec_source
            )
            return NoteResponse(**note)
        except XhsException as e:
            raise XhsError(f"获取笔记失败: {str(e)}")
```

#### 3. ClientManager (客户端管理器)

**位置**: `xhs_mcp_server/shared/client_manager.py`

**功能**: 统一管理多个小红书客户端实例

**关键特性**:
- **单例模式**: 保证全局唯一实例
- **自动清理**: 定期清理超时未使用的客户端 (1小时)
- **线程安全**: 使用 `asyncio.Lock` 保护并发访问

**核心实现**:
```python
class ClientManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._clients: Dict[str, Tuple[ApiClient, datetime]] = {}
            cls._instance._counter = 0
        return cls._instance

    async def create_client(self, request: CreateClientRequest) -> str:
        """创建新客户端"""
        async with self._lock:
            client = ApiClient(request)
            self._counter += 1
            client_id = f"client_{self._counter}"
            self._clients[client_id] = (client, datetime.now())
            return client_id

    async def get_client(self, client_id: str) -> ApiClient:
        """获取客户端实例"""
        client_tuple = self._clients.get(client_id)
        if not client_tuple:
            raise ClientNotFoundError(client_id)
        # 更新最后使用时间
        client, _ = client_tuple
        self._clients[client_id] = (client, datetime.now())
        return client

    async def _cleanup_expired(self):
        """清理超时客户端"""
        now = datetime.now()
        timeout = timedelta(hours=1)
        expired = [
            client_id
            for client_id, (_, last_used) in self._clients.items()
            if now - last_used > timeout
        ]
        for client_id in expired:
            del self._clients[client_id]
```

#### 4. MCP Server (Model Context Protocol)

**位置**: `xhs_mcp_server/mcp_server.py`

**功能**: 提供 MCP 协议接口,与 AI 工具集成

**工具列表**:
```python
# 客户端管理
create_xhs_client - 创建客户端实例

# 笔记相关
get_xhs_note - 获取笔记详情
get_xhs_note_html - 从 HTML 获取笔记详情
search_xhs_notes - 搜索笔记

# 用户相关
search_xhs_users - 搜索用户
get_xhs_user_info - 获取用户信息
get_xhs_user_notes - 获取用户笔记列表

# Feed 相关
get_xhs_feed_categories - 获取推荐流分类
get_xhs_feed - 获取推荐流内容
```

**工具调用流程**:
```python
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """MCP 工具调用处理器"""

    if name == "create_xhs_client":
        # 创建客户端
        request = CreateClientRequest(**arguments)
        client_id = await client_manager.create_client(request)
        return {"client_id": client_id}

    else:
        # 获取现有客户端
        client_id = arguments.get("client_id")
        client = await client_manager.get_client(client_id)

        # 调用对应方法
        if name == "get_xhs_note":
            request = McpNoteRequest(**arguments)
            result = await client.get_note(request)
            return result
```

## API 接口详解

### 1. 笔记相关接口

#### 获取笔记详情
```python
# 方法 1: 通过 API 获取
client.get_note_by_id(
    note_id="笔记ID",
    xsec_token="安全令牌",
    xsec_source="pc_feed"  # 来源: pc_feed/pc_search/pc_user
)

# 方法 2: 从 HTML 解析
client.get_note_by_id_from_html(
    note_id="笔记ID",
    xsec_token="安全令牌",
    xsec_source="pc_feed"
)

# 返回数据结构
{
    "note_id": "笔记ID",
    "title": "标题",
    "desc": "描述",
    "type": "normal|video",
    "user": {
        "user_id": "用户ID",
        "nickname": "昵称",
        ...
    },
    "image_list": [...],  # 图片列表
    "video": {...},       # 视频信息
    "interact_info": {
        "liked_count": "点赞数",
        "collected_count": "收藏数",
        "comment_count": "评论数",
        "share_count": "分享数"
    },
    "tag_list": [...],    # 标签列表
    "time": 1234567890,   # 发布时间戳
    "last_update_time": 1234567890
}
```

#### 搜索笔记
```python
client.get_note_by_keyword(
    keyword="搜索关键词",
    page=1,
    page_size=20,
    sort=SearchSortType.GENERAL,  # general|popularity_descending|time_descending
    note_type=SearchNoteType.ALL  # ALL(0)|VIDEO(1)|IMAGE(2)
)

# 返回数据
{
    "has_more": true,
    "items": [
        {
            "note_id": "笔记ID",
            "title": "标题",
            "cover": {...},
            "interact_info": {...}
        }
    ]
}
```

### 2. 用户相关接口

#### 获取用户信息
```python
client.get_user_info(user_id="用户ID")

# 返回数据
{
    "user_id": "用户ID",
    "nickname": "昵称",
    "avatar": "头像URL",
    "desc": "简介",
    "follows": "关注数",
    "fans": "粉丝数",
    "interaction": "获赞与收藏数"
}
```

#### 获取用户笔记
```python
client.get_user_notes(
    user_id="用户ID",
    cursor=""  # 分页游标
)

# 返回数据
{
    "cursor": "下一页游标",
    "has_more": true,
    "notes": [
        {
            "note_id": "笔记ID",
            "cover": {...},
            "interact_info": {...}
        }
    ]
}
```

#### 搜索用户
```python
client.get_user_by_keyword(
    keyword="用户名关键词",
    page=1,
    page_size=20
)
```

### 3. Feed 相关接口

#### 获取推荐流分类
```python
categories = client.get_home_feed_category()

# 返回分类列表
[
    {
        "category": "homefeed_recommend",
        "name": "推荐"
    },
    {
        "category": "homefeed.fashion_v3",
        "name": "穿搭"
    },
    ...
]
```

#### 获取推荐流
```python
from xhs.api import FeedType

client.get_home_feed(
    feed_type=FeedType.RECOMMEND  # 或其他分类
)

# 可用的 FeedType
FeedType.RECOMMEND  # 推荐
FeedType.FASION     # 穿搭
FeedType.FOOD       # 美食
FeedType.COSMETICS  # 彩妆
FeedType.MOVIE      # 影视
FeedType.CAREER     # 职场
FeedType.EMOTION    # 情感
FeedType.HOURSE     # 家居
FeedType.GAME       # 游戏
FeedType.TRAVEL     # 旅行
FeedType.FITNESS    # 健身
```

## 在你的代码中集成

### 方式 1: 直接使用 XhsClient (同步)

```python
from xhs.api import XhsClient

# 1. 创建客户端
client = XhsClient(
    cookie="你的小红书Cookie",
    user_agent="Mozilla/5.0...",  # 可选
    timeout=10,                   # 可选
    proxies=None                  # 可选
)

# 2. 获取笔记
note = client.get_note_by_id(
    note_id="笔记ID",
    xsec_token="安全令牌"
)
print(f"标题: {note['title']}")
print(f"点赞数: {note['interact_info']['liked_count']}")

# 3. 搜索笔记
results = client.get_note_by_keyword(
    keyword="Python",
    page=1,
    page_size=20
)
for item in results['items']:
    print(item['title'])

# 4. 获取用户信息
user = client.get_user_info(user_id="用户ID")
print(f"{user['nickname']}: 粉丝 {user['fans']}")

# 5. 获取推荐流
from xhs.api import FeedType
feed = client.get_home_feed(FeedType.RECOMMEND)
for item in feed['items']:
    print(item['note_card']['title'])
```

### 方式 2: 使用 ApiClient (异步)

```python
from xhs_mcp_server.shared.api import ApiClient
from xhs_mcp_server.shared.types import (
    CreateClientRequest,
    NoteRequest,
    SearchNotesRequest
)

async def main():
    # 1. 创建客户端
    request = CreateClientRequest(cookie="你的Cookie")
    async with ApiClient(request) as client:

        # 2. 获取笔记
        note_req = NoteRequest(
            client_id="",  # ApiClient 不需要
            note_id="笔记ID",
            xsec_token="令牌"
        )
        note = await client.get_note(note_req)

        # 3. 搜索笔记
        search_req = SearchNotesRequest(
            client_id="",
            keyword="Python",
            page=1,
            page_size=20
        )
        results = await client.search_notes(search_req)

# 运行
import asyncio
asyncio.run(main())
```

### 方式 3: 通过 REST API (推荐)

**启动服务**:
```bash
# 方式 1: Docker 部署
cd xhs_mcp_agent/xhs_mcp_server
docker-compose up -d

# 方式 2: 直接运行
python xhs_api.py
```

**调用示例**:
```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 创建客户端
response = requests.post(
    f"{BASE_URL}/clients",
    json={"cookie": "你的Cookie"}
)
client_id = response.json()["client_id"]

# 2. 获取笔记
response = requests.post(
    f"{BASE_URL}/clients/{client_id}/note",
    json={
        "note_id": "笔记ID",
        "xsec_token": "令牌"
    }
)
note = response.json()

# 3. 搜索笔记
response = requests.post(
    f"{BASE_URL}/clients/{client_id}/search/notes",
    json={
        "keyword": "Python",
        "page": 1,
        "page_size": 20
    }
)
results = response.json()

# 4. 获取用户信息
response = requests.post(
    f"{BASE_URL}/clients/{client_id}/user/info",
    json={"user_id": "用户ID"}
)
user = response.json()
```

### 方式 4: 通过 MCP Server (AI 集成)

适合集成到 Claude Code、Cursor 等 AI 工具中。

**配置 MCP 服务器** (在 `~/.claude/config.json`):
```json
{
  "mcpServers": {
    "xhs": {
      "command": "python",
      "args": ["/path/to/xhs_mcp_agent/xhs_mcp_server/mcp_server.py"]
    }
  }
}
```

**在 AI 中使用**:
```
# AI 会自动调用 MCP 工具

用户: "帮我搜索小红书上关于 Python 的笔记"

AI: 调用 create_xhs_client -> 获取 client_id
    调用 search_xhs_notes(client_id, keyword="Python")
    返回搜索结果
```

## 关键参数说明

### Cookie 获取方法

1. 打开小红书网页版 (xiaohongshu.com)
2. 登录账号
3. 按 F12 打开开发者工具
4. 切换到 Network 标签
5. 刷新页面
6. 找到任意请求,查看 Request Headers
7. 复制完整的 Cookie 值

**Cookie 包含的关键字段**:
- `a1`: 用户认证令牌
- `web_session`: 会话标识
- `webId`: Web 设备 ID
- `gid`: 群组 ID
- `websectiga`: 安全标识

### xsec_token 获取

`xsec_token` 是小红书的安全令牌,用于验证请求的合法性。

**获取方法**:
1. 在浏览器中访问笔记页面
2. 查看 URL 参数: `?xsec_token=xxx`
3. 或从网络请求中获取

**示例 URL**:
```
https://www.xiaohongshu.com/explore/6405a54e000000001201ee6e?
  xsec_token=ABfnJaJ1hnxfJ...&
  xsec_source=pc_feed
```

### xsec_source 说明

表示请求来源,影响返回数据的格式:
- `pc_feed`: 推荐流
- `pc_search`: 搜索结果
- `pc_user`: 用户主页

## 错误处理

### 常见错误类型

```python
from xhs.exception import (
    NeedVerifyError,  # 需要验证码 (471/461)
    IPBlockError,     # IP 被封
    SignError,        # 签名错误
    DataFetchError    # 数据获取失败
)

try:
    note = client.get_note_by_id(note_id, xsec_token)
except NeedVerifyError as e:
    print(f"需要验证: {e.verify_type}, UUID: {e.verify_uuid}")
except IPBlockError as e:
    print("IP 被封,请更换代理或等待")
except SignError as e:
    print("签名错误,请检查 Cookie")
except DataFetchError as e:
    print(f"数据获取失败: {e}")
```

### 错误码说明

| 错误码 | 含义 | 解决方法 |
|--------|------|----------|
| 471/461 | 需要验证码 | 等待或更换 IP |
| 300012 | 笔记不存在 | 检查 note_id |
| -510001 | Cookie 过期 | 重新登录获取 Cookie |
| -500 | IP 被封 | 使用代理或等待解封 |

## 高级功能

### 1. 使用代理

```python
client = XhsClient(
    cookie="你的Cookie",
    proxies={
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
)
```

### 2. 自定义 User-Agent

```python
client = XhsClient(
    cookie="你的Cookie",
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
)
```

### 3. 超时设置

```python
client = XhsClient(
    cookie="你的Cookie",
    timeout=30  # 30秒超时
)
```

### 4. 批量获取笔记

```python
def batch_get_notes(client, note_ids):
    """批量获取笔记信息"""
    notes = []
    for note_id in note_ids:
        try:
            note = client.get_note_by_id(note_id, xsec_token)
            notes.append(note)
            time.sleep(1)  # 避免请求过快
        except Exception as e:
            print(f"获取 {note_id} 失败: {e}")
    return notes
```

### 5. 爬取用户所有笔记

```python
def crawl_user_all_notes(client, user_id):
    """爬取用户的所有笔记"""
    all_notes = []
    cursor = ""

    while True:
        result = client.get_user_notes(user_id, cursor)
        all_notes.extend(result['notes'])

        if not result['has_more']:
            break
        cursor = result['cursor']
        time.sleep(1)  # 避免请求过快

    return all_notes
```

## 最佳实践

### 1. 请求频率控制

```python
import time
from functools import wraps

def rate_limit(seconds=1):
    """限制请求频率的装饰器"""
    def decorator(func):
        last_called = [0]

        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < seconds:
                time.sleep(seconds - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(seconds=2)
def get_note_safe(client, note_id, xsec_token):
    """安全的获取笔记 (限制频率)"""
    return client.get_note_by_id(note_id, xsec_token)
```

### 2. 重试机制

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def get_note_with_retry(client, note_id, xsec_token):
    """带重试的获取笔记"""
    return client.get_note_by_id(note_id, xsec_token)
```

### 3. Cookie 管理

```python
import json
from pathlib import Path

def save_cookie(cookie: str, filepath: str = "cookie.txt"):
    """保存 Cookie 到文件"""
    Path(filepath).write_text(cookie)

def load_cookie(filepath: str = "cookie.txt") -> str:
    """从文件加载 Cookie"""
    return Path(filepath).read_text().strip()

# 使用
cookie = load_cookie()
client = XhsClient(cookie=cookie)
```

### 4. 数据持久化

```python
import json

def save_notes(notes: list, filepath: str):
    """保存笔记到 JSON 文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def load_notes(filepath: str) -> list:
    """从 JSON 文件加载笔记"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
```

## 常见问题

### Q1: Cookie 多久过期?
A: 通常 7-30 天,取决于小红书的安全策略。建议定期检查和更新。

### Q2: 为什么会触发验证码?
A: 请求频率过高或 IP 异常会触发。建议:
- 控制请求频率 (每秒不超过 1 次)
- 使用代理轮换
- 模拟真实用户行为

### Q3: 如何获取大量数据?
A: 建议:
- 使用多个账号轮换
- 配置代理池
- 实现请求队列和限流
- 添加失败重试机制

### Q4: 签名 (x-s) 如何生成?
A: 项目使用内置的 `sign()` 函数生成签名,基于:
- URL 路径
- 请求数据
- Cookie 中的 a1 参数
- 时间戳

### Q5: 如何在生产环境部署?
A: 推荐使用 Docker:
```bash
cd xhs_mcp_agent/xhs_mcp_server
docker-compose up -d

# 或使用 Dockerfile 自定义部署
docker build -t xhs-api .
docker run -d -p 8000:8000 xhs-api
```

## 注意事项

⚠️ **重要提醒**:

1. **仅供学习研究**: 本项目仅用于学习和研究目的
2. **遵守服务条款**: 使用时请遵守小红书的服务条款
3. **请求频率**: 请控制请求频率,避免对服务器造成压力
4. **数据使用**: 请尊重内容创作者的权益,合理使用数据
5. **风险自负**: 使用本项目可能存在账号被封等风险

## 参考资源

- MCP 协议文档: https://modelcontextprotocol.io/
- 小红书开发者平台: https://open.xiaohongshu.com/
- FastAPI 文档: https://fastapi.tiangolo.com/
- aiohttp 文档: https://docs.aiohttp.org/

## 更新日志

- 2024-12: 初始版本
  - 实现基础 API 封装
  - 支持 MCP Server 模式
  - 支持 REST API 模式
  - 实现客户端管理器
  - 添加错误处理机制
