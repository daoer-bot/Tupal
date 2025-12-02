"""
测试改进后的热榜抓取功能
验证 next-daily-hot 风格的改进是否生效
"""
import asyncio
import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sources.baidu_source import BaiduSource
from sources.zhihu_source import ZhihuSource
from services.trending_service import TrendingService
from config import Config
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_base_source_improvements():
    """测试基础数据源的改进功能"""
    print("\n" + "="*60)
    print("测试 1: BaseSource 改进功能")
    print("="*60)
    
    # 测试百度热搜
    print("\n[测试] 百度热搜 - 请求重试机制和 User-Agent 池")
    baidu = BaiduSource()
    
    # 验证配置
    print(f"  ✓ 超时时间: {baidu.timeout}秒")
    print(f"  ✓ 最大重试: {baidu.max_retries}次")
    print(f"  ✓ 代理设置: {baidu.proxy or '未配置'}")
    
    try:
        items = await baidu.fetch_data()
        print(f"  ✓ 成功获取 {len(items)} 条数据")
        if items:
            print(f"  ✓ 第一条: {items[0].title}")
            print(f"  ✓ 热度值: {items[0].hot_value or '无'}")
    except Exception as e:
        print(f"  ✗ 获取失败: {e}")
    
    # 测试知乎热榜
    print("\n[测试] 知乎热榜 - 自定义请求头")
    zhihu = ZhihuSource()
    
    try:
        items = await zhihu.fetch_data()
        print(f"  ✓ 成功获取 {len(items)} 条数据")
        if items:
            print(f"  ✓ 第一条: {items[0].title}")
    except Exception as e:
        print(f"  ✗ 获取失败: {e}")


async def test_cache_improvements():
    """测试缓存改进功能"""
    print("\n" + "="*60)
    print("测试 2: 缓存降级策略")
    print("="*60)
    
    service = TrendingService()
    
    print(f"\n[配置] 缓存有效期: {Config.TRENDING_CACHE_TTL}秒")
    print(f"[配置] 过期数据保留: {Config.TRENDING_STALE_TTL}秒")
    
    # 第一次获取 - 应该从源获取
    print("\n[测试] 第一次获取百度热搜")
    try:
        result1 = await service.get_trending_data('baidu')
        print(f"  ✓ 获取成功")
        print(f"  ✓ 数据来源: {'缓存' if result1.get('from_cache') else '实时抓取'}")
        print(f"  ✓ 数据条数: {len(result1.get('items', []))}")
        print(f"  ✓ 是否过期: {result1.get('is_stale', False)}")
    except Exception as e:
        print(f"  ✗ 获取失败: {e}")
    
    # 第二次获取 - 应该从缓存获取
    print("\n[测试] 第二次获取百度热搜（应该使用缓存）")
    try:
        result2 = await service.get_trending_data('baidu')
        print(f"  ✓ 获取成功")
        print(f"  ✓ 数据来源: {'缓存' if result2.get('from_cache') else '实时抓取'}")
        print(f"  ✓ 是否过期: {result2.get('is_stale', False)}")
    except Exception as e:
        print(f"  ✗ 获取失败: {e}")


async def test_error_handling():
    """测试错误处理和降级策略"""
    print("\n" + "="*60)
    print("测试 3: 错误处理和降级")
    print("="*60)
    
    service = TrendingService()
    
    # 测试不存在的数据源
    print("\n[测试] 访问不存在的数据源")
    try:
        result = await service.get_trending_data('nonexistent')
        print(f"  ✗ 应该抛出异常但没有")
    except ValueError as e:
        print(f"  ✓ 正确捕获异常: {e}")
    except Exception as e:
        print(f"  ? 其他异常: {e}")


async def test_all_sources():
    """测试所有数据源"""
    print("\n" + "="*60)
    print("测试 4: 所有数据源")
    print("="*60)
    
    service = TrendingService()
    sources = service.get_sources_list()
    
    print(f"\n[信息] 已注册 {len(sources)} 个数据源")
    
    for source in sources:
        print(f"\n[测试] {source['name']} ({source['id']})")
        try:
            result = await service.get_trending_data(source['id'])
            items_count = len(result.get('items', []))
            from_cache = result.get('from_cache', False)
            is_stale = result.get('is_stale', False)
            
            status = "✓"
            if is_stale:
                status = "⚠ (使用过期缓存)"
            elif from_cache:
                status = "✓ (缓存)"
            
            print(f"  {status} 获取成功: {items_count} 条数据")
            
            if items_count > 0:
                print(f"  示例: {result['items'][0]['title'][:30]}...")
                
        except Exception as e:
            print(f"  ✗ 获取失败: {str(e)[:50]}...")


async def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("热榜抓取功能改进测试")
    print("参考 next-daily-hot-2.1.0 设计理念")
    print("="*60)
    
    # 显示当前配置
    print("\n[当前配置]")
    print(f"  缓存有效期: {Config.TRENDING_CACHE_TTL}秒")
    print(f"  过期保留期: {Config.TRENDING_STALE_TTL}秒")
    print(f"  请求超时: {Config.TRENDING_REQUEST_TIMEOUT}秒")
    print(f"  最大重试: {Config.TRENDING_MAX_RETRIES}次")
    print(f"  代理配置: {Config.TRENDING_PROXY or '未配置'}")
    print(f"  退避因子: {Config.TRENDING_BACKOFF_FACTOR}")
    
    try:
        # 运行所有测试
        await test_base_source_improvements()
        await test_cache_improvements()
        await test_error_handling()
        await test_all_sources()
        
        print("\n" + "="*60)
        print("✓ 所有测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行异步测试
    asyncio.run(main())