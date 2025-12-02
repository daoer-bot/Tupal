<template>
  <div class="trending-card">
    <div class="card-header">
      <div class="header-left">
        <img v-if="source.icon" :src="source.icon" :alt="source.name" class="source-icon" />
        <h3 class="source-name">{{ source.name }}</h3>
      </div>
      <div class="header-right">
        <span v-if="!loading && !error" class="update-time">
          {{ updateTimeText }}
        </span>
        <button 
          class="refresh-btn"
          :class="{ loading: loading }"
          @click="handleRefresh"
          :disabled="loading"
          title="刷新"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="refresh-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
          </svg>
        </button>
      </div>
    </div>

    <div class="card-body">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="skeleton-item" v-for="i in 8" :key="i"></div>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="error-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
        </svg>
        <p class="error-message">{{ error }}</p>
        <button class="retry-btn" @click="handleRefresh">重试</button>
      </div>

      <!-- 数据列表 -->
      <div v-else-if="items.length > 0" class="trending-list">
        <a
          v-for="(item, index) in items.slice(0, 10)"
          :key="item.id"
          :href="item.url"
          target="_blank"
          class="trending-item"
        >
          <div class="item-index" :class="getIndexClass(index)">
            {{ index + 1 }}
          </div>
          <div class="item-content">
            <div class="item-title">{{ item.title }}</div>
            <div v-if="item.extra?.label" class="item-label">{{ item.extra.label }}</div>
          </div>
          <div v-if="item.hot_value" class="item-hot">
            {{ formatHotValue(item.hot_value) }}
          </div>
        </a>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <p>暂无数据</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getTrendingBySource, type TrendingSource, type TrendingItem } from '../services/trendingApi'

interface Props {
  source: TrendingSource
}

const props = defineProps<Props>()

const items = ref<TrendingItem[]>([])
const loading = ref(false)
const error = ref('')
const updateTime = ref<Date | null>(null)
const updateTimeText = ref('刚刚更新')

let updateInterval: number | null = null

// 格式化热度值
const formatHotValue = (value: string | number): string => {
  const num = typeof value === 'string' ? parseInt(value) : value
  if (isNaN(num)) return String(value)
  
  if (num >= 100000000) {
    return (num / 100000000).toFixed(1) + '亿'
  } else if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return String(num)
}

// 获取排名样式类
const getIndexClass = (index: number): string => {
  if (index === 0) return 'top-1'
  if (index === 1) return 'top-2'
  if (index === 2) return 'top-3'
  return ''
}

// 更新相对时间文本
const updateRelativeTime = () => {
  if (!updateTime.value) {
    updateTimeText.value = '刚刚更新'
    return
  }
  
  const now = new Date()
  const diff = now.getTime() - updateTime.value.getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (seconds < 60) {
    updateTimeText.value = '刚刚更新'
  } else if (minutes < 60) {
    updateTimeText.value = `${minutes}分钟前更新`
  } else if (hours < 24) {
    updateTimeText.value = `${hours}小时前更新`
  } else {
    updateTimeText.value = `${Math.floor(hours / 24)}天前更新`
  }
}

// 加载数据
const loadData = async (forceRefresh = false) => {
  loading.value = true
  error.value = ''
  
  try {
    const result = await getTrendingBySource(props.source.id, forceRefresh)
    items.value = result.data
    updateTime.value = new Date()
    updateRelativeTime()
  } catch (e: any) {
    error.value = e.message || '加载失败'
    console.error(`加载 ${props.source.name} 失败:`, e)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const handleRefresh = () => {
  loadData(true)
}

onMounted(() => {
  loadData()
  
  // 每秒更新一次相对时间
  updateInterval = window.setInterval(() => {
    updateRelativeTime()
  }, 1000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>

<style scoped>
.trending-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: var(--transition);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.trending-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--border-hover);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.source-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.source-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.update-time {
  font-size: 0.75rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.refresh-btn {
  padding: 0.375rem;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--text-secondary);
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
}

.refresh-btn:hover:not(:disabled) {
  background: var(--surface-color);
  color: var(--primary-color);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn.loading .refresh-icon {
  animation: spin 1s linear infinite;
}

.refresh-icon {
  width: 18px;
  height: 18px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.card-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.trending-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.trending-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  text-decoration: none;
  color: var(--text-primary);
  transition: var(--transition);
  border-bottom: 1px solid var(--border-color);
}

.trending-item:last-child {
  border-bottom: none;
}

.trending-item:hover {
  background: var(--surface-color);
}

.item-index {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  background: var(--bg-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
}

.item-index.top-1 {
  background: #ff4757;
  color: white;
}

.item-index.top-2 {
  background: #ff6348;
  color: white;
}

.item-index.top-3 {
  background: #ffa502;
  color: white;
}

.item-content {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.item-title {
  flex: 1;
  font-size: 0.875rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-label {
  flex-shrink: 0;
  padding: 0.125rem 0.5rem;
  background: var(--primary-light);
  color: var(--primary-color);
  border-radius: var(--radius-sm);
  font-size: 0.625rem;
  font-weight: 500;
}

.item-hot {
  flex-shrink: 0;
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.loading-state, .error-state, .empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.skeleton-item {
  height: 40px;
  background: linear-gradient(90deg, var(--bg-color) 25%, var(--surface-color) 50%, var(--bg-color) 75%);
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
  border-radius: var(--radius-sm);
  margin: 0.5rem 1.25rem;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.error-icon {
  width: 48px;
  height: 48px;
  color: var(--error-color, #ff4757);
  margin-bottom: 1rem;
}

.error-message {
  margin: 0 0 1rem;
  font-size: 0.875rem;
}

.retry-btn {
  padding: 0.5rem 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.875rem;
  transition: var(--transition);
}

.retry-btn:hover {
  opacity: 0.9;
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}
</style>