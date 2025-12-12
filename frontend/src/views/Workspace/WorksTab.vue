<template>
  <div class="works-container">
    <!-- 数据概览卡片 -->
    <div class="stats-grid">
      <div class="stat-card glass-panel">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ historyList.length }}</div>
          <div class="stat-label">总作品数</div>
        </div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ completedCount }}</div>
          <div class="stat-label">已完成</div>
        </div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon">📄</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalPages }}</div>
          <div class="stat-label">总页数</div>
        </div>
      </div>
    </div>

    <div class="page-header">
      <h2 class="page-title">作品库</h2>
      <div class="header-actions">
        <button class="btn btn-secondary refresh-btn" @click="loadHistory" :disabled="loading">
          <span class="icon" :class="{ 'spinning': loading }">🔄</span>
          刷新
        </button>
      </div>
    </div>

    <div v-if="loading && historyList.length === 0" class="loading-state glass-panel">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="historyList.length === 0" class="empty-state glass-panel">
      <div class="empty-icon">📂</div>
      <h3>暂无作品</h3>
      <p>你生成的图文内容将显示在这里</p>
      <router-link to="/" class="btn btn-primary">去创作</router-link>
    </div>

    <div v-else class="works-grid">
      <div v-for="item in historyList" :key="item.task_id" class="work-card glass-panel" @click="viewDetails(item)">
        <div class="card-preview">
          <div class="preview-image" :style="getPreviewStyle(item)"></div>
          
          <!-- 右上角操作按钮组 -->
          <div class="action-buttons">
            <!-- 编辑按钮 -->
            <button
              class="action-btn edit-btn"
              @click.stop="handleEdit(item)"
              title="编辑"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
              </svg>
            </button>
            
            <!-- 删除按钮 -->
            <button
              class="action-btn delete-btn"
              @click.stop="handleDelete(item)"
              :disabled="deleting.has(item.task_id || item.id)"
              :title="deleting.has(item.task_id || item.id) ? '删除中...' : '删除'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getHistory, deleteHistory } from '../../services/api'
import { useAppStore } from '../../store'

const router = useRouter()
const store = useAppStore()
const historyList = ref<any[]>([])
const loading = ref(false)
const deleting = ref<Set<string>>(new Set())

// 计算统计数据
const completedCount = computed(() =>
  historyList.value.filter(item => item.status === 'completed').length
)

const totalPages = computed(() =>
  historyList.value.reduce((sum, item) => sum + (item.pages?.length || 0), 0)
)

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

const handleEdit = (item: any) => {
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
  
  // 跳转到创作区进行编辑
  router.push({
    path: '/creation/editor',
    query: {
      edit: item.task_id || item.id,
      topic: item.topic
    }
  })
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.works-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* 数据概览 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 2.5rem;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(236, 72, 153, 0.1));
  border-radius: 16px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
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

.works-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem;
}

.work-card {
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.work-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-preview {
  height: 220px;
  position: relative;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  transition: transform 0.5s ease;
}

.work-card:hover .preview-image {
  transform: scale(1.05);
}

/* 右上角操作按钮组 */
.action-buttons {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 10;
}

.work-card:hover .action-buttons {
  opacity: 1;
}

.action-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.action-btn:hover:not(:disabled) {
  transform: scale(1.1);
}

.action-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn svg {
  width: 1.1rem;
  height: 1.1rem;
  transition: color 0.3s;
}

/* 编辑按钮样式 */
.edit-btn:hover {
  background: #e0e7ff;
}

.edit-btn svg {
  color: #6366f1;
}

.edit-btn:hover svg {
  color: #4f46e5;
}

/* 删除按钮样式 */
.delete-btn:hover:not(:disabled) {
  background: #fee2e2;
}

.delete-btn svg {
  color: #ef4444;
}

.delete-btn:hover:not(:disabled) svg {
  color: #dc2626;
}

.status-badge {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  padding: 0.375rem 0.875rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.status-badge.completed {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.9), rgba(5, 150, 105, 0.9));
  color: white;
}

.status-badge.failed {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.9), rgba(220, 38, 38, 0.9));
  color: white;
}

.status-badge.pending {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.9), rgba(217, 119, 6, 0.9));
  color: white;
}

.card-content {
  padding: 1.5rem;
}

.card-title {
  margin: 0 0 0.75rem;
  font-size: 1.125rem;
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

.empty-state,
.loading-state {
  text-align: center;
  padding: 4rem 2rem;
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

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(99, 102, 241, 0.2);
  border-top-color: #6366f1;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .works-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
</style>