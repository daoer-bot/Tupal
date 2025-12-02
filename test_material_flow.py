#!/usr/bin/env python3
"""
素材中心数据流转测试脚本
测试从创建素材到在生成过程中使用的完整数据流
"""
import sys
import os
import json
import requests
import time
from datetime import datetime

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.material import MaterialType, MaterialCategory, create_material
from services.material_service import MaterialService
from storage.material_storage import MaterialStorage

# API配置
API_BASE_URL = "http://localhost:5030/api"

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def main():
    """主测试流程"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}素材中心数据流转测试{Colors.END:^60}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    material_service = MaterialService()
    test_materials = []
    passed = 0
    failed = 0
    
    # 测试1: 创建文本素材
    print(f"\n{Colors.BOLD}测试1: 创建文本素材{Colors.END}")
    try:
        material_id = material_service.create_material(
            name="测试产品介绍",
            material_type="text",
            category="视觉核心素材",
            content={"text": "这是一款创新的智能手表，具有健康监测、运动追踪等功能。"},
            tags=["产品", "智能手表"],
            description="测试用产品介绍素材"
        )
        if material_id:
            test_materials.append(material_id)
            print_success(f"文本素材创建成功，ID: {material_id}")
            passed += 1
        else:
            print_error("文本素材创建失败")
            failed += 1
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        failed += 1
    
    # 测试2: 创建图片素材
    print(f"\n{Colors.BOLD}测试2: 创建图片素材{Colors.END}")
    try:
        material_id = material_service.create_material(
            name="测试产品图片",
            material_type="image",
            category="细节展示素材",
            content={"url": "https://example.com/test-image.jpg", "description": "产品展示图"},
            tags=["图片", "产品展示"]
        )
        if material_id:
            test_materials.append(material_id)
            print_success(f"图片素材创建成功，ID: {material_id}")
            passed += 1
        else:
            print_error("图片素材创建失败")
            failed += 1
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        failed += 1
    
    # 测试3: 检索素材
    print(f"\n{Colors.BOLD}测试3: 检索素材{Colors.END}")
    try:
        result = material_service.get_materials()
        if result and 'items' in result:
            print_success(f"成功检索到 {len(result['items'])} 个素材")
            passed += 1
        else:
            print_error("检索素材失败")
            failed += 1
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        failed += 1
    
    # 测试4: 批量获取素材
    print(f"\n{Colors.BOLD}测试4: 批量获取素材{Colors.END}")
    try:
        if len(test_materials) >= 2:
            materials = material_service.get_materials_by_ids(test_materials[:2])
            if len(materials) == 2:
                print_success(f"批量获取成功，获取到 {len(materials)} 个素材")
                passed += 1
            else:
                print_error(f"批量获取结果不符合预期，期望2个，实际{len(materials)}个")
                failed += 1
        else:
            print_warning("测试素材不足，跳过此测试")
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        failed += 1
    
    # 测试5: 处理素材引用
    print(f"\n{Colors.BOLD}测试5: 处理素材引用{Colors.END}")
    try:
        base_prompt = "请介绍这款智能手表的特点"
        material_ids = test_materials[:min(2, len(test_materials))]
        
        result = material_service.process_material_references(
            material_ids=material_ids,
            base_prompt=base_prompt
        )
        
        if 'enhanced_prompt' in result and len(result['enhanced_prompt']) > len(base_prompt):
            print_success("素材引用处理成功")
            print_info(f"原始提示词长度: {len(base_prompt)}")
            print_info(f"增强提示词长度: {len(result['enhanced_prompt'])}")
            print_info(f"使用的素材数量: {len(result.get('materials_used', []))}")
            passed += 1
        else:
            print_error("素材引用处理失败")
            failed += 1
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        failed += 1
    
    # 测试6: @mention 提取
    print(f"\n{Colors.BOLD}测试6: @mention 提取{Colors.END}")
    try:
        if test_materials:
            text = f"使用 @[测试素材]({test_materials[0]}) 生成内容"
            extracted_ids = MaterialService.extract_mention_ids(text)
            
            if len(extracted_ids) == 1 and extracted_ids[0] == test_materials[0]:
                print_success(f"成功提取到素材ID: {extracted_ids[0]}")
                passed += 1
            else:
                print_error("@mention提取结果不符合预期")
                failed += 1
        else:
            print_warning("没有测试素材，跳过此测试")
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        failed += 1
    
    # 测试7: 数据持久化
    print(f"\n{Colors.BOLD}测试7: 数据持久化验证{Colors.END}")
    try:
        new_service = MaterialService()
        if test_materials:
            material = new_service.get_material(test_materials[0])
            if material:
                print_success("数据持久化验证通过")
                passed += 1
            else:
                print_error("数据持久化验证失败")
                failed += 1
        else:
            print_warning("没有测试素材，跳过此测试")
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        failed += 1
    
    # 打印摘要
    total = passed + failed
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}测试摘要{Colors.END}")
    print(f"总测试数: {total}")
    print(f"{Colors.GREEN}通过: {passed}{Colors.END}")
    print(f"{Colors.RED}失败: {failed}{Colors.END}")
    
    if total > 0:
        pass_rate = (passed / total * 100)
        print(f"通过率: {pass_rate:.1f}%")
        
        if pass_rate == 100:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 所有测试通过！{Colors.END}")
        elif pass_rate >= 80:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ 大部分测试通过{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ 测试失败较多，需要检查{Colors.END}")
    
    # 清理测试数据
    print(f"\n{Colors.BOLD}清理测试数据{Colors.END}")
    for material_id in test_materials:
        try:
            material_service.delete_material(material_id)
            print_info(f"删除素材: {material_id}")
        except Exception as e:
            print_warning(f"删除素材失败: {material_id}, 错误: {str(e)}")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)