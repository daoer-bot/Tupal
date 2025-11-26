"""测试 OpenAI 客户端创建"""
import sys
import traceback

try:
    from openai import OpenAI
    
    print("1. OpenAI 模块导入成功")
    print(f"   模块位置: {OpenAI.__module__}")
    
    api_key = "sk-test"
    base_url = "https://api.kkyyxx.xyz/v1"
    
    print(f"\n2. 尝试创建 OpenAI 客户端...")
    print(f"   api_key: {api_key[:10]}...")
    print(f"   base_url: {base_url}")
    
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    print("\n3. ✓ OpenAI 客户端创建成功!")
    print(f"   客户端类型: {type(client)}")
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    print("\n完整堆栈跟踪:")
    traceback.print_exc()