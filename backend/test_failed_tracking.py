"""
测试失败页面追踪功能
"""
import sys
import time
from services.progress_service import ProgressService
from services.image_service import ImageService

def test_failed_tracking():
    """测试失败页面追踪"""
    print("=" * 60)
    print("测试失败页面追踪功能")
    print("=" * 60)
    
    # 初始化服务
    progress_service = ProgressService()
    image_service = ImageService(generator_type='mock')
    
    # 创建测试任务
    task_id = "test_failed_tracking"
    
    print(f"\n1. 创建测试任务: {task_id}")
    progress_service.create_task(
        task_id=task_id,
        total_pages=5,
        topic="测试失败追踪"
    )
    
    # 启动任务
    print("2. 启动任务")
    progress_service.start_task(task_id)
    
    # 模拟成功的页面
    print("\n3. 模拟成功生成页面 1-3")
    for i in range(1, 4):
        progress_service.update_progress(
            task_id=task_id,
            current_page=i,
            image_url=f"https://example.com/image_{i}.jpg",
            message=f"第 {i} 页生成完成"
        )
        print(f"   ✅ 页面 {i} 生成成功")
        time.sleep(0.2)
    
    # 模拟失败的页面
    print("\n4. 模拟失败页面 4-5")
    
    # 页面4：API错误
    progress_service.record_failed_page(
        task_id=task_id,
        page_number=4,
        error="API请求超时: Connection timeout after 30s"
    )
    print("   ❌ 页面 4 生成失败: API请求超时")
    
    # 页面5：参数错误
    progress_service.record_failed_page(
        task_id=task_id,
        page_number=5,
        error="参数验证失败: Invalid prompt format"
    )
    print("   ❌ 页面 5 生成失败: 参数验证失败")
    
    # 完成任务
    print("\n5. 完成任务")
    progress_service.complete_task(
        task_id=task_id,
        message="生成完成，成功 3/5 页"
    )
    
    # 获取最终进度
    print("\n6. 查看最终进度")
    final_progress = progress_service.get_progress(task_id)
    
    if final_progress:
        print("\n" + "=" * 60)
        print("最终任务状态")
        print("=" * 60)
        print(f"任务ID: {final_progress['task_id']}")
        print(f"状态: {final_progress['status']}")
        print(f"进度: {final_progress['progress']}%")
        print(f"总页数: {final_progress['total_pages']}")
        print(f"完成页数: {final_progress['completed_pages']}")
        print(f"消息: {final_progress['message']}")
        
        print(f"\n成功的图片 ({len(final_progress['images'])} 张):")
        for img in final_progress['images']:
            print(f"  ✅ 页面 {img['page_number']}: {img['url']}")
        
        print(f"\n失败的页面 ({len(final_progress['failed_pages'])} 个):")
        for failed in final_progress['failed_pages']:
            print(f"  ❌ 页面 {failed['page_number']}")
            print(f"     错误: {failed['error']}")
            print(f"     时间: {failed['failed_at']}")
        
        print("\n" + "=" * 60)
        
        # 验证结果
        print("\n7. 验证测试结果")
        success = True
        
        if len(final_progress['images']) != 3:
            print("   ❌ 错误: 成功图片数量不正确")
            success = False
        else:
            print("   ✅ 成功图片数量正确 (3张)")
        
        if len(final_progress['failed_pages']) != 2:
            print("   ❌ 错误: 失败页面数量不正确")
            success = False
        else:
            print("   ✅ 失败页面数量正确 (2个)")
        
        if 'failed_pages' not in final_progress:
            print("   ❌ 错误: 缺少 failed_pages 字段")
            success = False
        else:
            print("   ✅ failed_pages 字段存在")
        
        # 检查失败页面的详细信息
        for failed in final_progress['failed_pages']:
            if 'page_number' not in failed or 'error' not in failed or 'failed_at' not in failed:
                print(f"   ❌ 错误: 失败页面缺少必需字段")
                success = False
            else:
                print(f"   ✅ 失败页面 {failed['page_number']} 包含完整信息")
        
        print("\n" + "=" * 60)
        if success:
            print("✅ 测试通过！失败追踪功能正常工作")
        else:
            print("❌ 测试失败！请检查代码")
        print("=" * 60)
        
        return success
    else:
        print("❌ 错误: 无法获取任务进度")
        return False

if __name__ == '__main__':
    try:
        success = test_failed_tracking()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)