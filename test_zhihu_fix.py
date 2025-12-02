"""测试知乎热榜API修复"""
import asyncio
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sources.zhihu_hot_source import ZhihuHotSource


async def test_zhihu():
    """测试知乎热榜"""
    print("=" * 50)
    print("测试知乎热榜API")
    print("=" * 50)
    
    source = ZhihuHotSource()
    
    print(f"\n数据源信息: {source.get_source_info()}")
    print(f"请求头: {source.get_headers()}")
    print("\n开始获取数据...")
    
    try:
        items = await source.fetch_data()
        
        if items:
            print(f"\n✅ 成功获取 {len(items)} 条数据")
            print("\n前3条数据预览:")
            for i, item in enumerate(items[:3], 1):
                print(f"\n{i}. {item.title}")
                print(f"   热度: {item.hot_value}")
                print(f"   链接: {item.url}")
                if item.extra and 'pic' in item.extra:
                    print(f"   图片: {item.extra['pic'][:50]}...")
        else:
            print("\n❌ 没有获取到数据")
            
    except Exception as e:
        print(f"\n❌ 获取失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_zhihu())