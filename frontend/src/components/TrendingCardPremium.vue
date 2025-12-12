<template>
  <div class="trending-card-premium glass-card-premium aurora-glow">
    <!-- 卡片头部 -->
    <div class="card-header">
      <div class="source-info">
        <div class="source-icon-wrapper">
          <img v-if="source.icon" :src="source.icon" :alt="source.name" class="source-icon" loading="lazy" />
          <div v-else class="source-icon-fallback" :style="{ backgroundColor: getSourceColor(source.id) }">
            {{ source.name.charAt(0) }}
          </div>
        </div>
        <div class="source-details">
          <h3 class="source-name">{{ source.name }}</h3>
          <div class="source-meta">
            <span class="update-indicator" :class="{ 'live': !loading && !error }">
              <span class="live-dot" v-if="!loading && !error"></span>
              {{ updateTimeText }}
            </span>
          </div>
        </div>
      </div>
      
      <div class="header-actions">
        <button 
          class="refresh-btn"
          :class="{ 'loading': loading, 'pulse': autoRefresh }"
          @click="handleRefresh"
          :disabled="loading"
          title="刷新数据"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="refresh-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
          </svg>
        </button>
        
        <button 
          class="expand-btn"
          :class="{ 'active': isExpanded }"
          @click="toggleExpand"
          title="展开/收起"
        >
          <ChevronDown :size="16" />
        </button>
      </div>
    </div>
    
    <!-- 卡片内容 -->
    <div class="card-content" :class="{ 'expanded': isExpanded }">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-header">
          <div class="loading-title"></div>
          <div class="loading-subtitle"></div>
        </div>
        <div class="skeleton-list">
          <div class="skeleton-item" v-for="i in 8" :key="i">
            <div class="skeleton-rank"></div>
            <div class="skeleton-content">
              <div class="skeleton-text"></div>
              <div class="skeleton-tag"></div>
            </div>
            <div class="skeleton-heat"></div>
          </div>
        </div>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">⚠️</div>
        <h4 class="error-title">数据加载失败</h4>
        <p class="error-message">{{ error }}</p>
        <button class="retry-btn btn-3d" @click="handleRefresh">
          <RefreshCw :size="16" />
          重新加载
        </button>
      </div>
      
      <!-- 空状态 -->
      <div v-else-if="items.length === 0" class="empty-state">
        <div class="empty-icon">📊</div>
        <h4 class="empty-title">暂无热点数据</h4>
        <p class="empty-message">暂无可用数据，请稍后重试</p>
      </div>
      
      <!-- 数据列表 -->
      <div v-else class="trending-list">
        <div 
          v-for="(item, index) in displayItems" 
          :key="item.id"
          class="trending-item"
          :class="{ 
            'top-item': index < 3,
            'hot-item': item.hot_value && parseHotValue(item.hot_value) > 1000000
          }"
          @click="handleItemClick(item)"
        >
          <!-- 排名 -->
          <div class="item-rank" :class="getRankClass(index)">
            <span class="rank-number">{{ index + 1 }}</span>
            <div class="rank-glow"></div>
          </div>
          
          <!-- 内容 -->
          <div class="item-content">
            <h4 class="item-title" :title="item.title">{{ item.title }}</h4>
            <div class="item-meta">
              <span v-if="item.extra?.label" class="item-label">
                {{ item.extra.label }}
              </span>
              <span v-if="item.extra?.author" class="item-author">
                @{{ item.extra.author }}
              </span>
            </div>
          </div>
          
          <!-- 热度 -->
          <div v-if="item.hot_value" class="item-heat">
            <div class="heat-icon">🔥</div>
            <span class="heat-value">{{ formatHotValue(item.hot_value) }}</span>
            <div class="heat-bar">
              <div 
                class="heat-fill" 
                :style="{ width: getHeatPercentage(item.hot_value) + '%' }"
              ></div>
            </div>
          </div>
          
          <!-- 趋势指示器 -->
          <div class="trend-indicator" v-if="item.extra?.trend">
            <div
              class="trend-arrow"
              :class="item.extra.trend"
              v-html="getTrendArrow(item.extra.trend)"
            ></div>
          </div>
        </div>
        
        <!-- 展开更多 -->
        <div v-if="!isExpanded && items.length > 10" class="expand-more">
          <button class="expand-btn-text" @click="isExpanded = true">
            查看全部 {{ items.length }} 条热点
            <ChevronDown :size="14" />
          </button>
        </div>
      </div>
    </div>
    
    <!-- 统计信息 -->
    <div v-if="!loading && !error && items.length > 0" class="card-stats">
      <div class="stat-item">
        <span class="stat-label">总热度</span>
        <span class="stat-value">{{ formatTotalHeat() }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">更新于</span>
        <span class="stat-value">{{ formatLastUpdate() }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">数据来源</span>
        <span class="stat-value">{{ source.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronDown, RefreshCw } from 'lucide-vue-next'
import { getTrendingBySource, type TrendingSource, type TrendingItem } from '../services/trendingApi'

const router = useRouter()

interface Props {
  source: TrendingSource
  autoRefresh?: boolean
}

const props = defineProps<Props>()

const items = ref<TrendingItem[]>([])
const loading = ref(false)
const error = ref('')
const updateTime = ref<Date | null>(null)
const updateTimeText = ref('刚刚更新')
const isExpanded = ref(false)

let updateInterval: number | null = null
let refreshInterval: number | null = null

// 显示项目
const displayItems = computed(() => {
  return isExpanded.value ? items.value : items.value.slice(0, 10)
})

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

// 解析热度值
const parseHotValue = (value: string | number): number => {
  return typeof value === 'string' ? parseInt(value) : value
}

// 获取热度百分比
const getHeatPercentage = (value: string | number): number => {
  const num = parseHotValue(value)
  const maxHeat = Math.max(...items.value.map(item => parseHotValue(item.hot_value || 0)))
  return maxHeat > 0 ? (num / maxHeat) * 100 : 0
}

// 获取排名样式类
const getRankClass = (index: number): string => {
  if (index === 0) return 'rank-gold'
  if (index === 1) return 'rank-silver'
  if (index === 2) return 'rank-bronze'
  return 'rank-normal'
}

// 获取趋势箭头
const getTrendArrow = (trend: string): string => {
  if (trend === 'up') return '↗'
  if (trend === 'down') return '↘'
  return '→'
}

// 获取源颜色
const getSourceColor = (sourceId: string): string => {
  const colors: Record<string, string> = {
    'weibo': '#ff6b6b',
    'zhihu': '#0066cc',
    'bilibili': '#fb7299',
    'douyin': '#000000',
    'baidu': '#2319dc',
    'toutiao': '#ff6600'
  }
  return colors[sourceId] || '#6366f1'
}

// 更新相对时间
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
    updateTimeText.value = `${minutes}分钟前`
  } else if (hours < 24) {
    updateTimeText.value = `${hours}小时前`
  } else {
    updateTimeText.value = `${Math.floor(hours / 24)}天前`
  }
}

// 格式化总热度
const formatTotalHeat = (): string => {
  const total = items.value.reduce((sum, item) => {
    return sum + parseHotValue(item.hot_value || 0)
  }, 0)
  return formatHotValue(total)
}

// 格式化最后更新时间
const formatLastUpdate = (): string => {
  if (!updateTime.value) return '未知'
  return updateTime.value.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 处理项目点击
const handleItemClick = (item: TrendingItem) => {
  router.push({
    path: '/creation/new',
    query: { topic: item.title }
  })
}

// 切换展开状态
const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

// 刷新数据
const handleRefresh = async () => {
  await loadData(true)
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

onMounted(() => {
  loadData()
  
  // 每秒更新一次相对时间
  updateInterval = window.setInterval(() => {
    updateRelativeTime()
  }, 1000)
  
  // 自动刷新（如果启用）
  if (props.autoRefresh) {
    refreshInterval = window.setInterval(() => {
      loadData(true)
    }, 300000) // 5分钟刷新一次
  }
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.trending-card-premium {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
  position: relative;
  transition: all 300ms cubic-bezier(0.25, 0.8, 0.25, 1);
}

.trending-card-premium::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 24px;
  padding: 1px;
  background: linear-gradient(135deg, #6366f1, #ec4899);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 300ms cubic-bezier(0.25, 0.8, 0.25, 1);
  pointer-events: none;
}

.trending-card-premium:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
}

.trending-card-premium:hover::before {
  opacity: 1;
}

.trending-card-premium:active {
  transform: translateY(-4px) scale(0.98);
  transition: transform 150ms;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
}

.source-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.source-icon-wrapper {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.source-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.source-icon-fallback {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 1rem;
}

.source-details {
  flex: 1;
}

.source-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.source-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.update-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.update-indicator.live {
  color: #10b981;
}

.live-dot {
  width: 6px;
  height: 6px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.refresh-btn,
.expand-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.refresh-btn:hover,
.expand-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: var(--primary-color);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn.loading .refresh-icon {
  animation: spin 1s linear infinite;
}

.refresh-btn.pulse {
  animation: pulse 2s infinite;
}

.expand-btn.active {
  transform: rotate(180deg);
}

/* 卡片内容 */
.card-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-content.expanded {
  overflow-y: auto;
}

/* 加载状态 */
.loading-state {
  padding: 1.25rem;
}

.loading-header {
  margin-bottom: 1rem;
}

.loading-title {
  height: 20px;
  width: 60%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.loading-subtitle {
  height: 16px;
  width: 40%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

.skeleton-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.skeleton-rank {
  width: 24px;
  height: 24px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

.skeleton-content {
  flex: 1;
}

.skeleton-text {
  height: 16px;
  width: 80%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 0.25rem;
}

.skeleton-tag {
  height: 12px;
  width: 30%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

.skeleton-heat {
  width: 40px;
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

/* 错误状态 */
.error-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.error-message {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.retry-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 0.9rem;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.empty-message {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* 趋势列表 */
.trending-list {
  flex: 1;
  overflow-y: auto;
}

.trending-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  cursor: pointer;
  transition: all 300ms cubic-bezier(0.25, 0.8, 0.25, 1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
}

.trending-item:last-child {
  border-bottom: none;
}

.trending-item:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateX(4px);
}

.trending-item:active {
  transform: translateX(4px) scale(0.98);
  transition: transform 150ms;
}

.trending-item.top-item {
  background: rgba(255, 255, 255, 0.02);
}

.trending-item.hot-item {
  background: rgba(255, 71, 87, 0.05);
}

/* 排名 */
.item-rank {
  position: relative;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.rank-number {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  z-index: 2;
}

.rank-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.rank-gold .rank-glow {
  background: radial-gradient(circle, rgba(255, 215, 0, 0.3) 0%, transparent 70%);
}

.rank-silver .rank-glow {
  background: radial-gradient(circle, rgba(192, 192, 192, 0.3) 0%, transparent 70%);
}

.rank-bronze .rank-glow {
  background: radial-gradient(circle, rgba(205, 127, 50, 0.3) 0%, transparent 70%);
}

.trending-item:hover .rank-glow {
  opacity: 1;
}

.rank-gold .rank-number {
  color: #ffd700;
}

.rank-silver .rank-number {
  color: #c0c0c0;
}

.rank-bronze .rank-number {
  color: #cd7f32;
}

/* 内容 */
.item-content {
  flex: 1;
  min-width: 0;
}

.item-title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.item-label {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(236, 72, 153, 0.1));
  color: var(--primary-color);
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.item-author {
  color: var(--text-secondary);
  font-size: 0.75rem;
}

/* 热度 */
.item-heat {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  min-width: 60px;
}

.heat-icon {
  font-size: 0.875rem;
}

.heat-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.heat-bar {
  width: 40px;
  height: 2px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 1px;
  overflow: hidden;
}

.heat-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff4757, #ffa502);
  border-radius: 1px;
  transition: width 0.3s ease;
}

/* 趋势指示器 */
.trend-indicator {
  margin-left: 0.5rem;
}

.trend-arrow {
  font-size: 1rem;
  font-weight: bold;
}

.trend-arrow.up {
  color: #10b981;
}

.trend-arrow.down {
  color: #ef4444;
}

.trend-arrow.stable {
  color: var(--text-secondary);
}

/* 展开更多 */
.expand-more {
  padding: 1rem;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.expand-btn-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: var(--primary-color);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.expand-btn-text:hover {
  gap: 0.75rem;
}

/* 统计信息 */
.card-stats {
  display: flex;
  justify-content: space-around;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

/* 动画 */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    padding: 1rem;
  }
  
  .trending-item {
    padding: 0.75rem 1rem;
  }
  
  .item-rank {
    width: 28px;
    height: 28px;
  }
  
  .rank-number {
    font-size: 0.8rem;
  }
  
  .item-title {
    font-size: 0.8rem;
  }
  
  .item-heat {
    min-width: 50px;
  }
  
  .heat-bar {
    width: 30px;
  }
  
  .card-stats {
    padding: 0.75rem 1rem;
  }
}
</style>