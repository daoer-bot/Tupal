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
              <button class="btn btn-primary btn-sm" @click="viewDetails(item)">
                查看详情
              </button>
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
import { getHistory } from '../services/api'
import { useAppStore } from '../store'

const router = useRouter()
const store = useAppStore()
const historyList = ref<any[]>([])
const loading = ref(false)

const loadHistory = async () => {
  loading.value = true
  try {
    const response = await getHistory()
    if (response.success) {
      historyList.value = response.data
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
  } finally {
    loading.value = false
  }
}

const viewDetails = (item: any) => {
  store.setOutline(item)
  router.push('/generator')
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
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.history-card:hover .preview-overlay {
  opacity: 1;
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