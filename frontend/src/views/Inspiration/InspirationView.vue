<template>
  <div class="inspiration-view">
    <div class="inspiration-container">
      <div class="header-section">
        <h1 class="page-title">灵感与发现</h1>
        <p class="page-subtitle">探索热点趋势，收集创作素材，发现优质模板</p>
      </div>
      
      <!-- 热榜小组件 -->
      <div class="widget-section">
        <div class="widget-header">
          <div class="widget-title-group">
            <TrendingUp :size="24" class="widget-icon" />
            <h2 class="widget-title">热榜</h2>
          </div>
          <button class="btn-link" @click="navigateTo('/inspiration/trending')">
            查看更多 <ChevronRight :size="16" />
          </button>
        </div>
        <div class="widget-content glass-card-premium">
          <div v-if="loadingTrending" class="loading-state">加载中...</div>
          <div v-else class="trending-list">
            <div 
              v-for="(item, index) in trendingPreview" 
              :key="index"
              class="trending-item"
            >
              <span class="trending-rank">{{ index + 1 }}</span>
              <span class="trending-title">{{ item.title }}</span>
              <span class="trending-hot">🔥 {{ item.hot }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 图文采集器小组件 -->
      <div class="widget-section">
        <div class="widget-header">
          <div class="widget-title-group">
            <Download :size="24" class="widget-icon" />
            <h2 class="widget-title">图文采集器</h2>
          </div>
          <button class="btn-link" @click="navigateTo('/inspiration/collector')">
            查看更多 <ChevronRight :size="16" />
          </button>
        </div>
        <div class="widget-content glass-card-premium">
          <div class="collector-quick">
            <input 
              v-model="quickCollectUrl" 
              type="text" 
              class="quick-input"
              placeholder="粘贴链接快速采集..."
            />
            <button class="btn-primary-small" @click="handleQuickCollect">
              采集
            </button>
          </div>
        </div>
      </div>
      
      <!-- 模板广场小组件 -->
      <div class="widget-section">
        <div class="widget-header">
          <div class="widget-title-group">
            <LayoutGrid :size="24" class="widget-icon" />
            <h2 class="widget-title">模板广场</h2>
          </div>
          <button class="btn-link" @click="navigateTo('/inspiration/templates')">
            查看更多 <ChevronRight :size="16" />
          </button>
        </div>
        <div class="widget-content glass-card-premium">
          <div class="template-grid">
            <div 
              v-for="template in templatePreview" 
              :key="template.id"
              class="template-card-mini"
              @click="useTemplate(template)"
            >
              <div class="template-icon-mini">{{ template.icon }}</div>
              <div class="template-name-mini">{{ template.name }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { TrendingUp, Download, LayoutGrid, ChevronRight } from 'lucide-vue-next'
import { getTrendingBySource, type TrendingItem } from '@/services/trendingApi'

const router = useRouter()

// 热榜数据
const loadingTrending = ref(true)
const trendingPreview = ref<Array<{ title: string; hot: string }>>([])

// 采集器
const quickCollectUrl = ref('')

// 模板数据
const templatePreview = ref([
  { id: 1, name: '穿搭分享', icon: '👗' },
  { id: 2, name: '美食探店', icon: '🍜' },
  { id: 3, name: '旅行攻略', icon: '✈️' },
  { id: 4, name: '好物推荐', icon: '🛍️' }
])

const navigateTo = (path: string) => {
  router.push(path)
}

const handleQuickCollect = () => {
  if (!quickCollectUrl.value) return
  // TODO: 实现快速采集逻辑
  console.log('快速采集:', quickCollectUrl.value)
  router.push('/inspiration/collector')
}

const useTemplate = (template: any) => {
  console.log('使用模板:', template)
  router.push('/inspiration/templates')
}

// 加载热榜数据
const loadTrendingData = async () => {
  try {
    loadingTrending.value = true
    // 默认加载微博热榜
    const response = await getTrendingBySource('weibo')
    if (response.success && response.data) {
      // 只取前3条
      trendingPreview.value = response.data.slice(0, 3).map(item => ({
        title: item.title,
        hot: item.hot_value || '热'
      }))
    }
  } catch (error) {
    console.error('加载热榜数据失败:', error)
    // 失败时显示提示
    trendingPreview.value = [
      { title: '暂时无法加载热榜数据', hot: '-' }
    ]
  } finally {
    loadingTrending.value = false
  }
}

onMounted(() => {
  loadTrendingData()
})
</script>

<style scoped>
.inspiration-view {
  min-height: 100vh;
  padding-top: 72px;
  background: linear-gradient(
    135deg,
    rgba(99, 102, 241, 0.05) 0%,
    rgba(236, 72, 153, 0.05) 50%,
    rgba(139, 92, 246, 0.05) 100%
  );
}

.inspiration-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem;
}

.header-section {
  text-align: center;
  margin-bottom: 3rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.page-subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

/* 小组件区域 */
.widget-section {
  margin-bottom: 2.5rem;
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.widget-title-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.widget-icon {
  color: var(--primary-color);
}

.widget-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.btn-link {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 0.5rem 1rem;
  border-radius: 8px;
}

.btn-link:hover {
  background: rgba(99, 102, 241, 0.1);
  transform: translateX(4px);
}

.widget-content {
  padding: 1.5rem;
}

/* 热榜列表 */
.loading-state {
  text-align: center;
  color: var(--text-secondary);
  padding: 2rem;
}

.trending-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.trending-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.trending-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.trending-rank {
  width: 24px;
  height: 24px;
  background: var(--primary-color);
  color: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 600;
  flex-shrink: 0;
}

.trending-title {
  flex: 1;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.trending-hot {
  color: var(--text-secondary);
  font-size: 0.85rem;
  flex-shrink: 0;
}

/* 采集器 */
.collector-quick {
  display: flex;
  gap: 1rem;
}

.quick-input {
  flex: 1;
  padding: 0.875rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.quick-input:focus {
  outline: none;
  border-color: var(--primary-color);
  background: rgba(255, 255, 255, 0.1);
}

.btn-primary-small {
  padding: 0.875rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-primary-small:hover {
  background: var(--accent-color);
  transform: translateY(-2px);
}

/* 模板网格 */
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
}

.template-card-mini {
  padding: 1.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.template-card-mini:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--primary-color);
  transform: translateY(-4px);
}

.template-icon-mini {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.template-name-mini {
  font-size: 0.9rem;
  color: var(--text-primary);
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .inspiration-container {
    padding: 2rem 1rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .widget-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .collector-quick {
    flex-direction: column;
  }
  
  .template-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>