<template>
  <div class="home-container">
    <ProcessSteps :current-step="1" />

    <div class="hero-section">
      <h2 class="hero-title">一句话，生成完整<span class="highlight">小红书图文</span></h2>
      <p class="hero-subtitle">
        输入你的创作主题，AI 将自动生成精美图文内容，让创作从未如此简单
      </p>
    </div>
    
    <div class="creation-card card">
      <div class="input-group">
        <label class="input-label">创作主题</label>
        <div class="input-wrapper">
          <textarea
            v-model="topic"
            placeholder="例如：如何提高工作效率的10个小技巧..."
            rows="3"
            class="topic-input"
          />
        </div>
      </div>
      
      <div class="upload-section">
        <label class="upload-btn" :class="{ 'has-file': referenceFileName }">
          <input
            type="file"
            accept="image/*"
            @change="handleFileUpload"
            hidden
          />
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
          </svg>
          <span class="text">{{ referenceFileName || '上传参考图片（可选）' }}</span>
          <span v-if="referenceFileName" class="remove-file" @click.prevent="clearFile">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </span>
        </label>
      </div>
      
      <button
        class="btn btn-primary generate-btn"
        @click="handleGenerate"
        :disabled="!topic || isGenerating"
      >
        <span v-if="isGenerating" class="loading-spinner"></span>
        {{ isGenerating ? '正在生成灵感...' : '开始生成图文' }}
      </button>
    </div>
    
    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-icon-bg">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l-.249 1.74" />
          </svg>
        </div>
        <h3>AI 智能生成</h3>
        <p>基于先进大语言模型，自动生成高质量文案</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon-bg">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
          </svg>
        </div>
        <h3>快速高效</h3>
        <p>一键生成，支持高并发，创作快人一步</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon-bg">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" />
          </svg>
        </div>
        <h3>风格一致</h3>
        <p>支持参考图风格迁移，保持视觉统一性</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../store'
import { generateOutline, uploadReference } from '../services/api'
import ProcessSteps from '../components/ProcessSteps.vue'

const router = useRouter()
const store = useAppStore()

const topic = ref('')
const referenceFileName = ref('')
const isGenerating = ref(false)

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
    store.setImageModelConfig(imageModels.value[selectedImageIndex.value])
  }
}

onMounted(() => {
  loadConfig()
})

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    referenceFileName.value = file.name
    
    try {
      const response = await uploadReference(file)
      store.setReferenceImage(response.file_url)
    } catch (error) {
      console.error('上传失败:', error)
      alert('图片上传失败，请重试')
    }
  }
}

const clearFile = () => {
  referenceFileName.value = ''
  store.setReferenceImage('')
}

const handleGenerate = async () => {
  if (!topic.value) return
  
  isGenerating.value = true
  store.setGenerating(true)
  
  try {
    const response = await generateOutline({
      topic: topic.value,
      reference_image: store.referenceImage || undefined,
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
</script>

<style scoped>
.home-container {
  max-width: 800px;
  margin: 0 auto;
  padding-top: 4rem;
}

.hero-section {
  text-align: center;
  margin-bottom: 3rem;
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 1rem;
  color: var(--text-primary);
  letter-spacing: -0.025em;
}

.highlight {
  color: var(--primary-color);
  margin-left: 0.5rem;
}

.hero-subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.creation-card {
  margin-bottom: 4rem;
  border: 1px solid var(--border-color);
  background: var(--surface-color);
  box-shadow: var(--shadow-lg);
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

.input-wrapper {
  position: relative;
}

.topic-input {
  width: 100%;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 1rem;
  resize: vertical;
  transition: var(--transition);
  background: var(--bg-color);
  color: var(--text-primary);
}

.topic-input:focus {
  outline: none;
  border-color: var(--primary-color);
  background: var(--surface-color);
  box-shadow: 0 0 0 3px var(--primary-light);
}

.upload-section {
  margin-bottom: 2rem;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--bg-color);
  border: 1px dashed var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-secondary);
  font-weight: 500;
  width: 100%;
  justify-content: center;
}

.upload-btn:hover {
  background: var(--surface-color);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.upload-btn.has-file {
  background: var(--primary-light);
  color: var(--primary-color);
  border-color: var(--primary-color);
  border-style: solid;
}

.upload-btn .icon {
  width: 1.25rem;
  height: 1.25rem;
}

.remove-file {
  margin-left: 0.5rem;
  padding: 0.25rem;
  border-radius: 50%;
  cursor: pointer;
  opacity: 0.6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-file:hover {
  background: rgba(0, 0, 0, 0.05);
  opacity: 1;
}

.generate-btn {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  border-radius: var(--radius-md);
  font-weight: 600;
  letter-spacing: 0.025em;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 2rem;
}

.feature-card {
  text-align: center;
  padding: 2rem;
  background: var(--surface-color);
  border-radius: var(--radius-lg);
  transition: var(--transition);
  border: 1px solid var(--border-color);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: var(--border-hover);
}

.feature-icon-bg {
  width: 3.5rem;
  height: 3.5rem;
  background: var(--primary-light);
  color: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
}

.feature-card h3 {
  margin: 0 0 0.75rem;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 600;
}

.feature-card p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
}
</style>