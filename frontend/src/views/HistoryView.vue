<template>
  <div class="history">
    <div class="header">
      <h2>历史记录</h2>
      <div class="search-bar">
        <input
          v-model="searchKeyword"
          @input="handleSearch"
          type="text"
          placeholder="搜索主题..."
          class="search-input"
        />
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="loadHistory" class="btn btn-primary">重试</button>
    </div>
    
    <!-- 空状态 -->
    <div v-else-if="historyList.length === 0" class="empty-state">
      <div class="icon">📝</div>
      <p>{{ searchKeyword ? '没有找到匹配的记录' : '暂无历史记录' }}</p>
      <button v-if="!searchKeyword" @click="goHome" class="btn btn-primary">
        开始创作
      </button>
    </div>
    
    <!-- 历史记录列表 -->
    <div v-else class="history-list">
      <div
        v-for="item in historyList"
        :key="item.id"
        class="history-item"
        @click="viewDetail(item.id)"
      >
        <div class="thumbnail">
          <img
            v-if="item.thumbnail"
            :src="item.thumbnail"
            :alt="item.topic"
          />
          <div v-else class="placeholder">
            <span>🖼️</span>
          </div>
        </div>
        
        <div class="info">
          <h3>{{ item.topic }}</h3>
          <div class="meta">
            <span class="pages">📄 {{ item.total_pages }} 页</span>
            <span class="date">{{ formatDate(item.created_at) }}</span>
          </div>
          <div class="status" :class="item.status">
            {{ getStatusText(item.status) }}
          </div>
        </div>
        
        <div class="actions" @click.stop>
          <button @click="viewDetail(item.id)" class="btn btn-sm btn-secondary">
            查看
          </button>
          <button @click="deleteItem(item.id)" class="btn btn-sm btn-danger">
            删除
          </button>
        </div>
      </div>
    </div>
    
    <!-- 分页 -->
    <div v-if="pagination.total_pages > 1" class="pagination">
      <button
        @click="changePage(pagination.page - 1)"
        :disabled="pagination.page === 1"
        class="btn btn-secondary"
      >
        上一页
      </button>
      
      <span class="page-info">
        第 {{ pagination.page }} / {{ pagination.total_pages }} 页
      </span>
      
      <button
        @click="changePage(pagination.page + 1)"
        :disabled="!pagination.has_more"
        class="btn btn-secondary"
      >
        下一页
      </button>
    </div>
    
    <!-- 详情弹窗 -->
    <div v-if="showDetail && currentDetail" class="modal" @click="closeDetail">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ currentDetail.topic }}</h3>
          <button @click="closeDetail" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="detail-meta">
            <div class="meta-item">
              <span class="label">创建时间：</span>
              <span>{{ formatDateTime(currentDetail.created_at) }}</span>
            </div>
            <div class="meta-item">
              <span class="label">页面数量：</span>
              <span>{{ currentDetail.total_pages }} 页</span>
            </div>
            <div class="meta-item">
              <span class="label">生成器：</span>
              <span>{{ currentDetail.generator_type }}</span>
            </div>
          </div>
          
          <div class="pages-grid">
            <div
              v-for="page in currentDetail.pages"
              :key="page.page_number"
              class="page-card"
            >
              <div v-if="page.image_url" class="page-image">
                <img :src="page.image_url" :alt="`页面 ${page.page_number}`" />
              </div>
              <div class="page-info">
                <div class="page-number">页面 {{ page.page_number }}</div>
                <h4>{{ page.title }}</h4>
                <p>{{ page.description }}</p>
                <a
                  v-if="page.image_url"
                  :href="page.image_url"
                  target="_blank"
                  class="download-link"
                >
                  下载
                </a>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="downloadAll" class="btn btn-primary">
            下载全部
          </button>
          <button @click="reEdit" class="btn btn-secondary">
            重新编辑
          </button>
          <button @click="closeDetail" class="btn btn-secondary">
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHistory, getHistoryItem, deleteHistory } from '../services/api'

const router = useRouter()

// 状态
const loading = ref(false)
const error = ref('')
const searchKeyword = ref('')
const historyList = ref<any[]>([])
const pagination = ref({
  page: 1,
  page_size: 12,
  total: 0,
  total_pages: 0,
  has_more: false
})

// 详情相关
const showDetail = ref(false)
const currentDetail = ref<any>(null)

// 加载历史记录
const loadHistory = async (page: number = 1) => {
  loading.value = true
  error.value = ''
  
  try {
    const params: any = {
      page,
      page_size: pagination.value.page_size
    }
    
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    
    const response = await getHistory() as any
    
    if (response.success && response.data) {
      historyList.value = response.data.items || []
      pagination.value = response.data.pagination || pagination.value
    } else {
      error.value = (response as any).error || '加载失败'
    }
  } catch (err: any) {
    error.value = err.message || '加载失败，请重试'
    console.error('Load history error:', err)
  } finally {
    loading.value = false
  }
}

// 搜索
let searchTimeout: any = null
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadHistory(1)
  }, 500)
}

// 查看详情
const viewDetail = async (historyId: string) => {
  try {
    const response = await getHistoryItem(historyId)
    
    if (response.success) {
      currentDetail.value = response.data
      showDetail.value = true
    } else {
      alert('加载详情失败')
    }
  } catch (err) {
    console.error('View detail error:', err)
    alert('加载详情失败')
  }
}

// 关闭详情
const closeDetail = () => {
  showDetail.value = false
  currentDetail.value = null
}

// 删除记录
const deleteItem = async (historyId: string) => {
  if (!confirm('确定要删除这条记录吗？')) {
    return
  }
  
  try {
    const response = await deleteHistory(historyId)
    
    if (response.success) {
      // 重新加载列表
      loadHistory(pagination.value.page)
    } else {
      alert('删除失败')
    }
  } catch (err) {
    console.error('Delete error:', err)
    alert('删除失败')
  }
}

// 切换页码
const changePage = (page: number) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    loadHistory(page)
  }
}

// 下载全部
const downloadAll = () => {
  if (!currentDetail.value) return
  
  currentDetail.value.pages.forEach((page: any) => {
    if (page.image_url) {
      const link = document.createElement('a')
      link.href = page.image_url
      link.download = `page_${page.page_number}.jpg`
      link.click()
    }
  })
}

// 重新编辑
const reEdit = () => {
  // TODO: 实现重新编辑功能
  alert('重新编辑功能开发中...')
}

// 前往首页
const goHome = () => {
  router.push('/')
}

// 格式化日期
const formatDate = (dateStr: string) => {
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch {
    return dateStr
  }
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateStr
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    completed: '已完成',
    pending: '进行中',
    failed: '失败'
  }
  return statusMap[status] || status
}

// 挂载时加载数据
onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* 头部 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header h2 {
  margin: 0;
  color: #333;
}

.search-bar {
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 25px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
}

/* 加载/错误/空状态 */
.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
}

.spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto 1rem;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state .icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state p {
  color: #666;
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}

/* 历史记录列表 */
.history-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.history-item {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.history-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.thumbnail {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: #f5f5f5;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  color: #ccc;
}

.info {
  padding: 1rem;
}

.info h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #666;
}

.status {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status.completed {
  background: #d1fae5;
  color: #065f46;
}

.status.pending {
  background: #fef3c7;
  color: #92400e;
}

.status.failed {
  background: #fee2e2;
  color: #991b1b;
}

.actions {
  display: flex;
  gap: 0.5rem;
  padding: 0 1rem 1rem 1rem;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.page-info {
  color: #666;
  font-size: 0.9rem;
}

/* 模态框 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #666;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 32px;
  height: 32px;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.detail-meta {
  margin-bottom: 2rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
}

.meta-item {
  margin-bottom: 0.5rem;
  color: #666;
}

.meta-item:last-child {
  margin-bottom: 0;
}

.meta-item .label {
  font-weight: 500;
  color: #333;
}

.pages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.page-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.page-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: #f5f5f5;
}

.page-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.page-info {
  padding: 1rem;
}

.page-number {
  display: inline-block;
  background: #667eea;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  margin-bottom: 0.5rem;
}

.page-info h4 {
  margin: 0.5rem 0;
  color: #333;
  font-size: 0.9rem;
}

.page-info p {
  margin: 0 0 0.75rem 0;
  color: #666;
  font-size: 0.8rem;
  line-height: 1.4;
}

.download-link {
  color: #667eea;
  text-decoration: none;
  font-size: 0.875rem;
}

.download-link:hover {
  text-decoration: underline;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1.5rem;
  border-top: 1px solid #e0e0e0;
}

/* 按钮样式 */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-secondary:hover:not(:disabled) {
  background: #f5f7ff;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

/* 响应式  */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-bar {
    max-width: 100%;
  }
  
  .history-list {
    grid-template-columns: 1fr;
  }
  
  .pages-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>