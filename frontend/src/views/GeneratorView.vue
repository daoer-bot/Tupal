<template>
  <div class="generator">
    <ProcessSteps :current-step="2" />

    <div class="page-header">
      <h2>文案大纲确认</h2>
      <div class="header-actions" v-if="store.currentOutline && !isGenerating && !isCompleted">
        <button @click="startGeneration" class="btn btn-primary">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon-svg">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l-.249 1.74" />
          </svg>
          开始生成图片
        </button>
      </div>
    </div>
    
    <!-- 大纲预览和编辑区 -->
    <div v-if="store.currentOutline && !isGenerating" class="outline-section">
      <div class="section-title">
        <h3>内容大纲：{{ store.currentOutline.topic }}</h3>
      </div>
      
      <div class="pages-grid">
        <div
          v-for="page in store.currentOutline.pages"
          :key="page.page_number"
          class="page-card"
        >
          <div class="page-number">P{{ page.page_number }}</div>
          <h4>{{ page.title }}</h4>
          <p>{{ page.description }}</p>
        </div>
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
            <img :src="image.url" :alt="`页面 ${image.page_number}`" />
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
    
    <!-- 完成状态 -->
    <div v-if="isCompleted" class="completion-section">
      <div class="success-message">
        <div class="success-icon">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3>图片生成完成！</h3>
        <p>所有页面已生成完毕，请前往结果页查看详情。</p>
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
      
      <div class="actions">
        <button @click="goHome" class="btn btn-secondary">返回首页</button>
        <button @click="viewResult" class="btn btn-primary">查看生成结果</button>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="retry" class="btn btn-secondary">重试</button>
    </div>
    
    <!-- 无大纲提示 -->
    <div v-if="!store.currentOutline && !isGenerating && !isCompleted" class="empty-state">
      <p>请先在首页生成内容大纲</p>
      <button @click="goHome" class="btn btn-primary">前往首页</button>
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

// 状态
const isGenerating = ref(false)
const isCompleted = ref(false)
const error = ref('')
const eventSource = ref<EventSource | null>(null)
const selectedGenerator = ref(store.imageModelConfig.generatorType || 'image_api') // 从 store 获取默认生成器

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

// 开始生成图片
const startGeneration = async () => {
  if (!store.currentOutline) {
    error.value = '没有可用的大纲'
    return
  }
  
  try {
    isGenerating.value = true
    error.value = ''
    
    // 使用 store 中的生成器类型（优先使用用户在配置中选择的）
    const generatorType = store.imageModelConfig.generatorType || selectedGenerator.value
    
    // 调用生成接口
    const response = await generateImages({
      task_id: store.currentOutline.task_id,
      pages: store.currentOutline.pages,
      topic: store.currentOutline.topic,
      reference_image: store.referenceImage || undefined,
      generator_type: generatorType, // 使用配置中的生成器类型
      image_model_config: store.imageModelConfig // 传递图片模型配置
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
      console.log('收到进度更新:', data) // 添加调试日志
      
      // 如果是 done 消息，保留之前的 images 数据
      if (data.done) {
        console.log('任务完成，保留现有图片数据')
        // 不更新 progressData，保留之前的数据
      } else {
        progressData.value = {
          ...progressData.value, // 保留之前的数据
          ...data,
          images: data.images || progressData.value.images || [], // 优先使用新数据，否则保留旧数据
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
      isCompleted.value = true
      
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
            status: progressData.value.failed_pages && progressData.value.failed_pages.length > 0
              ? 'completed'
              : 'completed'
          })
          console.log('历史记录已保存')
        } catch (err) {
          console.error('保存历史记录失败:', err)
          // 不影响用户操作，静默失败
        }
      }
    }
  )
}

// 重试
const retry = () => {
  error.value = ''
  isCompleted.value = false
  startGeneration()
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 查看结果
const viewResult = () => {
  router.push('/result')
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

// 挂载时检查是否有大纲
onMounted(() => {
  if (!store.currentOutline) {
    console.warn('No outline available')
  }
})
</script>

<style scoped>
.generator {
  max-width: 1200px;
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

/* 大纲区域 */
.outline-section {
  margin-bottom: 3rem;
}

.section-title {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.section-title h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 600;
}

.pages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.page-card {
  background: var(--surface-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  transition: var(--transition);
}

.page-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--border-hover);
}

.page-number {
  display: inline-block;
  background: var(--primary-light);
  color: var(--primary-color);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.page-card h4 {
  margin: 0 0 0.75rem;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 600;
}

.page-card p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.6;
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
.images-preview h4,
.completion-section h4 {
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-color);
  font-size: 0.9rem;
}

.download-link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.download-link:hover {
  text-decoration: underline;
}

/* 完成状态 */
.completion-section {
  text-align: center;
}

.success-message {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: var(--radius-lg);
  padding: 2rem;
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.success-icon {
  width: 4rem;
  height: 4rem;
  background: #dcfce7;
  color: #16a34a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.success-message h3 {
  margin: 0;
  color: #15803d;
  font-size: 1.25rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 3rem;
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

.empty-state {
  text-align: center;
  padding: 6rem 2rem;
  background: var(--surface-color);
  border-radius: var(--radius-lg);
  border: 1px dashed var(--border-color);
}

.empty-state p {
  color: var(--text-secondary);
  font-size: 1.1rem;
  margin-bottom: 2rem;
}
</style>