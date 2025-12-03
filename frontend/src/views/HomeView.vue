<template>
  <div class="home-container fade-enter-active">
    <!-- 头部 Hero 区域 -->
    <div class="hero-section">
      <div class="badge-pill animate-float">✨ AI 驱动的创意引擎</div>
      <h1 class="hero-title">
        释放无限<br>
        <span class="text-gradient">图文创作灵感</span>
      </h1>
      <p class="hero-subtitle">
        输入一个想法，自动生成完整的小红书图文。让 AI 成为你的专属设计总监，创作从未如此自由。
      </p>
    </div>
    
    <!-- 核心创作卡片 (灵感水晶) -->
    <div class="creation-card glass-panel-heavy">
      <div class="input-group">
        <label class="input-label">创作主题</label>
        <div class="input-wrapper">
          <MentionInput
            v-model="topic"
            placeholder="描述你的创意想法...&#10;例如：为夏日海边度假设计一套穿搭指南"
            :rows="5"
            input-class="topic-input glass-input"
          />
        </div>
      </div>
      
      <!-- 底部操作栏 -->
      <div class="action-bar">
        <!-- 生成按钮 -->
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
    
    <!-- 特性展示网格 -->
    <div class="features-grid">
      <div class="feature-card glass-panel">
        <div class="feature-icon-wrapper color-1">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l-.249 1.74" />
          </svg>
        </div>
        <h3>智能生成</h3>
        <p>基于先进大语言模型，自动生成高质量文案与配图方案</p>
      </div>
      
      <div class="feature-card glass-panel">
        <div class="feature-icon-wrapper color-2">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
          </svg>
        </div>
        <h3>快速高效</h3>
        <p>一键生成，支持高并发，让你的创作效率提升 10 倍</p>
      </div>
      
      <div class="feature-card glass-panel">
        <div class="feature-icon-wrapper color-3">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" />
          </svg>
        </div>
        <h3>风格一致</h3>
        <p>支持参考图风格迁移，保持视觉统一性，打造个人品牌</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../store'
import { generateOutline } from '../services/api'
import MentionInput from '../components/MentionInput.vue'
import materialApi from '../services/materialApi'

const router = useRouter()
const store = useAppStore()

const topic = ref('')
const isGenerating = ref(false)
const selectedMaterialIds = ref<string[]>([])

// 模型配置列表
const textModels = ref<any[]>([])
const imageModels = ref<any[]>([])
const selectedTextIndex = ref(0)
const selectedImageIndex = ref(0)

// 加载配置
const loadConfig = () => {
  const savedTextModels = localStorage.getItem('textModels')
  const savedImageModels = localStorage.getItem('imageModels')
  const savedSelectedTextIndex = localStorage.getItem('selectedTextIndex')
  const savedSelectedImageIndex = localStorage.getItem('selectedImageIndex')
  
  if (savedTextModels) textModels.value = JSON.parse(savedTextModels)
  if (savedImageModels) imageModels.value = JSON.parse(savedImageModels)
  if (savedSelectedTextIndex) selectedTextIndex.value = parseInt(savedSelectedTextIndex)
  if (savedSelectedImageIndex) selectedImageIndex.value = parseInt(savedSelectedImageIndex)
  
  updateStoreConfig()
}

// 更新 store 配置
const updateStoreConfig = () => {
  if (textModels.value.length > 0 && textModels.value[selectedTextIndex.value]) {
    store.setTextModelConfig(textModels.value[selectedTextIndex.value])
  }
  if (imageModels.value.length > 0 && imageModels.value[selectedImageIndex.value]) {
    const config = imageModels.value[selectedImageIndex.value]
    if (!config.generatorType) {
      config.generatorType = 'image_api'
    }
    store.setImageModelConfig(config)
  }
}

onMounted(() => {
  loadConfig()
})

const handleGenerate = async () => {
  if (!topic.value) return
  
  isGenerating.value = true
  store.setGenerating(true)
  
  store.setReferenceImage(null)

  try {
    let enhancedTopic = topic.value
    let referenceImages: string[] = []
    
    const mentionedMaterialIds = extractMaterialIds(topic.value)
    const allMaterialIds = [...new Set([...mentionedMaterialIds, ...selectedMaterialIds.value])]
    
    if (allMaterialIds.length > 0) {
      const refResponse = await materialApi.processReferences({
        material_ids: allMaterialIds,
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
      router.push('/generator')
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
</script>

<style scoped>
.home-container {
  max-width: 900px;
  margin: 0 auto;
  padding-top: 4vh;
}

/* 头部样式 */
.hero-section {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
}

.badge-pill {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 99px;
  font-size: 0.875rem;
  color: var(--primary-color);
  font-weight: 600;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.hero-subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

/* 核心创作卡片 */
.creation-card {
  padding: 2rem;
  margin-bottom: 4rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.creation-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
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
  padding-left: 0.5rem;
}

.topic-input {
  min-height: 160px;
  resize: none;
}

/* 底部操作栏 */
.action-bar {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.generate-btn {
  flex: 2;
  font-size: 1.1rem;
  min-height: 52px;
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
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 特性网格 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  padding: 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.3);
}

.feature-card:hover {
  background: rgba(255, 255, 255, 0.5);
  transform: translateY(-4px);
}

.feature-icon-wrapper {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.25rem;
  color: white;
}

.color-1 { background: linear-gradient(135deg, #6366f1, #8b5cf6); }
.color-2 { background: linear-gradient(135deg, #ec4899, #f43f5e); }
.color-3 { background: linear-gradient(135deg, #10b981, #3b82f6); }

.feature-icon-wrapper svg {
  width: 1.75rem;
  height: 1.75rem;
}

.feature-card h3 {
  font-size: 1.125rem;
  margin-bottom: 0.75rem;
  color: var(--text-primary);
}

.feature-card p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .action-bar {
    flex-direction: column;
  }
  
  .generate-btn {
    width: 100%;
  }
}
</style>