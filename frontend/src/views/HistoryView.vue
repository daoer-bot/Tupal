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
      <div v-for="item in historyList" :key="item.task_id" class="history-card">
        <div class="card-preview">
          <div class="preview-image" :style="getPreviewStyle(item)">
            <div class="preview-overlay">
              <div class="overlay-buttons">
                <button class="btn btn-secondary btn-sm" @click="editOutline(item)">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon-svg-sm">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                  </svg>
                  编辑大纲
                </button>
                <button class="btn btn-primary btn-sm" @click="viewDetails(item)">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon-svg-sm">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  查看详情
                </button>
                <button
                  class="btn btn-danger btn-sm"
                  @click.stop="handleDelete(item)"
                  :disabled="deleting.has(item.task_id || item.id)"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon-svg-sm">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                  </svg>
                  {{ deleting.has(item.task_id || item.id) ? '删除中...' : '删除' }}
                </button>
              </div>
            </div>
          </div>
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

const editOutline = (item: any) => {
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
  
  // 跳转到大纲编辑页面
  router.push('/generator')
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
}

.history-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
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

.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.history-card:hover .preview-overlay {
  opacity: 1;
}

.overlay-buttons {
  display: flex;
  gap: 0.75rem;
  flex-direction: column;
}

.overlay-buttons .btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
  min-width: 120px;
  justify-content: center;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.icon-svg-sm {
  width: 1rem;
  height: 1rem;
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