<template>
  <div class="inspiration-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="title-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
        </svg>
        灵感与发现
      </h1>
      <p class="page-subtitle">探索热点，采集灵感，激发创作</p>
    </div>

    <!-- 图文采集区域 -->
    <section class="section-collector">
      <div class="section-header">
        <div class="section-title-wrapper">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="section-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
          </svg>
          <h2 class="section-title">图文采集</h2>
        </div>
        <p class="section-desc">从网络采集优质图文内容，快速构建素材库</p>
      </div>

      <div class="collector-card glass-panel">
        <div class="input-row">
          <input
            v-model="contentUrl"
            type="text"
            class="url-input"
            placeholder="粘贴小红书、微博等平台的内容链接..."
            @keyup.enter="handleCollect"
          />
          <button
            class="collect-btn"
            @click="handleCollect"
            :disabled="!contentUrl || isCollecting"
          >
            <span v-if="isCollecting" class="loading-spinner"></span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="btn-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
            </svg>
            {{ isCollecting ? '采集中...' : '采集' }}
          </button>
        </div>
      </div>

      <!-- 采集预览 -->
      <transition name="slide-fade">
        <div v-if="collectedContent" class="collected-preview glass-panel">
          <div class="preview-header">
            <h3 class="preview-title">采集预览</h3>
            <button
              class="save-btn"
              @click="handleSave"
              :disabled="isSaving"
            >
              <span v-if="isSaving" class="loading-spinner"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="btn-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0z" />
              </svg>
              {{ isSaving ? '保存中...' : '保存到素材库' }}
            </button>
          </div>

          <div class="preview-content">
            <div class="content-meta">
              <div class="meta-item">
                <span class="meta-label">作者</span>
                <span class="meta-value">{{ collectedContent.author }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">标题</span>
                <span class="meta-value">{{ collectedContent.title }}</span>
              </div>
            </div>

            <div v-if="collectedContent.desc" class="content-description">
              <span class="meta-label">描述</span>
              <p>{{ collectedContent.desc }}</p>
            </div>

            <div v-if="collectedContent.cover" class="content-cover">
              <span class="meta-label">封面</span>
              <img :src="collectedContent.cover" alt="封面" class="preview-image" />
            </div>

            <div v-if="collectedContent.imgurl && collectedContent.imgurl.length" class="content-images">
              <span class="meta-label">图片 ({{ collectedContent.imgurl.length }})</span>
              <div class="image-grid">
                <img v-for="(img, idx) in collectedContent.imgurl" :key="idx" :src="img" alt="图片" class="preview-image" />
              </div>
            </div>
          </div>
        </div>
      </transition>
    </section>

    <!-- 分隔线 -->
    <div class="section-divider">
      <div class="divider-line"></div>
      <span class="divider-text">热门话题</span>
      <div class="divider-line"></div>
    </div>

    <!-- 平台热榜区域 -->
    <section class="section-trending">
      <div class="section-header">
        <div class="section-title-wrapper">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="section-icon fire-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 18a3.75 3.75 0 00.495-7.467 5.99 5.99 0 00-1.925 3.546 5.974 5.974 0 01-2.133-1A3.75 3.75 0 0012 18z" />
          </svg>
          <h2 class="section-title">平台热榜</h2>
        </div>
        <p class="section-desc">实时追踪全网热点，发现当下最热门的话题与趋势</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="trendingLoading && sources.length === 0" class="loading-container">
        <div class="loading-spinner large"></div>
        <p>正在加载热榜数据...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="trendingError" class="error-container glass-panel">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="error-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
        </svg>
        <p class="error-message">{{ trendingError }}</p>
        <button class="retry-btn" @click="loadSources">重试</button>
      </div>

      <!-- 热榜网格 -->
      <div v-else class="trending-grid">
        <TrendingCard 
          v-for="source in sources" 
          :key="source.id" 
          :source="source"
        />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TrendingCard from '../../components/TrendingCard.vue'
import { getTrendingSources, type TrendingSource } from '../../services/trendingApi'
import materialApi from '../../services/materialApi'

const router = useRouter()

// 图文采集相关状态
const contentUrl = ref('')
const isCollecting = ref(false)
const isSaving = ref(false)
const collectedContent = ref<any>(null)

// 平台热榜相关状态
const sources = ref<TrendingSource[]>([])
const trendingLoading = ref(false)
const trendingError = ref('')

// 图文采集方法
const handleCollect = async () => {
  if (!contentUrl.value) return

  isCollecting.value = true
  try {
    const response = await fetch('http://localhost:5030/api/xiaohongshu/parse', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url: contentUrl.value })
    })

    const result = await response.json()

    if (result.success) {
      collectedContent.value = result.data
    } else {
      alert('解析失败: ' + (result.error || '未知错误'))
    }
  } catch (error) {
    alert('请求失败: ' + error)
  } finally {
    isCollecting.value = false
  }
}

const handleSave = async () => {
  if (!collectedContent.value) return

  isSaving.value = true
  try {
    const response = await materialApi.createMaterial({
      name: collectedContent.value.title || '未命名素材',
      type: 'reference',
      category: '小红书采集',
      content: {
        author: collectedContent.value.author,
        title: collectedContent.value.title,
        description: collectedContent.value.desc,
        cover: collectedContent.value.cover,
        images: collectedContent.value.imgurl || [],
        source_url: contentUrl.value,
        reference_type: 'xiaohongshu'
      },
      description: collectedContent.value.desc || '',
      tags: ['小红书', '采集']
    })

    if (response.success && response.material_id) {
      router.push(`/workspace/knowledge?type=reference&highlight=${response.material_id}`)
    } else {
      alert('保存失败: ' + (response.error || '未知错误'))
    }
  } catch (error) {
    alert('保存失败: ' + error)
  } finally {
    isSaving.value = false
  }
}

// 平台热榜方法
const loadSources = async () => {
  trendingLoading.value = true
  trendingError.value = ''
  
  try {
    sources.value = await getTrendingSources()
  } catch (e: any) {
    trendingError.value = e.message || '加载数据源失败'
    console.error('加载数据源失败:', e)
  } finally {
    trendingLoading.value = false
  }
}

onMounted(() => {
  loadSources()
})
</script>

<style scoped>
.inspiration-view {
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  font-size: 2.25rem;
  font-weight: 800;
  margin: 0 0 0.75rem;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color, #ec4899));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.title-icon {
  width: 36px;
  height: 36px;
  color: var(--primary-color);
}

.page-subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
  margin: 0;
}

/* 区块样式 */
.section-collector,
.section-trending {
  margin-bottom: 2rem;
}

.section-header {
  margin-bottom: 1.5rem;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.section-icon {
  width: 24px;
  height: 24px;
  color: var(--primary-color);
}

.fire-icon {
  color: #f97316;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.section-desc {
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin: 0;
  padding-left: 2rem;
}

/* 玻璃面板 */
.glass-panel {
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
  border-radius: 16px;
}

/* 采集卡片 */
.collector-card {
  padding: 1.5rem;
}

.input-row {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.url-input {
  flex: 1;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  border: 1px solid rgba(99, 102, 241, 0.2);
  background: rgba(255, 255, 255, 0.8);
  color: var(--text-primary);
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.url-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.url-input::placeholder {
  color: var(--text-tertiary, #94a3b8);
}

.collect-btn,
.save-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, var(--primary-color), var(--accent-color, #8b5cf6));
  color: white;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.collect-btn:hover:not(:disabled),
.save-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
}

.collect-btn:disabled,
.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

/* 加载动画 */
.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

.loading-spinner.large {
  width: 40px;
  height: 40px;
  border-width: 3px;
  border-color: var(--border-color, rgba(99, 102, 241, 0.2));
  border-top-color: var(--primary-color);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 采集预览 */
.collected-preview {
  margin-top: 1.5rem;
  padding: 1.5rem;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
}

.preview-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.content-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.meta-item {
  padding: 1rem;
  background: rgba(99, 102, 241, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(99, 102, 241, 0.1);
}

.meta-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.meta-value {
  display: block;
  font-size: 0.95rem;
  color: var(--text-primary);
  font-weight: 500;
}

.content-description,
.content-cover,
.content-images {
  padding: 1rem;
  background: rgba(99, 102, 241, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(99, 102, 241, 0.1);
}

.content-description p {
  margin: 0.5rem 0 0;
  line-height: 1.6;
  color: var(--text-primary);
}

.preview-image {
  max-width: 100%;
  border-radius: 8px;
  margin-top: 0.75rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.image-grid .preview-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  margin-top: 0;
}

/* 分隔线 */
.section-divider {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin: 3rem 0;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent);
}

.divider-text {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* 加载和错误状态 */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  color: var(--text-secondary);
}

.error-container {
  background: rgba(255, 255, 255, 0.65);
}

.error-icon {
  width: 48px;
  height: 48px;
  color: #f97316;
  margin-bottom: 1rem;
}

.error-message {
  margin: 0 0 1.5rem;
  font-size: 1rem;
}

.retry-btn {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* 热榜网格 */
.trending-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.5rem;
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 过渡动画 */
.slide-fade-enter-active {
  transition: all 0.4s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .inspiration-view {
    padding: 1.5rem 1rem;
  }

  .page-title {
    font-size: 1.75rem;
  }

  .title-icon {
    width: 28px;
    height: 28px;
  }

  .input-row {
    flex-direction: column;
  }

  .collect-btn {
    width: 100%;
    justify-content: center;
  }

  .preview-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .save-btn {
    width: 100%;
    justify-content: center;
  }

  .content-meta {
    grid-template-columns: 1fr;
  }

  .trending-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .section-desc {
    padding-left: 0;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .trending-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1025px) and (max-width: 1400px) {
  .trending-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1401px) {
  .trending-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* 暗色模式适配 */
@media (prefers-color-scheme: dark) {
  .glass-panel {
    background: rgba(30, 41, 59, 0.65);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .url-input {
    background: rgba(30, 41, 59, 0.8);
    border-color: rgba(99, 102, 241, 0.3);
    color: #f1f5f9;
  }

  .url-input::placeholder {
    color: #64748b;
  }

  .meta-item,
  .content-description,
  .content-cover,
  .content-images {
    background: rgba(99, 102, 241, 0.1);
    border-color: rgba(99, 102, 241, 0.2);
  }

  .error-container {
    background: rgba(30, 41, 59, 0.65);
  }
}
</style>