
<template>
  <div class="result-view">
    <ProcessSteps :current-step="3" />
    
    <div class="page-header">
      <h2>图文生成结果</h2>
      <div class="header-actions" v-if="!isGenerating && hasImages">
        <button @click="downloadAll" class="btn btn-primary">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon-svg">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
          </svg>
          下载全部
        </button>
      </div>
    </div>

    <!-- 生成进度区 -->
    <div v-if="isGenerating" class="generation-section">
      <div class="progress-container">
        <div class="progress-header">
          <h3>正在生成图片...</h3>
          <span class="progress-percentage">{{ progressData.progress }}%</span>
        </div>
        
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" :style="{ width: `${progressData.progress}%` }"></div>
        </div>
        
        <div class="progress-info">
          <p class="progress-message">{{ progressData.message }}</p>
          <p class="progress-detail">
            {{ progressData.completed_pages }} / {{ progressData.total_pages }} 页已完成
          </p>
        </div>
      </div>
      
      <!-- 已生成的图片预览 -->
      <div v-if="progressData.images.length > 0" class="images-preview">
        <h4>已生成的图片</h4>
        <div class="images-grid">
          <div
            v-for="image in progressData.images"
            :key="image.page_number"
            class="image-item"
          >
            <img :src="image.url" :alt="`页面 ${image.page_number}`" @click="previewImage(image.url)" />
            <div class="image-label">页面 {{ image.page_number }}</div>
          </div>
        </div>
      </div>
      
      <!-- 失败的页面信息 -->
      <div v-if="progressData.failed_pages && progressData.failed_pages.length > 0" class="failed-pages-section">
        <h4>⚠️ 生成失败的页面</h4>
        <div class="failed-pages-list">
          <div
            v-for="failed in progressData.failed_pages"
            :key="failed.page_number"
            class="failed-page-item"
          >
            <div class="failed-page-header">
              <span class="failed-page-number">页面 {{ failed.page_number }}</span>
              <span class="failed-page-time">{{ formatTime(failed.failed_at) }}</span>
            </div>
            <div class="failed-page-error">
              <span class="error-text">{{ failed.error }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 生成完成 - 显示结果 -->
    <div v-if="!isGenerating && store.currentOutline" class="result-content">
      <!-- 画廊视图 -->
      <div v-if="!expandedPageNumber" class="gallery-container">
        <div class="gallery-grid">
          <div
            v-for="page in store.currentOutline.pages"
            :key="page.page_number"
            class="gallery-item"
            @click="expandPage(page.page_number)"
          >
            <div class="gallery-image-wrapper">
              <img
                v-if="page.image_url"
                :src="page.image_url"
                :alt="`页面 ${page.page_number}`"
                class="gallery-image"
              />
              <div v-else class="gallery-image-placeholder">
                <span>暂无图片</span>
              </div>
              <div class="gallery-badge">P{{ page.page_number }}</div>
            </div>
          </div>
        </div>
        
        <!-- 文案区域在下方 - 只显示一个小红书文案 -->
        <div class="gallery-caption-section">
          <h3 class="gallery-caption-title">📝 小红书文案</h3>
          <div class="gallery-single-caption">
            <p v-if="store.currentOutline.pages[0]?.xiaohongshu_content" class="caption-text">
              {{ store.currentOutline.pages[0].xiaohongshu_content }}
            </p>
            <p v-else class="caption-text caption-fallback">暂无文案内容</p>
          </div>
        </div>
      </div>
      
      <!-- 展开的小红书视图 -->
      <div v-else class="xiaohongshu-expanded" @click="collapsePage">
        <div class="xhs-expanded-content" @click.stop>
          <button class="xhs-close-btn" @click="collapsePage">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          
          <div class="xhs-expanded-image">
            <img
              v-if="expandedPage?.image_url"
              :src="expandedPage.image_url"
              :alt="`页面 ${expandedPage.page_number}`"
            />
            <div v-else class="xhs-expanded-placeholder">
              <span>暂无图片</span>
            </div>
            <div class="xhs-expanded-badge">P{{ expandedPage?.page_number }}</div>
          </div>
          
          <div class="xhs-expanded-caption">
            <h3 class="xhs-expanded-title">{{ expandedPage?.title }}</h3>
            <div class="xhs-expanded-text">
              <p v-if="store.currentOutline?.pages[0]?.xiaohongshu_content">
                {{ store.currentOutline.pages[0].xiaohongshu_content }}
              </p>
              <p v-else class="xhs-fallback">暂无文案内容</p>
            </div>
            
            <div class="xhs-expanded-actions">
              <a
                v-if="expandedPage?.image_url"
                :href="expandedPage.image_url"
                target="_blank"
                class="xhs-action-btn"
                @click.stop
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                </svg>
                下载图片
              </a>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 失败的页面信息（完成状态） -->
      <div v-if="progressData.failed_pages && progressData.failed_pages.length > 0" class="failed-pages-section">
        <h4>⚠️ 以下页面生成失败</h4>
        <div class="failed-pages-list">
          <div
            v-for="failed in progressData.failed_pages"
            :key="failed.page_number"
            class="failed-page-item"
          >
            <div class="failed-page-header">
              <span class="failed-page-number">页面 {{ failed.page_number }}</span>
              <span class="failed-page-time">{{ formatTime(failed.failed_at) }}</span>
            </div>
            <div class="failed-page-error">
              <span class="error-text">{{ failed.error }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="retry" class="btn btn-secondary">重试</button>
    </div>
    
    <!-- 无大纲提示 -->
    <div v-if="!store.currentOutline && !isGenerating" class="empty-state">
      <p>暂无生成结果</p>
      <button @click="goHome" class="btn btn-primary">返回首页</button>
    </div>

    <div class="actions-footer" v-if="!isGenerating">
      <button @click="goBack" class="btn btn-secondary">返回上一步</button>
      <button @click="goHome" class="btn btn-outline">回到首页</button>
    </div>

    <!-- 图片预览模态框 -->
    <div v-if="previewUrl" class="image-modal" @click="closePreview">
      <div class="modal-content">
        <img :src="previewUrl" alt="预览图片" />
        <button class="close-btn" @click="closePreview">×</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../store'
import { generateImages, subscribeProgress, saveHistory, type ProgressData } from '../services/api'
import ProcessSteps from '../components/ProcessSteps.vue'

const router = useRouter()
const store = useAppStore()
const previewUrl = ref('')
const expandedPageNumber = ref<number | null>(null)

// 状态
const isGenerating = ref(false)
const error = ref('')
const eventSource = ref<EventSource | null>(null)
const selectedGenerator = ref(store.imageModelConfig.generatorType || 'image_api')

// 进度数据
const progressData = ref<ProgressData>({
  task_id: '',
  status: 'pending',
  progress: 0,
  total_pages: 0,
  completed_pages: 0,
  current_page: 0,
  message: '准备开始...',
  images: [],
  failed_pages: [],
  timestamp: ''
})

const hasImages = computed(() => {
  return store.currentOutline?.pages?.some(p => !!p.image_url) ?? false
})

// 开始生成图片
const startGeneration = async () => {
  if (!store.currentOutline) {
    error.value = '没有可用的大纲'
    return
  }
  
  try {
    isGenerating.value = true
    error.value = ''
    
    // 使用 store 中的生成器类型
    const generatorType = store.imageModelConfig.generatorType || selectedGenerator.value
    
    // 调用生成接口
    const response = await generateImages({
      task_id: store.currentOutline.task_id,
      pages: store.currentOutline.pages,
      topic: store.currentOutline.topic,
      reference_image: store.referenceImage || undefined,
      generator_type: generatorType,
      image_model_config: store.imageModelConfig
    })
    
    if (response.success) {
      // 订阅进度更新
      subscribeToProgress(response.task_id)
    } else {
      throw new Error('启动生成任务失败')
    }
  } catch (err: any) {
    error.value = err.message || '生成失败，请重试'
    isGenerating.value = false
    console.error('Generation error:', err)
  }
}

// 订阅进度更新
const subscribeToProgress = (taskId: string) => {
  eventSource.value = subscribeProgress(
    taskId,
    // 进度回调
    (data: ProgressData) => {
      console.log('收到进度更新:', data)
      
      if (data.done) {
        console.log('任务完成，保留现有图片数据')
      } else {
        progressData.value = {
          ...progressData.value,
          ...data,
          images: data.images || progressData.value.images || [],
          failed_pages: data.failed_pages || progressData.value.failed_pages || []
        }
        store.updateProgress(data.progress || progressData.value.progress, data.message || progressData.value.message)
      }
    },
    // 错误回调
    (err: Error) => {
      error.value = err.message
      isGenerating.value = false
    },
    // 完成回调
    async () => {
      isGenerating.value = false
      
      // 更新store中的大纲，添加图片URL
      if (store.currentOutline && progressData.value.images && Array.isArray(progressData.value.images)) {
        progressData.value.images.forEach(img => {
          const page = store.currentOutline!.pages.find(
            p => p.page_number === img.page_number
          )
          if (page) {
            page.image_url = img.url
          }
        })
        
        // 自动保存到历史记录
        try {
          await saveHistory({
            task_id: store.currentOutline.task_id,
            topic: store.currentOutline.topic,
            pages: store.currentOutline.pages,
            reference_image: store.referenceImage || undefined,
            generator_type: selectedGenerator.value,
            status: 'completed'
          })
          console.log('历史记录已保存')
        } catch (err) {
          console.error('保存历史记录失败:', err)
        }
      }
    }
  )
}

// 重试
const retry = () => {
  error.value = ''
  startGeneration()
}

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.push('/generator')
}

const previewImage = (url: string) => {
  previewUrl.value = url
}

const closePreview = () => {
  previewUrl.value = ''
}

// 展开图片到小红书视图
const expandPage = (pageNumber: number) => {
  expandedPageNumber.value = pageNumber
}

// 收起回到画廊视图
const collapsePage = () => {
  expandedPageNumber.value = null
}

// 获取展开的页面数据
const expandedPage = computed(() => {
  if (!expandedPageNumber.value || !store.currentOutline) return null
  return store.currentOutline.pages.find(p => p.page_number === expandedPageNumber.value)
})

const downloadAll = () => {
  if (!store.currentOutline) return
  
  store.currentOutline.pages.forEach(page => {
    if (page.image_url) {
      const link = document.createElement('a')
      link.href = page.image_url
      link.download = `page_${page.page_number}.jpg`
      link.click()
    }
  })
}

// 格式化时间
const formatTime = (timestamp: string) => {
  try {
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return timestamp
  }
}

// 清理资源
onUnmounted(() => {
  if (eventSource.value) {
    eventSource.value.close()
  }
})

// 挂载时自动开始生成
onMounted(() => {
  if (!store.currentOutline) {
    router.push('/')
  } else {
    // 检查是否已有图片（从历史记录查看的情况）
    const hasAnyImages = store.currentOutline.pages.some(p => !!p.image_url)
    if (!hasAnyImages) {
      // 只有当没有图片时才自动开始生成
      console.log('自动开始生成图片')
      startGeneration()
    } else {
      console.log('从历史记录查看，已有图片')
    }
  }
})
</script>

<style scoped>
.result-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

/* 生成进度区域 */
.generation-section {
  max-width: 800px;
  margin: 0 auto;
}

.progress-container {
  background: var(--surface-color);
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  margin-bottom: 2rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.progress-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.progress-percentage {
  font-weight: 700;
  color: var(--primary-color);
  font-size: 1.1rem;
}

.progress-bar-bg {
  background: var(--bg-color);
  border-radius: 9999px;
  height: 0.75rem;
  overflow: hidden;
  

  margin-bottom: 1.5rem;
}

.progress-bar-fill {
  background: var(--primary-color);
  height: 100%;
  border-radius: 9999px;
  transition: width 0.3s ease;
}

.progress-info {
  text-align: center;
}

.progress-message {
  font-size: 1rem;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.progress-detail {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* 图片预览 */
.images-preview h4 {
  color: var(--text-primary);
  margin: 2rem 0 1rem 0;
  font-size: 1.1rem;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.image-item {
  background: var(--surface-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  transition: var(--transition);
  cursor: pointer;
}

.image-item:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.image-item img {
  width: 100%;
  height: 320px;
  object-fit: cover;
  display: block;
}

.image-label {
  padding: 1rem;
  color: var(--text-primary);
  font-weight: 500;
  text-align: center;
  border-top: 1px solid var(--border-color);
  font-size: 0.9rem;
}

/* 失败页面区域 */
.failed-pages-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-radius: var(--radius-lg);
}

.failed-pages-section h4 {
  color: #be123c;
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.failed-pages-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.failed-page-item {
  background: white;
  border-radius: var(--radius-md);
  padding: 1rem;
  border: 1px solid #fda4af;
}

.failed-page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.failed-page-number {
  font-weight: 600;
  color: #e11d48;
  font-size: 0.9rem;
}

.failed-page-time {
  color: #881337;
  font-size: 0.8rem;
  opacity: 0.7;
}

.failed-page-error {
  color: #9f1239;
  font-size: 0.875rem;
}

.error-text {
  word-break: break-word;
}

/* 画廊视图容器 */
.gallery-container {
  max-width: 1200px;
  margin: 0 auto;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.gallery-item {
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--surface-color);
  box-shadow: var(--shadow-sm);
}

.gallery-item:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
}

.gallery-image-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  overflow: hidden;
  background: #f3f4f6;
}

.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.gallery-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.gallery-badge {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  background: rgba(255, 255, 255, 0.95);
  color: #333;
  padding: 0.35rem 0.75rem;
  border-radius: 16px;
  font-size: 0.7rem;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(8px);
}

/* 文案区域 */
.gallery-caption-section {
  background: var(--surface-color);
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.gallery-caption-title {
  margin: 0 0 1.5rem 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
}

.gallery-single-caption {
  padding: 2rem;
  background: white;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  max-width: 800px;
  margin: 0 auto;
}

.caption-text {
  color: #333;
  font-size: 0.9rem;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

.caption-fallback {
  color: var(--text-secondary);
  font-style: italic;
}

/* 展开的小红书视图 */
.xiaohongshu-expanded {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  cursor: pointer;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.xhs-expanded-content {
  background: white;
  border-radius: var(--radius-lg);
  max-width: 600px;
  max-height: 90vh;
  width: 100%;
  overflow-y: auto;
  cursor: default;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.xhs-close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 10;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border: none;
  border-radius: 50%;
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.xhs-close-btn:hover {
  background: rgba(0, 0, 0, 0.8);
  transform: scale(1.1);
}

.xhs-close-btn svg {
  width: 1.5rem;
  height: 1.5rem;
}

.xhs-expanded-image {
  position: relative;
  width: 100%;
  background: #f3f4f6;
}

.xhs-expanded-image img {
  width: 100%;
  height: auto;
  max-height: 60vh;
  object-fit: cover;
  display: block;
}

.xhs-expanded-placeholder {
  width: 100%;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.xhs-expanded-badge {
  position: absolute;
  top: 1rem;
  left: 1rem;
  background: rgba(255, 255, 255, 0.95);
  color: #333;
  padding: 0.4rem 0.9rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(8px);
}

.xhs-expanded-caption {
  padding: 2rem;
  background: white;
}

.xhs-expanded-title {
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: #333;
  line-height: 1.5;
}

.xhs-expanded-text {
  color: #333;
  font-size: 0.95rem;
  line-height: 1.8;
  margin-bottom: 1.5rem;
}

.xhs-expanded-text p {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.xhs-fallback {
  color: var(--text-secondary);
  font-style: italic;
}

.xhs-expanded-actions {
  display: flex;
  justify-content: center;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.xhs-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border-radius: var(--radius-md);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
}

.xhs-action-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.xhs-action-btn svg {
  width: 1.2rem;
  height: 1.2rem;
}

.actions-footer {
  margin-top: 3rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.empty-state {
  text-align: center;
  padding: 4rem;
  background: var(--surface-color);
  border-radius: var(--radius-lg);
  border: 1px dashed var(--border-color);
}

.empty-state p {
  color: var(--text-secondary);
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

/* 错误提示 */
.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  text-align: center;
  margin: 2rem 0;
}

.error-message p {
  color: #b91c1c;
  margin: 0 0 1rem 0;
  font-weight: 500;
}

.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  cursor: zoom-out;
}

.modal-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.modal-content img {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 4px;
}

.close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: none;
  border: none;
  color: white;
  font-size: 2rem;
  cursor: pointer;
}

@media (max-width: 768px) {
  .gallery-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .gallery-caption-section {
    padding: 1.5rem;
  }
  
  .gallery-caption-item {
    padding: 1.2rem;
  }
  
  .xhs-expanded-content {
    max-width: 100%;
    margin: 0 1rem;
  }
  
  .xhs-expanded-caption {
    padding: 1.5rem;
  }
  
  .xhs-expanded-title {
    font-size: 1.1rem;
  }
  
  .xhs-expanded-text {
    font-size: 0.9rem;
  }
}
</style>
