<template>
  <div class="generator">
    <h2>图片生成器</h2>
    
    <!-- 大纲预览和编辑区 -->
    <div v-if="store.currentOutline && !isGenerating" class="outline-section">
      <div class="section-header">
        <h3>内容大纲：{{ store.currentOutline.topic }}</h3>
        <div class="header-actions">
          <!-- 生成器选择 -->
          <div class="generator-selector">
            <label for="generator-type">图片生成器：</label>
            <select id="generator-type" v-model="selectedGenerator" class="generator-select">
              <option value="mock">Mock (测试用占位图)</option>
              <option value="image_api">Image API (真实图片生成)</option>
              <option value="openai">OpenAI DALL-E 3</option>
            </select>
          </div>
          <button @click="startGeneration" class="btn btn-primary">
            开始生成图片
          </button>
        </div>
      </div>
      
      <div class="pages-grid">
        <div
          v-for="page in store.currentOutline.pages"
          :key="page.page_number"
          class="page-card"
        >
          <div class="page-number">{{ page.page_number }}</div>
          <h4>{{ page.title }}</h4>
          <p>{{ page.description }}</p>
        </div>
      </div>
    </div>
    
    <!-- 生成进度区 -->
    <div v-if="isGenerating" class="generation-section">
      <h3>正在生成图片...</h3>
      
      <!-- 进度条 -->
      <div class="progress-bar-container">
        <div class="progress-bar" :style="{ width: `${progressData.progress}%` }">
          <span class="progress-text">{{ progressData.progress }}%</span>
        </div>
      </div>
      
      <!-- 状态信息 -->
      <div class="progress-info">
        <p class="progress-message">{{ progressData.message }}</p>
        <p class="progress-detail">
          {{ progressData.completed_pages }} / {{ progressData.total_pages }} 页已完成
        </p>
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
              <span class="error-icon">❌</span>
              <span class="error-text">{{ failed.error }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 完成状态 -->
    <div v-if="isCompleted" class="completion-section">
      <div class="success-message">
        <span class="success-icon">✓</span>
        <h3>图片生成完成！</h3>
      </div>
      
      <div class="images-grid">
        <div
          v-for="image in progressData.images"
          :key="image.page_number"
          class="image-item"
        >
          <img :src="image.url" :alt="`页面 ${image.page_number}`" />
          <div class="image-label">
            页面 {{ image.page_number }}
            <a :href="image.url" target="_blank" class="download-link">下载</a>
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
              <span class="error-icon">❌</span>
              <span class="error-text">{{ failed.error }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="actions">
        <button @click="goHome" class="btn btn-secondary">返回首页</button>
        <button @click="downloadAll" class="btn btn-primary">下载全部</button>
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

const router = useRouter()
const store = useAppStore()

// 状态
const isGenerating = ref(false)
const isCompleted = ref(false)
const error = ref('')
const eventSource = ref<EventSource | null>(null)
const selectedGenerator = ref('image_api') // 默认使用 image_api（支持大多数第三方API）

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
    
    // 调用生成接口
    const response = await generateImages({
      task_id: store.currentOutline.task_id,
      pages: store.currentOutline.pages,
      topic: store.currentOutline.topic,
      reference_image: store.referenceImage || undefined,
      generator_type: selectedGenerator.value, // 使用用户选择的生成器
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

// 下载全部（简单实现）
const downloadAll = () => {
  if (!progressData.value.images || !Array.isArray(progressData.value.images)) {
    console.error('没有可下载的图片')
    return
  }
  progressData.value.images.forEach(image => {
    const link = document.createElement('a')
    link.href = image.url
    link.download = `page_${image.page_number}.jpg`
    link.click()
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

/* 大纲区域 */
.outline-section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-header h3 {
  margin: 0;
  color: #333;
  flex: 1;
  min-width: 200px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.generator-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.generator-selector label {
  font-size: 0.9rem;
  color: #666;
  white-space: nowrap;
}

.generator-select {
  padding: 0.5rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #333;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 200px;
}

.generator-select:hover {
  border-color: #667eea;
}

.generator-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.pages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.page-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.page-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.page-number {
  display: inline-block;
  background: #667eea;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.page-card h4 {
  margin: 0.5rem 0;
  color: #333;
  font-size: 1rem;
}

.page-card p {
  margin: 0;
  color: #666;
  font-size: 0.875rem;
  line-height: 1.5;
}

/* 生成进度区域 */
.generation-section {
  text-align: center;
}

.generation-section h3 {
  color: #667eea;
  margin-bottom: 2rem;
}

.progress-bar-container {
  background: #f0f0f0;
  border-radius: 25px;
  height: 50px;
  overflow: hidden;
  margin-bottom: 1.5rem;
  position: relative;
}

.progress-bar {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  height: 100%;
  border-radius: 25px;
  transition: width 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-text {
  color: white;
  font-weight: bold;
  font-size: 1.1rem;
}

.progress-info {
  margin-bottom: 2rem;
}

.progress-message {
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.progress-detail {
  color: #666;
  font-size: 0.9rem;
}

/* 图片预览 */
.images-preview h4,
.completion-section h4 {
  text-align: left;
  color: #333;
  margin: 2rem 0 1rem 0;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.image-item {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.image-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.image-item img {
  width: 100%;
  height: 300px;
  object-fit: cover;
  display: block;
}

.image-label {
  padding: 0.75rem;
  text-align: center;
  color: #333;
  font-weight: 500;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.download-link {
  color: #667eea;
  text-decoration: none;
  font-size: 0.875rem;
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
  border: 2px solid #86efac;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.success-icon {
  display: inline-block;
  width: 60px;
  height: 60px;
  line-height: 60px;
  background: #22c55e;
  color: white;
  border-radius: 50%;
  font-size: 2rem;
  margin-bottom: 1rem;
}

.success-message h3 {
  margin: 0;
  color: #166534;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

/* 错误提示 */
.error-message {
  background: #fef2f2;
  border: 2px solid #fca5a5;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  margin: 2rem 0;
}

.error-message p {
  color: #991b1b;
  margin: 0 0 1rem 0;
}

/* 空状态 */
/* 失败页面区域 */
.failed-pages-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #fef2f2;
  border: 2px solid #fca5a5;
  border-radius: 8px;
}

.failed-pages-section h4 {
  color: #991b1b;
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.failed-pages-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.failed-page-item {
  background: white;
  border-radius: 6px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.failed-page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.failed-page-number {
  font-weight: 600;
  color: #dc2626;
  font-size: 1rem;
}

.failed-page-time {
  color: #666;
  font-size: 0.875rem;
}

.failed-page-error {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #fef2f2;
  border-radius: 4px;
  border-left: 3px solid #dc2626;
}

.error-icon {
  flex-shrink: 0;
  font-size: 1rem;
}

.error-text {
  flex: 1;
  color: #7f1d1d;
  font-size: 0.875rem;
  line-height: 1.5;
  word-break: break-word;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-state p {
  color: #666;
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

/* 按钮样式 */
.btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-secondary:hover {
  background: #f5f7ff;
}
</style>