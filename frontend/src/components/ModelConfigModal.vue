<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click="closeModal">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h2>🔧 模型配置管理</h2>
            <button class="close-btn" @click="closeModal">✕</button>
          </div>
          
          <div class="modal-body">
            <!-- 文本模型配置 -->
            <div class="config-section">
              <div class="section-title">
                <h3>📝 文本模型（生成大纲）</h3>
                <button class="add-btn" @click="addTextModel">+ 添加模型</button>
              </div>
              
              <div v-if="textModels.length === 0" class="empty-state">
                暂无配置，点击"添加模型"开始配置
              </div>
              
              <div v-else class="models-list">
                <div
                  v-for="(model, index) in textModels"
                  :key="index"
                  class="model-card"
                  :class="{ active: selectedTextIndex === index }"
                  @click="selectedTextIndex = index"
                >
                  <div class="model-header">
                    <input
                      v-model="model.name"
                      placeholder="配置名称"
                      class="model-name-input"
                      @click.stop
                    />
                    <button class="delete-btn" @click.stop="deleteTextModel(index)">🗑️</button>
                  </div>
                  <div class="model-fields">
                    <input
                      v-model="model.url"
                      placeholder="API URL"
                      class="model-input"
                      @click.stop
                    />
                    <input
                      v-model="model.apiKey"
                      type="password"
                      placeholder="API Key"
                      class="model-input"
                      @click.stop
                    />
                    <input
                      v-model="model.model"
                      placeholder="模型名称 (如: gpt-4)"
                      class="model-input"
                      @click.stop
                    />
                  </div>
                  <div v-if="selectedTextIndex === index" class="active-badge">✓ 当前使用</div>
                </div>
              </div>
            </div>
            
            <!-- 图片模型配置 -->
            <div class="config-section">
              <div class="section-title">
                <h3>🎨 图片模型（生成图片）</h3>
                <button class="add-btn" @click="addImageModel">+ 添加模型</button>
              </div>
              
              <div v-if="imageModels.length === 0" class="empty-state">
                暂无配置，点击"添加模型"开始配置
              </div>
              
              <div v-else class="models-list">
                <div
                  v-for="(model, index) in imageModels"
                  :key="index"
                  class="model-card"
                  :class="{ active: selectedImageIndex === index }"
                  @click="selectedImageIndex = index"
                >
                  <div class="model-header">
                    <input
                      v-model="model.name"
                      placeholder="配置名称"
                      class="model-name-input"
                      @click.stop
                    />
                    <button class="delete-btn" @click.stop="deleteImageModel(index)">🗑️</button>
                  </div>
                  <div class="model-fields">
                    <input
                      v-model="model.url"
                      placeholder="API URL"
                      class="model-input"
                      @click.stop
                    />
                    <input
                      v-model="model.apiKey"
                      type="password"
                      placeholder="API Key"
                      class="model-input"
                      @click.stop
                    />
                    <input
                      v-model="model.model"
                      placeholder="模型名称 (如: dall-e-3)"
                      class="model-input"
                      @click.stop
                    />
                  </div>
                  <div v-if="selectedImageIndex === index" class="active-badge">✓ 当前使用</div>
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
    url: '',
    apiKey: '',
    model: ''
  })
}

const addImageModel = () => {
  imageModels.value.push({
    name: `图片模型 ${imageModels.value.length + 1}`,
    url: '',
    apiKey: '',
    model: ''
  })
}

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
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 16px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 2px solid #f0f0f0;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
  transition: color 0.3s;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.config-section {
  margin-bottom: 2rem;
}

.config-section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-title h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.add-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #999;
  background: #f9f9f9;
  border-radius: 8px;
  border: 2px dashed #ddd;
}

.models-list {
  display: grid;
  gap: 1rem;
}

.model-card {
  background: #f9f9f9;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.model-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.model-card.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-color: #667eea;
  border-width: 3px;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.model-name-input {
  flex: 1;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  background: transparent;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background 0.3s;
}

.model-name-input:focus {
  outline: none;
  background: white;
}

.delete-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  transition: transform 0.2s;
}

.delete-btn:hover {
  transform: scale(1.2);
}

.model-fields {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.model-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  background: white;
  transition: border-color 0.3s;
}

.model-input:focus {
  outline: none;
  border-color: #667eea;
}

.active-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem 2rem;
  border-top: 2px solid #f0f0f0;
}

.btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 8px;
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

/* 过渡动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9);
}
</style>