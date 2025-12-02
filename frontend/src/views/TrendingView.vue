<template>
  <div class="trending-container">
    <div class="trending-header">
      <h1 class="trending-title">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="title-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
        </svg>
        灵感与发现
      </h1>
      <button 
        class="refresh-btn" 
        @click="refreshAll"
        :disabled="loading"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" :class="['refresh-icon', { 'spinning': loading }]">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
        </svg>
        {{ loading ? '刷新中...' : '刷新全部' }}
      </button>
    </div>

    <div v-if="error" class="error-message">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="error-icon">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
      </svg>
      {{ error }}
    </div>

    <div v-if="loading && trendingData.length === 0" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在加载热榜数据...</p>
    </div>

    <div v-else class="trending-grid">
      <div 
        v-for="source in trendingData" 
        :key="source.source_id"
        class="trending-card"
      >
        <div class="card-header">
          <div class="source-info">
            <img 
              v-if="source.icon" 
              :src="source.icon" 
              :alt="source.source_name"
              class="source-icon"
              @error="handleIconError"
            >
            <div class="source-icon-placeholder" v-else>
              {{ source.source_name.charAt(0) }}
            </div>
            <h3 class="source-name">{{ source.source_name }}</h3>
          </div>
          <div class="update-time" :title="`更新时间: ${formatTime(source.updated_time)}`">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="time-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ getRelativeTime(source.updated_time) }}
          </div>
        </div>

        <div class="trending-list">
          <a
            v-for="(item, index) in source.items.slice(0, 10)"
            :key="item.id"
            :href="item.url"
            target="_blank"
            rel="noopener noreferrer"
            class="trending-item"
          >
            <span class="item-index" :class="{ 'top-three': index < 3 }">{{ index + 1 }}</span>
            <span class="item-title">{{ item.title }}</span>
            <span v-if="item.hot_value" class="item-hot">{{ item.hot_value }}</span>
            <span v-if="item.extra?.tag" class="item-tag">{{ item.extra.tag }}</span>
          </a>
        </div>

        <div v-if="source.from_cache" class="cache-badge">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="cache-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
          </svg>
          缓存数据
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getTrendingData } from '../services/api'

interface TrendingItem {
  id: string
  title: string
  url: string
  mobile_url?: string
  hot_value?: string
  index?: number
  extra?: {
    tag?: string
    excerpt?: string
    author?: string
  }
}

interface TrendingSource {
  source_id: string
  source_name: string
  icon: string
  items: TrendingItem[]
  updated_time: string
  from_cache: boolean
}

const trendingData = ref<TrendingSource[]>([])
const loading = ref(false)
const error = ref('')

const loadTrendingData = async (forceRefresh: boolean = false) => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await getTrendingData(forceRefresh)
    if (response.success) {
      trendingData.value = response.data
    } else {
      error.value = '加载失败'
    }
  } catch (err: any) {
    error.value = err.message || '网络错误，请稍后重试'
    console.error('Failed to load trending data:', err)
  } finally {
    loading.value = false
  }
}

const refreshAll = () => {
  loadTrendingData(true)
}

const handleIconError = (e: Event) => {
  const target = e.target as HTMLImageElement
  target.style.display = 'none'
}

const formatTime = (timeStr: string): string => {
  try {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return timeStr
  }
}

const getRelativeTime = (timeStr: string): string => {
  try {
    const date = new Date(timeStr)
    const now = new Date()
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
    
    if (diff < 60) return '刚刚'
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
    if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
    return `${Math.floor(diff / 86400)}天前`
  } catch {
    return '未知'
  }
}

onMounted(() => {
  loadTrendingData()
})
</script>

<style scoped>
.trending-container {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  background: var(--bg-color);
}

.trending-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--border-color);
}

.trending-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.title-icon {
  width: 2rem;
  height: 2rem;
  color: var(--primary-color);
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
}

.refresh-btn:hover:not(:disabled) {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.refresh-icon.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: var(--radius-md);
  color: #c33;
  margin-bottom: 1.5rem;
}

.error-icon {
  width: 1.5rem;
  height: 1.5rem;
  flex-shrink: 0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.trending-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 1.5rem;
}

.trending-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: var(--transition);
  position: relative;
}

.trending-card:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
}

.card-header {
  padding: 1.25rem;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(135deg, var(--bg-color) 0%, var(--surface-color) 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.source-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.source-icon {
  width: 2rem;
  height: 2rem;
  border-radius: var(--radius-sm);
  object-fit: cover;
}

.source-icon-placeholder {
  width: 2rem;
  height: 2rem;
  border-radius: var(--radius-sm);
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.source-name {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.update-time {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.time-icon {
  width: 0.875rem;
  height: 0.875rem;
}

.trending-list {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.trending-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--text-primary);
  transition: var(--transition);
}

.trending-item:hover {
  background: var(--bg-color);
  transform: translateX(4px);
}

.item-index {
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-color);
  border-radius: 4px;
}

.item-index.top-three {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  color: white;
  font-weight: 700;
}

.item-title {
  flex: 1;
  font-size: 0.9375rem;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.item-hot {
  flex-shrink: 0;
  font-size: 0.75rem;
  color: var(--primary-color);
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  background: var(--primary-light);
  border-radius: var(--radius-sm);
}

.item-tag {
  flex-shrink: 0;
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background: #ff6b6b;
  color: white;
  border-radius: var(--radius-sm);
  font-weight: 600;
}

.cache-badge {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.625rem;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  color: white;
  font-size: 0.75rem;
  border-radius: var(--radius-sm);
}

.cache-icon {
  width: 0.875rem;
  height: 0.875rem;
}

@media (max-width: 768px) {
  .trending-container {
    padding: 1rem;
  }
  
  .trending-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .trending-grid {
    grid-template-columns: 1fr;
  }
}
</style>