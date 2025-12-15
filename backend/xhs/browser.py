"""
小红书浏览器自动化模块
使用 Playwright 实现扫码登录获取 Cookie
"""

import asyncio
import json
import time
from typing import Optional, Dict, Callable, Any
from dataclasses import dataclass
from enum import Enum

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class LoginStatus(Enum):
    """登录状态枚举"""
    WAITING_SCAN = "waiting_scan"  # 等待扫码
    SCANNED = "scanned"  # 已扫码，等待确认
    SUCCESS = "success"  # 登录成功
    FAILED = "failed"  # 登录失败
    TIMEOUT = "timeout"  # 超时
    CANCELLED = "cancelled"  # 已取消


@dataclass
class LoginResult:
    """登录结果"""
    status: LoginStatus
    cookie: Optional[str] = None
    qr_code_url: Optional[str] = None
    error: Optional[str] = None
    user_info: Optional[Dict] = None


class XhsBrowserLogin:
    """小红书浏览器登录类"""
    
    XHS_LOGIN_URL = "https://www.xiaohongshu.com"
    XHS_QR_LOGIN_URL = "https://www.xiaohongshu.com/login"
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 120,
        proxy: Optional[str] = None
    ):
        """
        初始化浏览器登录
        
        Args:
            headless: 是否无头模式（不显示浏览器窗口）
            timeout: 登录超时时间（秒）
            proxy: 代理地址
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright 未安装。请运行: pip install playwright && playwright install chromium"
            )
        
        self.headless = headless
        self.timeout = timeout
        self.proxy = proxy
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._cancelled = False
        self._status_callback: Optional[Callable[[LoginStatus, Any], None]] = None
    
    def set_status_callback(self, callback: Callable[[LoginStatus, Any], None]):
        """设置状态回调函数"""
        self._status_callback = callback
    
    def _notify_status(self, status: LoginStatus, data: Any = None):
        """通知状态变化"""
        if self._status_callback:
            self._status_callback(status, data)
    
    async def _init_browser(self):
        """初始化浏览器"""
        playwright = await async_playwright().start()
        
        launch_options = {
            "headless": self.headless,
        }
        
        if self.proxy:
            launch_options["proxy"] = {"server": self.proxy}
        
        self._browser = await playwright.chromium.launch(**launch_options)
        
        # 创建上下文，模拟真实浏览器
        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
        )
        
        self._page = await self._context.new_page()
    
    async def _close_browser(self):
        """关闭浏览器"""
        if self._page:
            await self._page.close()
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
    
    async def _get_cookies_string(self) -> str:
        """获取 Cookie 字符串"""
        cookies = await self._context.cookies()
        return "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    
    async def _check_login_status(self) -> bool:
        """检查是否已登录"""
        cookies = await self._context.cookies()
        cookie_names = [c['name'] for c in cookies]
        
        # 检查关键 cookie 是否存在
        required_cookies = ['a1', 'web_session']
        return all(name in cookie_names for name in required_cookies)
    
    async def _wait_for_qr_code(self) -> Optional[str]:
        """等待二维码出现并获取二维码图片 URL"""
        try:
            # 等待二维码元素出现
            qr_selector = 'img[class*="qrcode"], canvas[class*="qrcode"], .qrcode-img img'
            await self._page.wait_for_selector(qr_selector, timeout=10000)
            
            # 尝试获取二维码图片
            qr_element = await self._page.query_selector(qr_selector)
            if qr_element:
                # 如果是 img 标签，获取 src
                tag_name = await qr_element.evaluate("el => el.tagName.toLowerCase()")
                if tag_name == 'img':
                    return await qr_element.get_attribute('src')
                elif tag_name == 'canvas':
                    # 如果是 canvas，转换为 base64
                    return await qr_element.evaluate(
                        "el => el.toDataURL('image/png')"
                    )
            
            return None
        except Exception:
            return None
    
    async def _extract_qr_code_base64(self) -> Optional[str]:
        """提取二维码的 base64 数据"""
        try:
            # 尝试多种选择器
            selectors = [
                'img[class*="qrcode"]',
                'canvas[class*="qrcode"]',
                '.qrcode-img img',
                '[class*="login"] img',
                '[class*="qr"] img',
            ]
            
            for selector in selectors:
                element = await self._page.query_selector(selector)
                if element:
                    tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                    if tag_name == 'img':
                        src = await element.get_attribute('src')
                        if src and (src.startswith('data:') or src.startswith('http')):
                            return src
                    elif tag_name == 'canvas':
                        return await element.evaluate("el => el.toDataURL('image/png')")
            
            # 如果找不到二维码元素，截取登录区域的截图
            login_area = await self._page.query_selector('[class*="login"], [class*="qr"]')
            if login_area:
                screenshot = await login_area.screenshot(type='png')
                import base64
                return f"data:image/png;base64,{base64.b64encode(screenshot).decode()}"
            
            return None
        except Exception as e:
            print(f"提取二维码失败: {e}")
            return None
    
    async def login_with_qr_code(self) -> LoginResult:
        """
        使用二维码登录
        
        Returns:
            LoginResult: 登录结果
        """
        try:
            await self._init_browser()
            
            # 访问小红书首页
            await self._page.goto(self.XHS_LOGIN_URL, wait_until="networkidle")
            
            # 等待页面加载
            await asyncio.sleep(2)
            
            # 检查是否已经登录
            if await self._check_login_status():
                cookie = await self._get_cookies_string()
                return LoginResult(
                    status=LoginStatus.SUCCESS,
                    cookie=cookie
                )
            
            # 点击登录按钮（如果存在）
            try:
                login_btn = await self._page.query_selector(
                    'button:has-text("登录"), a:has-text("登录"), [class*="login"]'
                )
                if login_btn:
                    await login_btn.click()
                    await asyncio.sleep(1)
            except Exception:
                pass
            
            # 尝试切换到二维码登录
            try:
                qr_tab = await self._page.query_selector(
                    '[class*="qrcode"], button:has-text("扫码登录"), a:has-text("扫码")'
                )
                if qr_tab:
                    await qr_tab.click()
                    await asyncio.sleep(1)
            except Exception:
                pass
            
            # 获取二维码
            qr_code_data = await self._extract_qr_code_base64()
            
            if qr_code_data:
                self._notify_status(LoginStatus.WAITING_SCAN, {"qr_code": qr_code_data})
            
            # 等待登录成功
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                if self._cancelled:
                    return LoginResult(status=LoginStatus.CANCELLED)
                
                # 检查是否登录成功
                if await self._check_login_status():
                    cookie = await self._get_cookies_string()
                    self._notify_status(LoginStatus.SUCCESS)
                    return LoginResult(
                        status=LoginStatus.SUCCESS,
                        cookie=cookie
                    )
                
                # 检查页面是否跳转（登录成功的标志）
                current_url = self._page.url
                if '/explore' in current_url or '/user' in current_url:
                    cookie = await self._get_cookies_string()
                    self._notify_status(LoginStatus.SUCCESS)
                    return LoginResult(
                        status=LoginStatus.SUCCESS,
                        cookie=cookie
                    )
                
                await asyncio.sleep(1)
            
            return LoginResult(
                status=LoginStatus.TIMEOUT,
                error="登录超时，请重试"
            )
            
        except Exception as e:
            return LoginResult(
                status=LoginStatus.FAILED,
                error=str(e)
            )
        finally:
            await self._close_browser()
    
    def cancel(self):
        """取消登录"""
        self._cancelled = True


class XhsBrowserLoginManager:
    """小红书浏览器登录管理器（单例）"""
    
    _instance = None
    _login_sessions: Dict[str, XhsBrowserLogin] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def create_session(
        self,
        session_id: str,
        headless: bool = True,
        timeout: int = 120,
        proxy: Optional[str] = None
    ) -> XhsBrowserLogin:
        """创建登录会话"""
        if session_id in self._login_sessions:
            # 取消旧会话
            self._login_sessions[session_id].cancel()
        
        session = XhsBrowserLogin(
            headless=headless,
            timeout=timeout,
            proxy=proxy
        )
        self._login_sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[XhsBrowserLogin]:
        """获取登录会话"""
        return self._login_sessions.get(session_id)
    
    def cancel_session(self, session_id: str):
        """取消登录会话"""
        if session_id in self._login_sessions:
            self._login_sessions[session_id].cancel()
            del self._login_sessions[session_id]
    
    def cleanup(self):
        """清理所有会话"""
        for session in self._login_sessions.values():
            session.cancel()
        self._login_sessions.clear()


# 全局登录管理器实例
login_manager = XhsBrowserLoginManager()


async def get_cookie_by_qr_login(
    headless: bool = False,
    timeout: int = 120,
    proxy: Optional[str] = None,
    status_callback: Optional[Callable[[LoginStatus, Any], None]] = None
) -> LoginResult:
    """
    通过扫码登录获取小红书 Cookie
    
    Args:
        headless: 是否无头模式（建议设为 False 以便用户扫码）
        timeout: 超时时间（秒）
        proxy: 代理地址
        status_callback: 状态回调函数
    
    Returns:
        LoginResult: 登录结果
    """
    login = XhsBrowserLogin(
        headless=headless,
        timeout=timeout,
        proxy=proxy
    )
    
    if status_callback:
        login.set_status_callback(status_callback)
    
    return await login.login_with_qr_code()


def check_playwright_installed() -> bool:
    """检查 Playwright 是否已安装"""
    return PLAYWRIGHT_AVAILABLE