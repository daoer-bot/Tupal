"""
小红书热榜数据源测试脚本
"""
import asyncio
import sys
import logging
from sources.xiaohongshu_source import XiaohongshuSource

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_xiaohongshu_source():
    """测试小红书数据源"""
    logger.info("开始测试小红书热榜数据源...")
    
    try:
        # 创建数据源实例
        source = XiaohongshuSource()
        
        # 显示数据源信息
        info = source.get_source_info()
        logger.info(f"数据源信息: {info}")
        
        # 获取热榜数据
        logger.info("正在获取热榜数据...")
        items = await source.fetch_data()
        
        # 显示结果
        logger.info(f"成功获取 {len(items)} 条热榜数据")
        
        if items:
            logger.info("\n前5条热榜数据:")
            for i, item in enumerate(items[:5], 1):
                logger.info(f"\n{i}. {item.title}")
                logger.info(f"   热度: {item.hot_value}")
                logger.info(f"   链接: {item.url}")
                if item.extra:
                    logger.info(f"   额外信息: {item.extra}")
        else:
            logger.warning("未获取到任何数据")
        
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(test_xiaohongshu_source())
    
    if success:
        logger.info("\n✅ 测试通过！小红书热榜数据源工作正常。")
        sys.exit(0)
    else:
        logger.error("\n❌ 测试失败！请检查错误信息。")
        sys.exit(1)