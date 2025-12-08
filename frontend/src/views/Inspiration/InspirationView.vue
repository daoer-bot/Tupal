<template>
  <div class="inspiration-view">
    <div class="content-container">
      <!-- 头部区域 -->
      <div class="header-section animate-fade-in">
        <h1 class="page-title text-gradient-neon">灵感与发现</h1>
        <p class="page-subtitle">探索全网热点，激发无限创意</p>
      </div>

      <!-- Bento Grid 布局 -->
      <div class="bento-grid">
        
        <!-- 1. 采集器模块 (占据 4 列) -->
        <div class="col-span-4 glass-card animate-slide-up" style="--delay: 0.1s">
          <div class="card-header">
            <div class="icon-box collect">
              <Download :size="20" />
            </div>
            <h2 class="card-title">灵感采集</h2>
          </div>
          <div class="card-body">
            <p class="card-desc">一键提取小红书/抖音灵感</p>
            <div class="collector-input-wrapper">
              <input 
                v-model="quickCollectUrl" 
                type="text" 
                class="collector-input"
                placeholder="粘贴链接..."
              />
              <button class="btn-icon" @click="handleQuickCollect">
                <ArrowRight :size="18" />
              </button>
            </div>
          </div>
        </div>

        <!-- 2. 热门话题概览 (占据 8 列) -->
        <div class="col-span-8 glass-card animate-slide-up" style="--delay: 0.2s">
          <div class="card-header">
            <div class="icon-box hot">
              <TrendingUp :size="20" />
            </div>
            <h2 class="card-title">实时热点追踪</h2>
            <button class="btn-link" @click="navigateTo('/inspiration/trending')">
              查看全部 <ChevronRight :size="16" />
            </button>
          </div>
          <div class="trending-tags">
            <span v-for="(tag, index) in ['AI绘画', '赛博朋克', '极简主义', '复古未来']" :key="index" class="trend-tag">
              #{{ tag }}
            </span>
          </div>
        </div>

        <!-- 3. 热榜卡片流 (占据 12 列) -->
        <div class="col-span-12 animate-slide-up" style="--delay: 0.3s">
          <div class="section-header">
            <h3 class="section-title heading-decoration">全网热榜</h3>
          </div>
          
          <div class="trending-scroll-container">
            <div v-if="loadingTrending" class="loading-state glass-card">
              <div class="spinner"></div>
              <span>正在追踪热点...</span>
            </div>
            <div v-else class="trending-cards">
              <div 
                v-for="(item, index) in trendingPreview" 
                :key="index"
                class="trending-card glass-card"
                @click="navigateTo('/inspiration/trending')"
              >
                <div class="card-rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</div>
                <div class="card-content">
                  <h3 class="card-title-text">{{ item.title }}</h3>
                  <div class="card-meta">
                    <span class="hot-value">🔥 {{ item.hot }}</span>
                    <span class="source-tag">微博</span>
                  </div>
                </div>
                <div class="card-glow"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. 模板广场 (占据 12 列) -->
        <div class="col-span-12 animate-slide-up" style="--delay: 0.4s">
          <div class="section-header">
            <h3 class="section-title heading-decoration">精选模板</h3>
            <button class="btn-glass btn-sm" @click="navigateTo('/inspiration/templates')">
              更多模板
            </button>
          </div>
          
          <div class="template-grid">
            <div 
              v-for="template in templatePreview" 
              :key="template.id"
              class="template-card glass-card"
              @click="useTemplate(template)"
            >
              <div class="template-preview">
                <div class="template-icon">{{ template.icon }}</div>
              </div>
              <div class="template-info">
                <h3 class="template-name">{{ template.name }}</h3>
                <span class="template-tag">{{ template.tag }}</span>
              </div>
              <div class="hover-overlay">
                <span class="use-btn">立即使用</span>
              </div>
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
import { TrendingUp, Download, ChevronRight, ArrowRight } from 'lucide-vue-next'
import { getTrendingBySource } from '@/services/trendingApi'

const router = useRouter()

// 热榜数据
const loadingTrending = ref(true)
const trendingPreview = ref<Array<{ title: string; hot: string }>>([])

// 采集器
const quickCollectUrl = ref('')

// 模板数据
const templatePreview = ref([
  { id: 1, name: 'OOTD 穿搭分享', icon: '👗', tag: '时尚' },
  { id: 2, name: '周末探店指南', icon: '🍜', tag: '美食' },
  { id: 3, name: '旅行Vlog封面', icon: '✈️', tag: '旅行' },
  { id: 4, name: '好物种草清单', icon: '🛍️', tag: '生活' }
])

const navigateTo = (path: string) => {
  router.push(path)
}

const handleQuickCollect = () => {
  if (!quickCollectUrl.value) return
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
      // 只取前5条
      trendingPreview.value = response.data.slice(0, 5).map(item => ({
        title: item.title,
        hot: item.hot_value || '热'
      }))
    }
  } catch (error) {
    console.error('加载热榜数据失败:', error)
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
  padding-top: var(--nav-height);
  padding-bottom: 4rem;
  position: relative;
}

.content-container {
  position: relative;
  z-index: 1;
}

/* 头部区域 */
.header-section {
  text-align: center;
  margin-bottom: 3rem;
  padding-top: 2rem;
}

.page-title {
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 1.2rem;
  color: var(--text-secondary);
  font-weight: 400;
}

/* 卡片通用样式 */
.card-header {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid var(--glass-border);
}

.card-body {
  padding: 1.5rem;
}

.icon-box {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.icon-box.hot { background: linear-gradient(135deg, #f43f5e, #fb7185); }
.icon-box.collect { background: linear-gradient(135deg, #8b5cf6, #a78bfa); }

.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  flex: 1;
}

.card-desc {
  color: var(--text-secondary);
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

/* 采集器输入框 */
.collector-input-wrapper {
  display: flex;
  align-items: center;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 0.25rem;
  transition: all 0.3s ease;
}

.collector-input-wrapper:focus-within {
  border-color: var(--neon-violet);
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
}

.collector-input {
  flex: 1;
  background: none;
  border: none;
  padding: 0.75rem 1rem;
  color: white;
  font-size: 0.95rem;
}

.collector-input:focus {
  outline: none;
}

.btn-icon {
  background: var(--neon-violet);
  color: white;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: var(--neon-pink);
}

/* 热门标签 */
.trending-tags {
  padding: 1.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.trend-tag {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  color: var(--text-secondary);
  padding: 0.5rem 1rem;
  border-radius: 100px;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  cursor: pointer;
}

.trend-tag:hover {
  background: rgba(139, 92, 246, 0.1);
  color: var(--neon-violet);
  border-color: var(--neon-violet);
}

/* 区域标题 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 0 0.5rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.btn-link {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.btn-link:hover {
  color: var(--neon-violet);
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
}

/* 热榜滚动容器 */
.trending-scroll-container {
  overflow-x: auto;
  padding: 0.5rem;
  margin: -0.5rem;
  scrollbar-width: none;
}

.trending-scroll-container::-webkit-scrollbar {
  display: none;
}

.trending-cards {
  display: flex;
  gap: 1.5rem;
  min-width: min-content;
}

.trending-card {
  min-width: 280px;
  padding: 1.5rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 160px;
}

.card-rank {
  font-size: 3rem;
  font-weight: 900;
  opacity: 0.1;
  position: absolute;
  top: 0.5rem;
  right: 1rem;
  line-height: 1;
}

.rank-1 { color: #f43f5e; opacity: 0.3; }
.rank-2 { color: #f97316; opacity: 0.3; }
.rank-3 { color: #eab308; opacity: 0.3; }

.card-title-text {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: var(--text-primary);
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.hot-value {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.source-tag {
  font-size: 0.75rem;
  color: var(--neon-cyan);
  background: rgba(6, 182, 212, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

/* 模板网格 */
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.5rem;
}

.template-card {
  cursor: pointer;
}

.template-preview {
  height: 140px;
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid var(--glass-border);
}

.template-icon {
  font-size: 3.5rem;
  transition: transform 0.4s ease;
}

.template-card:hover .template-icon {
  transform: scale(1.1) rotate(5deg);
}

.template-info {
  padding: 1.25rem;
}

.template-name {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
}

.template-tag {
  font-size: 0.75rem;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.05);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.hover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  backdrop-filter: blur(4px);
}

.template-card:hover .hover-overlay {
  opacity: 1;
}

.use-btn {
  background: white;
  color: black;
  padding: 0.75rem 1.5rem;
  border-radius: 100px;
  font-weight: 600;
  transform: translateY(20px);
  transition: transform 0.3s ease;
}

.template-card:hover .use-btn {
  transform: translateY(0);
}

/* 响应式 */
@media (max-width: 768px) {
  .page-title { font-size: 2.5rem; }
  .template-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>