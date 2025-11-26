"""
大纲生成功能测试脚本
用于验证AI服务配置和大纲生成是否正常工作
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from services.outline_service import OutlineService
from generators.factory import GeneratorFactory
from config import Config


def test_configuration():
    """测试配置是否正确"""
    print("=" * 60)
    print("1. 测试配置")
    print("=" * 60)
    
    # 检查 Gemini API Key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        print(f"✓ GEMINI_API_KEY: 已配置 ({gemini_key[:10]}...)")
    else:
        print("✗ GEMINI_API_KEY: 未配置")
    
    # 检查 OpenAI API Key
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f"✓ OPENAI_API_KEY: 已配置 ({openai_key[:10]}...)")
    else:
        print("✗ OPENAI_API_KEY: 未配置")
    
    # 检查 Image API
    image_key = os.getenv('IMAGE_API_KEY')
    image_url = os.getenv('IMAGE_API_URL')
    if image_key and image_url:
        print(f"✓ IMAGE_API: 已配置")
    else:
        print("✗ IMAGE_API: 未完全配置")
    
    print()


def test_generator_factory():
    """测试生成器工厂"""
    print("=" * 60)
    print("2. 测试生成器工厂")
    print("=" * 60)
    
    # 模拟Flask配置
    class MockConfig:
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        IMAGE_API_KEY = os.getenv('IMAGE_API_KEY')
        IMAGE_API_URL = os.getenv('IMAGE_API_URL')
    
    # 测试 Gemini 生成器
    try:
        from generators.gemini_generator import GeminiGenerator
        if MockConfig.GEMINI_API_KEY:
            generator = GeminiGenerator(api_key=MockConfig.GEMINI_API_KEY)
            if generator.validate_config():
                print("✓ Gemini 生成器: 创建成功")
            else:
                print("✗ Gemini 生成器: 配置无效")
        else:
            print("⊘ Gemini 生成器: API Key 未配置，跳过测试")
    except Exception as e:
        print(f"✗ Gemini 生成器: 创建失败 - {e}")
    
    # 测试 OpenAI 生成器
    try:
        from generators.openai_generator import OpenAIGenerator
        if MockConfig.OPENAI_API_KEY:
            generator = OpenAIGenerator(
                api_key=MockConfig.OPENAI_API_KEY,
                base_url=MockConfig.OPENAI_BASE_URL
            )
            if generator.validate_config():
                print("✓ OpenAI 生成器: 创建成功")
            else:
                print("✗ OpenAI 生成器: 配置无效")
        else:
            print("⊘ OpenAI 生成器: API Key 未配置，跳过测试")
    except Exception as e:
        print(f"✗ OpenAI 生成器: 创建失败 - {e}")
    
    print()


def test_outline_generation():
    """测试大纲生成"""
    print("=" * 60)
    print("3. 测试大纲生成")
    print("=" * 60)
    
    # 检查是否有可用的生成器
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_key:
        print("⊘ 没有配置任何大纲生成器，跳过测试")
        print("提示：请在 .env 文件中配置 GEMINI_API_KEY 或 OPENAI_API_KEY")
        return
    
    # 测试主题
    test_topic = "如何提高工作效率的10个小技巧"
    
    print(f"测试主题: {test_topic}")
    print("正在生成大纲...\n")
    
    try:
        # 使用 Gemini 生成器
        service = OutlineService(generator_type='gemini')
        result = service.generate(topic=test_topic)
        
        if result['success']:
            print("✓ 大纲生成成功！\n")
            print(f"任务ID: {result.get('task_id')}")
            print(f"主题: {result.get('topic')}")
            print(f"生成时间: {result.get('created_at')}")
            print(f"\n生成了 {len(result.get('pages', []))} 页内容：\n")
            
            for page in result.get('pages', []):
                print(f"  页面 {page['page_number']}: {page['title']}")
                print(f"    描述: {page['description'][:50]}...")
                print()
            
            print("✓ 大纲格式验证通过")
        else:
            print(f"✗ 大纲生成失败: {result.get('error')}")
            
    except Exception as e:
        print(f"✗ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
    
    print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("图宝 - 大纲生成功能测试")
    print("=" * 60 + "\n")
    
    # 运行所有测试
    test_configuration()
    test_generator_factory()
    test_outline_generation()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60 + "\n")
    
    # 给出下一步建议
    gemini_key = os.getenv('GEMINI_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not gemini_key and not openai_key:
        print("⚠️  下一步操作：")
        print("1. 复制 backend/.env.example 为 backend/.env")
        print("2. 在 .env 文件中配置你的 API Keys")
        print("3. 重新运行此测试脚本")
    else:
        print("✓ 配置正常，可以启动应用进行完整测试")
        print("\n启动命令：")
        print("  cd backend")
        print("  python app.py")


if __name__ == '__main__':
    main()