<template>
  <div class="history-container">
    <div class="page-header">
      <h2 class="page-title">历史记录</h2>
      <div class="header-actions">
        <button class="btn btn-secondary refresh-btn" @click="loadHistory" :disabled="loading">
          <span class="icon" :class="{ 'spinning': loading }">🔄</span>
          刷新
        </button>
      </div>
    </div>

    <div v-if="loading && historyList.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="historyList.length === 0" class="empty-state">
      <div class="empty-icon">📂</div>
      <h3>暂无历史记录</h3>
      <p>你生成的图文内容将显示在这里</p>
      <router-link to="/" class="btn btn-primary">去创作</router-link>
    </div>

    <div v-else class="history-grid">
      <div v-for="item in historyList" :key="item.task_id" class="history-card" @click="viewDetails(item)">
        <div class="card-preview">
          <div class="preview-image" :style="getPreviewStyle(item)"></div>
          
          <!-- 左上角删除按钮 -->
          <button
            class="delete-btn"
            @click.stop="handleDelete(item)"
            :disabled="deleting.has(item.task_id || item.id)"
            :title="deleting.has(item.task_id || item.id) ? '删除中...' : '删除'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          
          <div class="status-badge" :class="item.status">
            {{ getStatusText(item.status) }}
          </div>
        </div>
        
        <div class="card-content">
          <h3 class="card-title" :title="item.topic">{{ item.topic }}</h3>
          <div class="card-meta">
            <span class="meta-item">
              <span class="icon">📅</span>
              {{ formatDate(item.created_at) }}
            </span>
            <span class="meta-item">
              <span class="icon">📄</span>
              {{ item.pages?.length || 0 }} 页
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHistory, deleteHistory } from '../services/api'
import { useAppStore } from '../store'

const router = useRouter()
const store = useAppStore()
const historyList = ref<any[]>([])
const loading = ref(false)
const deleting = ref<Set<string>>(new Set())

const loadHistory = async () => {
  loading.value = true
  try {
    const response = await getHistory()
    if (response.success && response.data) {
      // 修复：正确获取历史记录列表
      historyList.value = response.data.items || response.data || []
    } else {
      historyList.value = []
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
    historyList.value = []
  } finally {
    loading.value = false
  }
}

const viewDetails = (item: any) => {
  // 构建符合 Outline 接口的数据结构
  const outline = {
    task_id: item.task_id || item.id,
    topic: item.topic,
    pages: item.pages || []
  }
  store.setOutline(outline)
  
  // 如果有参考图片，也设置到 store
  if (item.reference_image) {
    store.setReferenceImage(item.reference_image)
  }
  
  // 跳转到结果页面查看已完成的内容
  router.push('/result')
}

const getPreviewStyle = (item: any) => {
  // 尝试获取第一张图片的 URL
  const firstImage = item.pages?.[0]?.image_url
  if (firstImage) {
    return {
      backgroundImage: `url(${firstImage})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  // 如果没有图片，使用渐变背景
  return {
    background: 'linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%)'
  }
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    'completed': '已完成',
    'failed': '失败',
    'pending': '进行中'
  }
  return map[status] || status
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleDelete = async (item: any) => {
  const historyId = item.task_id || item.id
  
  if (!confirm(`确定要删除"${item.topic}"吗？此操作无法撤销。`)) {
    return
  }
  
  deleting.value.add(historyId)
  
  try {
    const response = await deleteHistory(historyId)
    if (response.success) {
      // 从列表中移除
      historyList.value = historyList.value.filter(h =>
        (h.task_id || h.id) !== historyId
      )
    } else {
      alert('删除失败，请重试')
    }
  } catch (error: any) {
    console.error('删除历史记录失败:', error)
    alert('删除失败：' + (error?.message || '请重试'))
  } finally {
    deleting.value.delete(historyId)
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.refresh-btn .icon {
  display: inline-block;
  transition: transform 0.5s;
}

.refresh-btn .icon.spinning {
  animation: spin 1s linear infinite;
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.history-card {
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s;
  border: 1px solid var(--border-color);
  cursor: pointer;
}

.history-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.history-card:active {
  transform: translateY(-2px);
}

.card-preview {
  height: 180px;
  position: relative;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  transition: transform 0.5s;
}

.history-card:hover .preview-image {
  transform: scale(1.05);
}

/* 左上角删除按钮 */
.delete-btn {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  opacity: 0;
  z-index: 10;
}

.history-card:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover:not(:disabled) {
  background: #fee2e2;
  transform: scale(1.1);
}

.delete-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.delete-btn svg {
  width: 1.1rem;
  height: 1.1rem;
  color: #ef4444;
  transition: color 0.3s;
}

.delete-btn:hover:not(:disabled) svg {
  color: #dc2626;
}

.status-badge {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-badge.completed {
  color: #10b981;
}

.status-badge.failed {
  color: #ef4444;
}

.status-badge.pending {
  color: #f59e0b;
}

.card-content {
  padding: 1.25rem;
}

.card-title {
  margin: 0 0 0.75rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 1rem;
  border: 2px dashed var(--border-color);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0 0 0.5rem;
  color: var(--text-primary);
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.loading-state {
  text-align: center;
  padding: 4rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: var(--primary-color);
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>