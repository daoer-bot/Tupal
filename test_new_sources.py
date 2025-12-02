"""
测试新添加的热榜数据源
"""
import asyncio
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sources.toutiao_source import ToutiaoSource
from sources.hupu_source import HupuSource
from sources.tieba_source import TiebaSource
from sources.kr36_source import Kr36Source


async def test_source(source, source_name):
    """测试单个数据源"""
    print(f"\n{'='*60}")
    print(f"测试 {source_name}")
    print(f"{'='*60}")
    
    try:
        items = await source.fetch_data()
        
        if items:
            print(f"✅ 成功获取 {len(items)} 条数据")
            print(f"\n前3条数据预览：")
            for i, item in enumerate(items[:3], 1):
                print(f"\n{i}. {item.title}")
                print(f"   URL: {item.url}")
                if item.hot_value:
                    print(f"   热度: {item.hot_value}")
                if item.extra:
                    print(f"   额外信息: {item.extra}")
        else:
            print(f"⚠️  获取到0条数据")
            
    except Exception as e:
        print(f"❌ 获取失败: {str(e)}")


async def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("开始测试新添加的4个热榜数据源")
    print("="*60)
    
    # 创建数据源实例
    sources = [
        (ToutiaoSource(), "今日头条"),
        (HupuSource(), "虎扑热榜"),
        (TiebaSource(), "贴吧热榜"),
        (Kr36Source(), "36氪")
    ]
    
    # 测试每个数据源
    for source, name in sources:
        await test_source(source, name)
        await asyncio.sleep(1)  # 避免请求过快
    
    print(f"\n{'='*60}")
    print("所有测试完成！")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())