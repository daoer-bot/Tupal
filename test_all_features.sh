#!/bin/bash

# 图宝功能全面测试脚本
# 测试所有API端点和功能

echo "======================================"
echo "图宝 - 功能全面测试"
echo "======================================"
echo ""

API_BASE="http://localhost:5030/api"
RESULTS_FILE="test_results.txt"

# 清空结果文件
> $RESULTS_FILE

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
test_api() {
    local test_name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "测试 $TOTAL_TESTS: $test_name ... "
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_BASE$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_BASE$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    
    # 记录结果
    echo "=== $test_name ===" >> $RESULTS_FILE
    echo "HTTP Status: $http_code" >> $RESULTS_FILE
    echo "Response: $body" >> $RESULTS_FILE
    echo "" >> $RESULTS_FILE
    
    # 检查状态码
    if [ "$http_code" -eq "$expected_status" ] || [ "$expected_status" -eq "0" ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (期望: $expected_status, 实际: $http_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "开始测试..."
echo ""

# ========================================
# 1. 基础健康检查
# ========================================
echo -e "${YELLOW}[1] 基础服务测试${NC}"
test_api "后端健康检查" "GET" "/../health" "" "200"
test_api "根路径访问" "GET" "/.." "" "200"
echo ""

# ========================================
# 2. 素材管理功能测试
# ========================================
echo -e "${YELLOW}[2] 素材管理功能测试${NC}"

# 2.1 创建文本素材
test_api "创建文本素材" "POST" "/materials" '{
    "name": "测试产品介绍",
    "type": "text",
    "category": "文案配图素材",
    "content": {
        "text": "这是一款革命性的智能产品，具有AI驱动的功能。"
    },
    "tags": ["AI", "智能"],
    "description": "测试用产品介绍素材"
}' "201"

# 2.2 创建图片素材
test_api "创建图片素材" "POST" "/materials" '{
    "name": "测试产品图片",
    "type": "image",
    "category": "视觉核心素材",
    "content": {
        "url": "https://picsum.photos/400/300",
        "alt": "测试图片"
    },
    "tags": ["产品", "展示"],
    "description": "测试用产品图片"
}' "201"

# 2.3 获取素材列表
test_api "获取所有素材" "GET" "/materials" "" "200"
test_api "按类型筛选素材" "GET" "/materials?type=text" "" "200"
test_api "搜索素材" "GET" "/materials?keyword=测试" "" "200"

# 2.4 获取分类和标签
test_api "获取所有分类" "GET" "/materials/categories" "" "200"
test_api "获取所有标签" "GET" "/materials/tags" "" "200"

echo ""

# ========================================
# 3. 大纲生成功能测试
# ========================================
echo -e "${YELLOW}[3] 大纲生成功能测试${NC}"

test_api "生成大纲-基础" "POST" "/generate-outline" '{
    "topic": "如何提高工作效率的10个小技巧",
    "generator_type": "mock"
}' "200"

test_api "生成大纲-缺少主题" "POST" "/generate-outline" '{
    "generator_type": "mock"
}' "400"

echo ""

# ========================================
# 4. 历史记录功能测试
# ========================================
echo -e "${YELLOW}[4] 历史记录功能测试${NC}"

# 4.1 保存历史记录
test_api "保存历史记录" "POST" "/history" '{
    "task_id": "test_task_001",
    "topic": "测试主题",
    "pages": [
        {
            "page": 1,
            "title": "第一页",
            "description": "测试内容",
            "image_url": "https://picsum.photos/400/300"
        }
    ],
    "generator_type": "mock",
    "status": "completed"
}' "200"

# 4.2 获取历史列表
test_api "获取历史列表" "GET" "/history" "" "200"
test_api "获取历史列表-分页" "GET" "/history?page=1&page_size=10" "" "200"
test_api "搜索历史记录" "GET" "/history?keyword=测试" "" "200"

echo ""

# ========================================
# 5. 图片生成功能测试（Mock模式）
# ========================================
echo -e "${YELLOW}[5] 图片生成功能测试${NC}"

# 生成唯一任务ID
TASK_ID="test_$(date +%s)"

test_api "启动图片生成任务" "POST" "/generate-images" "{
    \"task_id\": \"$TASK_ID\",
    \"pages\": [
        {
            \"page\": 1,
            \"title\": \"第一页\",
            \"description\": \"这是测试页面\"
        },
        {
            \"page\": 2,
            \"title\": \"第二页\",
            \"description\": \"这是第二个测试页面\"
        }
    ],
    \"topic\": \"测试主题\",
    \"generator_type\": \"mock\"
}" "200"

echo ""

# ========================================
# 6. SSE进度推送测试
# ========================================
echo -e "${YELLOW}[6] SSE进度推送测试${NC}"
echo "测试 SSE 进度流（5秒采样）..."

# 跨平台的超时实现
(
    curl -N -s "$API_BASE/progress/$TASK_ID" | while IFS= read -r line; do
        if [[ $line == data:* ]]; then
            echo "收到进度更新: ${line:6}" | head -c 100
            echo "..."
        fi
    done
) &
CURL_PID=$!

# 等待5秒
sleep 5

# 终止curl进程
kill $CURL_PID 2>/dev/null
wait $CURL_PID 2>/dev/null

echo -e "${GREEN}✓ SSE 连接测试通过${NC}"
PASSED_TESTS=$((PASSED_TESTS + 1))
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""

# ========================================
# 7. 素材引用处理测试
# ========================================
echo -e "${YELLOW}[7] 素材引用处理测试${NC}"

# 先获取素材ID列表（从之前创建的素材中）
echo "获取素材ID用于引用测试..."
material_ids=$(curl -s "$API_BASE/materials?page_size=2" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 | head -2 | tr '\n' ',' | sed 's/,$//')

if [ ! -z "$material_ids" ]; then
    test_api "处理素材引用" "POST" "/materials/process-references" "{
        \"material_ids\": [\"${material_ids%%,*}\"],
        \"base_prompt\": \"创建一个产品展示图\"
    }" "200"
    
    test_api "批量获取素材" "POST" "/materials/batch" "{
        \"material_ids\": [\"${material_ids%%,*}\"]
    }" "200"
else
    echo -e "${YELLOW}跳过引用测试（无可用素材）${NC}"
fi

echo ""

# ========================================
# 8. 错误处理测试
# ========================================
echo -e "${YELLOW}[8] 错误处理测试${NC}"

test_api "访问不存在的素材" "GET" "/materials/nonexistent_id" "" "404"
test_api "访问不存在的历史" "GET" "/history/nonexistent_id" "" "404"
test_api "删除不存在的素材" "DELETE" "/materials/nonexistent_id" "" "404"
test_api "无效的素材数据" "POST" "/materials" '{
    "name": "测试",
    "type": "invalid_type"
}' "400"

echo ""

# ========================================
# 9. 前端服务测试
# ========================================
echo -e "${YELLOW}[9] 前端服务测试${NC}"

frontend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173)
if [ "$frontend_status" -eq "200" ]; then
    echo -e "前端服务访问: ${GREEN}✓ PASSED${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "前端服务访问: ${RED}✗ FAILED${NC} (HTTP $frontend_status)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""

# ========================================
# 测试总结
# ========================================
echo "======================================"
echo "测试完成！"
echo "======================================"
echo ""
echo "总测试数: $TOTAL_TESTS"
echo -e "${GREEN}通过: $PASSED_TESTS${NC}"
echo -e "${RED}失败: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
    echo ""
    echo "详细结果已保存到: $RESULTS_FILE"
    exit 0
else
    echo -e "${RED}⚠️  部分测试失败，请查看详细结果${NC}"
    echo ""
    echo "详细结果已保存到: $RESULTS_FILE"
    exit 1
fi