<template>
  <div v-if="show" class="material-editor-overlay" @click.self="$emit('close')">
    <div class="material-editor">
      <div class="editor-header">
        <h2>{{ isEdit ? '编辑素材' : '添加素材' }}</h2>
        <button class="btn-close" @click="$emit('close')">
          <X :size="20" />
        </button>
      </div>

      <div class="editor-body">
        <form @submit.prevent="handleSubmit">
          <!-- 基本信息 -->
          <div class="form-section">
            <div class="form-group">
              <label>素材名称 *</label>
              <input
                v-model="formData.name"
                type="text"
                placeholder="给素材起个名字"
                required
              />
            </div>
          </div>

          <!-- 图文内容区域 -->
          <div class="form-section">
            <h3>素材内容</h3>
            
            <div class="content-editor mixed-editor">
              <!-- 文本部分 -->
              <div class="form-group">
                <label>文字内容</label>
                <textarea
                  v-model="contentText"
                  placeholder="请输入文字内容..."
                  rows="6"
                ></textarea>
              </div>
              
              <!-- 图片部分 -->
              <div class="form-group">
                <label>图片内容</label>
                <div
                  class="upload-area"
                  :class="{ 'drag-over': isDragging }"
                  @drop.prevent="handleDrop"
                  @dragover.prevent="isDragging = true"
                  @dragleave.prevent="isDragging = false"
                  @click="triggerFileInput"
                >
                  <input
                    ref="fileInput"
                    type="file"
                    accept="image/*"
                    multiple
                    @change="handleFileSelect"
                    style="display: none"
                  />
                  <div class="upload-prompt">
                    <div class="upload-icon">
                      <FolderOpen :size="32" :stroke-width="1.5" />
                    </div>
                    <p>拖拽图片到这里或点击上传</p>
                    <span class="upload-hint">支持多张图片，JPG, PNG, GIF, WEBP 格式</span>
                  </div>
                </div>
                
                <!-- 已上传图片预览 -->
                <div v-if="images.length > 0" class="images-preview">
                  <div
                    v-for="(img, index) in images"
                    :key="index"
                    class="image-item"
                  >
                    <img :src="img" alt="预览" />
                    <button type="button" class="btn-remove-small" @click="removeImage(index)">
                      <X :size="14" />
                    </button>
                  </div>
                </div>
              </div>
              
              <div class="content-hint">
                <span>💡 提示：文字和图片至少填写一项</span>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="editor-actions">
            <button type="button" class="btn btn-secondary" @click="$emit('close')">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? '保存中...' : (isEdit ? '保存' : '创建') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { X, FolderOpen } from 'lucide-vue-next'
import type { Material } from '../services/materialApi'

const props = defineProps<{
  show?: boolean
  material?: Material
}>()

const emit = defineEmits<{
  close: []
  submit: [data: any]
}>()

const isEdit = computed(() => !!props.material)
const loading = ref(false)

// 内容
const contentText = ref('')
const images = ref<string[]>([])

// 图片上传相关
const fileInput = ref<HTMLInputElement>()
const isDragging = ref(false)

// 表单数据
const formData = reactive({
  name: ''
})

// 监听 show 变化，重置或初始化表单
watch(() => props.show, (newShow) => {
  if (newShow) {
    if (props.material) {
      // 编辑模式：加载现有数据
      formData.name = props.material.name
      contentText.value = props.material.content?.text || ''
      images.value = props.material.content?.images ? [...props.material.content.images] : []
    } else {
      // 创建模式：重置表单
      formData.name = ''
      contentText.value = ''
      images.value = []
    }
  }
}, { immediate: true })

// 触发文件选择
function triggerFileInput() {
  fileInput.value?.click()
}

// 处理文件选择
function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files) {
    Array.from(files).forEach(file => {
      if (file.type.startsWith('image/')) {
        processImageFile(file)
      }
    })
  }
  // 清空 input 以便重复选择同一文件
  if (target) target.value = ''
}

// 处理拖拽上传
function handleDrop(event: DragEvent) {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files) {
    Array.from(files).forEach(file => {
      if (file.type.startsWith('image/')) {
        processImageFile(file)
      }
    })
  }
}

// 处理图片文件
function processImageFile(file: File) {
  const reader = new FileReader()
  reader.onload = (e) => {
    const dataUrl = e.target?.result as string
    if (dataUrl && !images.value.includes(dataUrl)) {
      images.value.push(dataUrl)
    }
  }
  reader.readAsDataURL(file)
}

// 移除单张图片
function removeImage(index: number) {
  images.value.splice(index, 1)
}

async function handleSubmit() {
  const hasText = contentText.value.trim()
  const hasImages = images.value.length > 0
  
  if (!hasText && !hasImages) {
    alert('请至少输入文字或上传图片')
    return
  }
  
  if (!formData.name.trim()) {
    alert('请输入素材名称')
    return
  }
  
  loading.value = true
  
  // 构建内容
  const content: any = {}
  if (hasText) {
    content.text = contentText.value
  }
  if (hasImages) {
    content.images = [...images.value]
  }

  // 提交数据 - 统一使用 mixed 类型
  emit('submit', {
    name: formData.name,
    type: 'mixed',
    content: content,
    tags: [],
    description: '',
    material_id: props.material?.id
  })

  setTimeout(() => {
    loading.value = false
  }, 1000)
}
</script>

<style scoped>
.material-editor-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.material-editor {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.editor-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.btn-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #6b7280;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #f3f4f6;
  color: #111827;
}

.editor-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.form-section {
  margin-bottom: 24px;
}

.form-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: #111827;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
}

/* 图文混合编辑样式 */
.mixed-editor {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 图片上传区域 */
.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #f9fafb;
}

.upload-area:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.upload-area.drag-over {
  border-color: #3b82f6;
  background: #dbeafe;
}

.upload-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-icon {
  color: #9ca3af;
  display: flex;
  justify-content: center;
}

.upload-prompt p {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.upload-hint {
  font-size: 12px;
  color: #6b7280;
}

/* 图片预览网格 */
.images-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-remove-small {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.9);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.image-item:hover .btn-remove-small {
  opacity: 1;
}

.btn-remove-small:hover {
  background: #dc2626;
}

.content-hint {
  padding: 12px 16px;
  background: #f0f9ff;
  border-radius: 8px;
  font-size: 13px;
  color: #0369a1;
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
  margin: 0 -24px -24px;
  border-radius: 0 0 12px 12px;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #f9fafb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-primary:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}
</style>