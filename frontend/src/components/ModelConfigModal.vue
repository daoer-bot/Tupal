<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click="closeModal">
        <div class="glass-panel modal-container" @click.stop>
          <div class="modal-header">
            <div class="header-title">
              <h2>模型配置</h2>
              <p>管理你的 AI 模型参数</p>
            </div>
            <button class="close-btn" @click="closeModal">✕</button>
          </div>
          
          <div class="modal-body">
            <!-- 文本模型配置 -->
            <div class="config-section">
              <div class="section-header">
                <div class="section-info">
                  <span class="section-icon">📝</span>
                  <h3>文本模型</h3>
                  <span class="badge">生成大纲</span>
                </div>
                <button class="btn-sm btn-outline" @click="addTextModel">
                  + 添加模型
                </button>
              </div>
              
              <div v-if="textModels.length === 0" class="empty-config">
                暂无配置，点击上方按钮添加
              </div>
              
              <div v-else class="models-grid">
                <div
                  v-for="(model, index) in textModels"
                  :key="index"
                  class="model-card"
                  :class="{ active: selectedTextIndex === index }"
                  @click="selectedTextIndex = index"
                >
                  <div class="card-header">
                    <input
                      v-model="model.name"
                      placeholder="配置名称"
                      class="model-name-input"
                      @click.stop
                    />
                    <div class="card-actions">
                      <span v-if="selectedTextIndex === index" class="active-tag">当前使用</span>
                      <button class="delete-btn" @click.stop="deleteTextModel(index)">🗑️</button>
                    </div>
                  </div>
                  
                  <div class="card-body">
                    <div class="form-group">
                      <label>API URL</label>
                      <input v-model="model.url" placeholder="https://api.openai.com" class="glass-input" @click.stop />
                      <p class="field-hint">
                        <span class="endpoint-label">实际调用地址: </span>
                        <code class="endpoint-url">{{ getActualEndpoint(model) }}</code>
                      </p>
                    </div>
                    
                    <div class="form-group">
                      <label>API Key</label>
                      <input v-model="model.apiKey" type="password" placeholder="sk-..." class="glass-input" @click.stop />
                    </div>
                    
                    <div class="form-group">
                      <label>模型名称</label>
                      <input v-model="model.model" placeholder="gpt-4" class="glass-input" @click.stop />
                      <p class="field-hint">
                        文本模型使用 OpenAI 格式，支持: gpt-4, gpt-3.5-turbo, claude-3-opus 等
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 图片模型配置 -->
            <div class="config-section">
              <div class="section-header">
                <div class="section-info">
                  <span class="section-icon">🎨</span>
                  <h3>图片模型</h3>
                  <span class="badge">生成图片</span>
                </div>
                <button class="btn-sm btn-outline" @click="addImageModel">
                  + 添加模型
                </button>
              </div>
              
              <div v-if="imageModels.length === 0" class="empty-config">
                暂无配置，点击上方按钮添加
              </div>
              
              <div v-else class="models-grid">
                <div
                  v-for="(model, index) in imageModels"
                  :key="index"
                  class="model-card"
                  :class="{ active: selectedImageIndex === index }"
                  @click="selectedImageIndex = index"
                >
                  <div class="card-header">
                    <input
                      v-model="model.name"
                      placeholder="配置名称"
                      class="model-name-input"
                      @click.stop
                    />
                    <div class="card-actions">
                      <span v-if="selectedImageIndex === index" class="active-tag">当前使用</span>
                      <button class="delete-btn" @click.stop="deleteImageModel(index)">🗑️</button>
                    </div>
                  </div>
                  
                  <div class="card-body">
                    <div class="form-group">
                      <label>接口规则</label>
                      <select v-model="model.apiFormat" class="glass-input" @click.stop>
                        <option value="chat">OpenAI-Chat 格式（推荐）</option>
                        <option value="generations">OpenAI-DALL·E 格式</option>
                        <option value="official">Gemini 原生格式</option>
                      </select>
                      <p class="field-hint">
                        • OpenAI-Chat: /v1/chat/completions 端点<br>
                        • OpenAI-DALL·E 格式: /v1/images/generations 端点<br>
                        • Gemini 原生格式: 原生 generateContent 端点
                      </p>
                    </div>
                    
                    <div class="form-group">
                      <label>API URL</label>
                      <input v-model="model.url" placeholder="API 地址" class="glass-input" @click.stop />
                      <p class="field-hint">
                        <span class="endpoint-label">实际调用地址: </span>
                        <code class="endpoint-url">{{ getActualEndpoint(model) }}</code>
                      </p>
                    </div>
                    
                    <div class="form-group">
                      <label>API Key</label>
                      <input v-model="model.apiKey" type="password" placeholder="API Key" class="glass-input" @click.stop />
                    </div>
                    
                    <div class="form-group">
                      <label>模型名称</label>
                      <input v-model="model.model" placeholder="nano-banana" class="glass-input" @click.stop />
                      <p class="field-hint">
                        <span v-if="model.apiFormat === 'chat'">常用模型: gemini-2.0-flash-exp-image-generation, gpt-4, claude-3 等</span>
                        <span v-else-if="model.apiFormat === 'generations'">常用模型: dall-e-3, dall-e-2, flux-pro 等</span>
                        <span v-else>常用模型: gemini-2.0-flash-exp, gemini-pro-vision 等</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeModal">取消</button>
            <button class="btn btn-primary" @click="saveConfig">保存配置</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface ModelConfig {
  name: string
  url: string
  apiKey: string
  model: string
  generatorType: string
  apiFormat?: string // 仅用于图片模型
}

// 计算实际的接口地址（根据选择的格式动态变化）
const getActualEndpoint = (model: ModelConfig): string => {
  if (!model.url) {
    return '请先填写 API URL'
  }
  
  let baseUrl = model.url.trim().replace(/\/+$/, '') // 移除末尾的斜杠
  
  // 文本模型（OpenAI 格式）
  if (model.generatorType === 'openai') {
    // 如果 URL 不包含 /v1，自动添加
    if (!baseUrl.endsWith('/v1')) {
      baseUrl = `${baseUrl}/v1`
    }
    return `${baseUrl}/chat/completions`
  }
  
  // 图像模型
  if (model.apiFormat === 'chat') {
    // OpenAI-Chat 格式: /v1/chat/completions
    return `${baseUrl}/v1/chat/completions`
  } else if (model.apiFormat === 'generations') {
    // OpenAI-DALL·E 格式: /v1/images/generations
    return `${baseUrl}/v1/images/generations`
  } else if (model.apiFormat === 'official') {
    // Gemini 原生格式: /v1beta/models/{model}:generateContent
    const modelName = model.model || 'gemini-2.0-flash-exp'
    return `${baseUrl}/v1beta/models/${modelName}:generateContent`
  }
  
  return baseUrl
}

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
  save: [textModels: ModelConfig[], imageModels: ModelConfig[], selectedTextIndex: number, selectedImageIndex: number]
}>()

const textModels = ref<ModelConfig[]>([])
const imageModels = ref<ModelConfig[]>([])
const selectedTextIndex = ref(0)
const selectedImageIndex = ref(0)

// 加载配置
const loadConfig = () => {
  const savedTextModels = localStorage.getItem('textModels')
  const savedImageModels = localStorage.getItem('imageModels')
  const savedSelectedTextIndex = localStorage.getItem('selectedTextIndex')
  const savedSelectedImageIndex = localStorage.getItem('selectedImageIndex')
  
  if (savedTextModels) {
    textModels.value = JSON.parse(savedTextModels)
  }
  if (savedImageModels) {
    imageModels.value = JSON.parse(savedImageModels)
  }
  if (savedSelectedTextIndex) {
    selectedTextIndex.value = parseInt(savedSelectedTextIndex)
  }
  if (savedSelectedImageIndex) {
    selectedImageIndex.value = parseInt(savedSelectedImageIndex)
  }
}

// 监听 show 变化，打开时加载配置
watch(() => props.show, (newVal) => {
  if (newVal) {
    loadConfig()
  }
})

const addTextModel = () => {
  textModels.value.push({
    name: `文本模型 ${textModels.value.length + 1}`,
    url: 'https://api.openai.com',
    apiKey: '',
    model: 'gpt-4',
    generatorType: 'openai'
  })
}

const addImageModel = () => {
  imageModels.value.push({
    name: `图片模型 ${imageModels.value.length + 1}`,
    url: '',
    apiKey: '',
    model: 'nano-banana',
    generatorType: 'image_api',  // 明确设置为 image_api
    apiFormat: 'chat'  // 默认使用 chat 格式
  })
}

// 监听 apiFormat 变化，自动更新对应的默认模型
watch(() => imageModels.value.map(m => m.apiFormat), (newFormats, oldFormats) => {
  imageModels.value.forEach((model, index) => {
    // 只有当格式发生变化时才更新模型
    if (newFormats[index] !== oldFormats[index]) {
      if (model.apiFormat === 'official') {
        // Gemini 原生格式
        model.model = 'gemini-3-pro-image-preview'
      } else if (model.apiFormat === 'chat') {
        // OpenAI-Chat 格式
        model.model = 'nano-banana'
      } else if (model.apiFormat === 'generations') {
        // OpenAI-DALL·E 格式
        model.model = 'nano-banana'
      }
    }
  })
}, { deep: true })

const deleteTextModel = (index: number) => {
  if (confirm('确定要删除这个配置吗？')) {
    textModels.value.splice(index, 1)
    if (selectedTextIndex.value >= textModels.value.length) {
      selectedTextIndex.value = Math.max(0, textModels.value.length - 1)
    }
  }
}

const deleteImageModel = (index: number) => {
  if (confirm('确定要删除这个配置吗？')) {
    imageModels.value.splice(index, 1)
    if (selectedImageIndex.value >= imageModels.value.length) {
      selectedImageIndex.value = Math.max(0, imageModels.value.length - 1)
    }
  }
}

const closeModal = () => {
  emit('close')
}

const saveConfig = () => {
  // 保存到 localStorage
  localStorage.setItem('textModels', JSON.stringify(textModels.value))
  localStorage.setItem('imageModels', JSON.stringify(imageModels.value))
  localStorage.setItem('selectedTextIndex', selectedTextIndex.value.toString())
  localStorage.setItem('selectedImageIndex', selectedImageIndex.value.toString())
  
  // 触发保存事件
  emit('save', textModels.value, imageModels.value, selectedTextIndex.value, selectedImageIndex.value)
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  border-radius: 24px;
  width: 100%;
  max-width: 900px;
  height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.9);
}

.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: transparent;
}

.header-title h2 {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
  color: var(--text-primary);
  font-weight: 700;
}

.header-title p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.2rem;
  color: var(--text-tertiary);
  cursor: pointer;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--text-primary);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  background: transparent;
}

.config-section {
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  padding-bottom: 1rem;
}

.section-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-icon {
  font-size: 1.5rem;
  filter: none;
}

.section-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
  font-weight: 700;
}

.badge {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  border: none;
}

.btn-outline {
  background: white;
  border: 1px solid rgba(0,0,0,0.1);
  color: var(--text-secondary);
  border-radius: 8px;
  font-size: 0.85rem;
  padding: 0.4rem 1rem;
  transition: all 0.2s;
  cursor: pointer;
}

.btn-outline:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.model-card {
  background: white;
  border: 1px solid rgba(0,0,0,0.05);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.model-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.05);
}

.model-card.active {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-color);
}

.card-header {
  padding: 1rem;
  border-bottom: 1px solid rgba(0,0,0,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
}

.model-name-input {
  border: none;
  background: transparent;
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-primary);
  width: 100%;
  padding: 0.25rem 0;
  border-bottom: 1px solid transparent;
}

.model-name-input:focus {
  outline: none;
  border-bottom-color: var(--primary-color);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.active-tag {
  font-size: 0.7rem;
  color: white;
  font-weight: 600;
  background: var(--primary-color);
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
}

.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.3;
  transition: opacity 0.2s;
  padding: 0.25rem;
  filter: none;
}

.delete-btn:hover {
  opacity: 1;
}

.card-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.glass-input {
  padding: 0.75rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  color: var(--text-primary);
  width: 100%;
}

.glass-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.modal-footer {
  padding: 1.5rem 2rem;
  border-top: 1px solid rgba(0,0,0,0.05);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  background: transparent;
}

.btn {
  padding: 0.6rem 1.5rem;
  font-size: 0.9rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 600;
}

.btn-secondary {
  background: transparent;
  border: 1px solid rgba(0,0,0,0.1);
  color: var(--text-secondary);
}

.btn-secondary:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.btn-primary {
  background: var(--primary-color);
  border: 1px solid var(--primary-color);
  color: white;
}

.btn-primary:hover {
  filter: brightness(1.1);
}

.empty-config {
  text-align: center;
  padding: 4rem;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  color: var(--text-tertiary);
}

.field-hint {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-tertiary);
  line-height: 1.5;
}

.endpoint-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.endpoint-url {
  background: #f1f5f9;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: var(--text-secondary);
  word-break: break-all;
  display: inline-block;
  margin-top: 0.25rem;
  border: 1px solid rgba(0,0,0,0.05);
}

.warning-text {
  color: #d97706;
  font-weight: 500;
}

.info-text {
  color: #2563eb;
  font-weight: 500;
}

/* 动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95) translateY(10px);
}
</style>