<template>
  <div class="home">
    <div class="hero">
      <h2>一句话，生成完整小红书图文</h2>
      <p class="description">
        输入你的创作主题，AI 将自动生成 6-9 页精美图文内容
      </p>
      
      <div class="input-section">
        <textarea
          v-model="topic"
          placeholder="例如：如何提高工作效率的10个小技巧"
          rows="3"
          class="topic-input"
        />
        
        <div class="reference-upload">
          <label class="upload-label">
            <input
              type="file"
              accept="image/*"
              @change="handleFileUpload"
              hidden
            />
            <span>📷 上传参考图片（可选）</span>
          </label>
          <span v-if="referenceFileName" class="file-name">
            {{ referenceFileName }}
          </span>
        </div>
        
        <button
          class="btn btn-primary generate-btn"
          @click="handleGenerate"
          :disabled="!topic || isGenerating"
        >
          {{ isGenerating ? '生成中...' : '开始生成' }}
        </button>
      </div>
      
      <div class="features">
        <div class="feature-item">
          <div class="icon">🤖</div>
          <h3>AI 智能生成</h3>
          <p>基于 Gemini 3 技术</p>
        </div>
        <div class="feature-item">
          <div class="icon">⚡</div>
          <h3>快速高效</h3>
          <p>支持最高 25 并发</p>
        </div>
        <div class="feature-item">
          <div class="icon">🎨</div>
          <h3>风格一致</h3>
          <p>参考图片风格匹配</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../store'
import { generateOutline, uploadReference } from '../services/api'

const router = useRouter()
const store = useAppStore()

const topic = ref('')
const referenceFileName = ref('')
const isGenerating = ref(false)

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

const handleGenerate = async () => {
  if (!topic.value) return
  
  isGenerating.value = true
  store.setGenerating(true)
  
  try {
    const response = await generateOutline({
      topic: topic.value,
      reference_image: store.referenceImage || undefined
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
.home {
  max-width: 800px;
  margin: 0 auto;
}

.hero {
  text-align: center;
}

.hero h2 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.description {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 2rem;
}

.input-section {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  margin-bottom: 3rem;
}

.topic-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  margin-bottom: 1rem;
  transition: border-color 0.3s;
}

.topic-input:focus {
  outline: none;
  border-color: #667eea;
}

.reference-upload {
  margin-bottom: 1.5rem;
  text-align: left;
}

.upload-label {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background: #f5f5f5;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
}

.upload-label:hover {
  background: #e0e0e0;
}

.file-name {
  margin-left: 1rem;
  color: #667eea;
  font-size: 0.9rem;
}

.generate-btn {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
}

.feature-item {
  text-align: center;
}

.icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-item h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.feature-item p {
  color: #666;
  font-size: 0.9rem;
}
</style>