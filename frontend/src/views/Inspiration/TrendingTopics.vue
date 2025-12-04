<template>
  <div class="trending-view">
    <!-- 创作卡片 -->
    <div class="creation-card glass-panel-heavy">
      <div class="input-group">
        <label class="input-label">创作主题</label>
        <div class="input-wrapper">
          <MentionInput
            v-model="topic"
            placeholder="描述你的创意想法...&#10;例如：为夏日海边度假设计一套穿搭指南"
            :rows="4"
            input-class="topic-input glass-input"
          />
        </div>
      </div>
      
      <div class="action-bar">
        <button
          class="btn btn-primary generate-btn"
          @click="handleGenerate"
          :disabled="!topic || isGenerating"
        >
          <span v-if="isGenerating" class="loading-spinner"></span>
          {{ isGenerating ? '正在编织灵感...' : '开始生成' }}
          <svg v-if="!isGenerating" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="btn-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l-.249 1.74" />
          </svg>
        </button>
      </div>
    </div>

    <div class="trending-header">
      <div class="header-content">
        <h1 class="page-title">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="title-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 18a3.75 3.75 0 00.495-7.467 5.99 5.99 0 00-1.925 3.546 5.974 5.974 0 01-2.133-1A3.75 3.75 0 0012 18z" />
          </svg>
          热点与趋势
        </h1>
        <p class="page-subtitle">实时追踪全网热点，发现当下最热门的话题与趋势</p>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && sources.length === 0" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载热榜数据...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="error-icon">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
      </svg>
      <p class="error-message">{{ error }}</p>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../../store'
import TrendingCard from '../../components/TrendingCard.vue'
import MentionInput from '../../components/MentionInput.vue'
import { getTrendingSources, type TrendingSource } from '../../services/trendingApi'
import { generateOutline } from '../../services/api'
import materialApi from '../../services/materialApi'

const router = useRouter()
const store = useAppStore()

const topic = ref('')
const isGenerating = ref(false)
const sources = ref<TrendingSource[]>([])
const loading = ref(false)
const error = ref('')

const loadSources = async () => {
  loading.value = true
  error.value = ''
  
  try {
    sources.value = await getTrendingSources()
  } catch (e: any) {
    error.value = e.message || '加载数据源失败'
    console.error('加载数据源失败:', e)
  } finally {
    loading.value = false
  }
}

const handleGenerate = async () => {
  if (!topic.value) return
  
  isGenerating.value = true
  store.setGenerating(true)
  store.setReferenceImage(null)

  try {
    let enhancedTopic = topic.value
    let referenceImages: string[] = []
    
    const mentionedMaterialIds = extractMaterialIds(topic.value)
    
    if (mentionedMaterialIds.length > 0) {
      const refResponse = await materialApi.processReferences({
        material_ids: mentionedMaterialIds,
        base_prompt: topic.value
      })
      
      if (refResponse.success && refResponse.data) {
        enhancedTopic = refResponse.data.enhanced_prompt
        referenceImages = refResponse.data.reference_images
        
        if (referenceImages && referenceImages.length > 0) {
          store.setReferenceImage(referenceImages[0])
        }
      }
    }
    
    const finalReferenceImage = store.referenceImage || referenceImages[0] || undefined
    
    const response = await generateOutline({
      topic: enhancedTopic,
      reference_image: finalReferenceImage,
      generator_type: store.textModelConfig.generatorType || 'openai',
      text_model_config: store.textModelConfig
    })
    
    if (response.success) {
      store.setOutline(response.data)
      router.push('/creation/new')
    }
  } catch (error) {
    console.error('生成失败:', error)
    alert('生成大纲失败，请重试')
  } finally {
    isGenerating.value = false
    store.setGenerating(false)
  }
}

const extractMaterialIds = (text: string): string[] => {
  const regex = /@\[([^\]]+)\]\(([^)]+)\)/g
  const ids: string[] = []
  let match
  
  while ((match = regex.exec(text)) !== null) {
    ids.push(match[2])
  }
  
  return ids
}

onMounted(() => {
  loadSources()
  
  // 加载配置
  const savedTextModels = localStorage.getItem('textModels')
  const savedImageModels = localStorage.getItem('imageModels')
  const savedSelectedTextIndex = localStorage.getItem('selectedTextIndex')
  const savedSelectedImageIndex = localStorage.getItem('selectedImageIndex')
  
  if (savedTextModels) {
    const textModels = JSON.parse(savedTextModels)
    const selectedTextIndex = savedSelectedTextIndex ? parseInt(savedSelectedTextIndex) : 0
    if (textModels.length > 0 && textModels[selectedTextIndex]) {
      store.setTextModelConfig(textModels[selectedTextIndex])
    }
  }
  
  if (savedImageModels) {
    const imageModels = JSON.parse(savedImageModels)
    const selectedImageIndex = savedSelectedImageIndex ? parseInt(savedSelectedImageIndex) : 0
    if (imageModels.length > 0 && imageModels[selectedImageIndex]) {
      const config = imageModels[selectedImageIndex]
      if (!config.generatorType) {
        config.generatorType = 'image_api'
      }
      store.setImageModelConfig(config)
    }
  }
})
</script>

<style scoped>
.trending-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* 创作卡片 */
.creation-card {
  padding: 2rem;
  margin-bottom: 3rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.creation-card:hover {
  transform: translateY(-2px);
}

.input-group {
  margin-bottom: 1.5rem;
}

.input-label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.topic-input {
  min-height: 120px;
  resize: none;
}

.action-bar {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.generate-btn {
  flex: 1;
  font-size: 1rem;
  min-height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

.trending-header {
  margin-bottom: 2rem;
}

.header-content {
  text-align: center;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  font-size: 2rem;
  font-weight: 800;
  margin: 0 0 0.75rem;
  color: var(--text-primary);
}

.title-icon {
  width: 32px;
  height: 32px;
  color: var(--primary-color);
}

.page-subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.6;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon {
  width: 64px;
  height: 64px;
  color: var(--error-color, #ff4757);
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
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: var(--transition);
}

.retry-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

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

/* 响应式设计 */
@media (max-width: 768px) {
  .trending-view {
    padding: 1rem 0.75rem;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .title-icon {
    width: 24px;
    height: 24px;
  }

  .page-subtitle {
    font-size: 0.875rem;
  }

  .trending-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
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
</style>