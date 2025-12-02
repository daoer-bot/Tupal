<template>
  <div class="material-editor-overlay" @click.self="$emit('close')">
    <div class="material-editor">
      <div class="editor-header">
        <h2>{{ isEdit ? '编辑素材' : '创建素材' }}</h2>
        <button class="btn-close" @click="$emit('close')">
          <X :size="20" />
        </button>
      </div>

      <div class="editor-body">
        <form @submit.prevent="handleSubmit">
          <!-- 场景选择器 (仅在创建时显示) -->
          <div class="form-section" v-if="!isEdit">
            <h3>选择素材类型</h3>
            <div class="scene-grid">
              <div
                v-for="scene in scenes"
                :key="scene.category"
                class="scene-card"
                :class="{ active: formData.category === scene.category }"
                @click="selectScene(scene)"
              >
                <div class="scene-icon">
                  <component :is="scene.icon" :size="32" :stroke-width="1.5" />
                </div>
                <div class="scene-info">
                  <div class="scene-name">{{ scene.name }}</div>
                  <div class="scene-desc">{{ scene.desc }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 基本信息 -->
          <div class="form-section">
            <h3>基本信息</h3>
            
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

          <!-- 内容类型选择 -->
          <div class="form-section">
            <h3>内容类型</h3>
            <div class="content-type-tabs">
              <button
                type="button"
                class="tab-btn"
                :class="{ active: contentType === 'text' }"
                @click="contentType = 'text'"
              >
                <FileText :size="18" />
                <span>文字内容</span>
              </button>
              <button
                type="button"
                class="tab-btn"
                :class="{ active: contentType === 'image' }"
                @click="contentType = 'image'"
              >
                <Image :size="18" />
                <span>图片内容</span>
              </button>
            </div>
          </div>

          <!-- 内容区域 -->
          <div class="form-section">
            <h3>素材内容</h3>
            
            <!-- 文本输入 -->
            <div v-if="contentType === 'text'" class="content-editor">
              <div class="form-group">
                <label>文本内容 *</label>
                <textarea
                  v-model="contentText"
                  placeholder="请输入内容..."
                  rows="10"
                  required
                ></textarea>
              </div>
            </div>

            <!-- 图片上传 -->
            <div v-else class="content-editor">
              <div class="form-group">
                <label>上传图片 *</label>
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
                    @change="handleFileSelect"
                    style="display: none"
                  />
                  <div v-if="!imagePreview" class="upload-prompt">
                    <div class="upload-icon">
                      <FolderOpen :size="48" :stroke-width="1.5" />
                    </div>
                    <p>拖拽图片到这里或点击上传</p>
                    <span class="upload-hint">支持 JPG, PNG, GIF, WEBP 格式</span>
                  </div>
                  <div v-else class="image-preview-box">
                    <img :src="imagePreview" alt="预览" />
                    <button type="button" class="btn-remove" @click.stop="removeImage">
                      <X :size="16" />
                      <span>移除</span>
                    </button>
                  </div>
                </div>
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
import { ref, reactive, computed } from 'vue'
import { X, FileText, Image, FolderOpen, Film, ZoomIn, BarChart3, Scale, Type } from 'lucide-vue-next'
import type { Material } from '../services/materialApi'
import type { Component } from 'vue'

const props = defineProps<{
  material?: Material
}>()

const emit = defineEmits<{
  close: []
  submit: [data: any]
}>()

const isEdit = computed(() => !!props.material)
const loading = ref(false)

// 内容类型（text 或 image）
const contentType = ref<'text' | 'image'>('text')

// 统一的内容文本
const contentText = ref('')

// 图片上传相关
const fileInput = ref<HTMLInputElement>()
const imagePreview = ref('')
const imageFile = ref<File>()
const isDragging = ref(false)

// 场景定义 - 5大核心类型
const scenes = [
  { name: '视觉核心素材', category: '视觉核心素材', type: 'image', icon: Film, desc: '封面图、场景图、生活片段' },
  { name: '细节展示素材', category: '细节展示素材', type: 'image', icon: ZoomIn, desc: '产品特写、使用效果、材质纹理' },
  { name: '信息结构素材', category: '信息结构素材', type: 'image', icon: BarChart3, desc: '表格、流程图、结构图、截图' },
  { name: '对比验证素材', category: '对比验证素材', type: 'image', icon: Scale, desc: '前后对比、数据验证、测评参数' },
  { name: '文案配图素材', category: '文案配图素材', type: 'text', icon: Type, desc: '金句、标题、引导文案' },
] as const

// 表单数据
const formData = reactive({
  name: '',
  type: 'image' as 'text' | 'image',
  category: '封面素材',
  content: {} as any
})

// 初始化表单数据
if (props.material) {
  formData.name = props.material.name
  // 只接受 text 和 image 类型，其他类型默认为 text
  formData.type = (props.material.type === 'text' || props.material.type === 'image')
    ? props.material.type
    : 'text'
  formData.category = props.material.category
  formData.content = { ...props.material.content }

  // 设置内容类型和内容
  if (props.material.type === 'text' && props.material.content.text) {
    contentType.value = 'text'
    contentText.value = props.material.content.text
  } else if (props.material.type === 'image' && props.material.content.url) {
    contentType.value = 'image'
    imagePreview.value = props.material.content.url
  }
} else {
  // 默认选中第一个场景
  selectScene(scenes[0])
}

// 选择场景
function selectScene(scene: typeof scenes[number]) {
  formData.category = scene.category
  formData.type = scene.type as any
  initContentByType(scene.type)
}

function initContentByType(type: string) {
  // 清空内容
  formData.content = {}
  contentText.value = ''
  imagePreview.value = ''
  imageFile.value = undefined
}

// 触发文件选择
function triggerFileInput() {
  fileInput.value?.click()
}

// 处理文件选择
function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    processImageFile(file)
  }
}

// 处理拖拽上传
function handleDrop(event: DragEvent) {
  isDragging.value = false
  const file = event.dataTransfer?.files[0]
  if (file && file.type.startsWith('image/')) {
    processImageFile(file)
  }
}

// 处理图片文件
function processImageFile(file: File) {
  imageFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

// 移除图片
function removeImage() {
  imagePreview.value = ''
  imageFile.value = undefined
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function handleSubmit() {
  loading.value = true

  // 根据内容类型包装内容
  let content: any = {}
  
  if (contentType.value === 'text') {
    // 文本内容
    if (!contentText.value.trim()) {
      alert('请输入文本内容')
      loading.value = false
      return
    }
    content = { text: contentText.value }
    formData.type = 'text'
  } else {
    // 图片内容 - 使用base64编码的图片数据
    if (!imagePreview.value) {
      alert('请上传图片')
      loading.value = false
      return
    }
    content = { url: imagePreview.value, description: '' }
    formData.type = 'image'
  }

  // 提交数据，确保可选字段有默认值
  emit('submit', {
    name: formData.name,
    type: formData.type,
    category: formData.category,
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
  max-width: 900px;
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
  margin-bottom: 32px;
}

.form-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: #111827;
}

/* 场景选择网格 */
.scene-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.scene-card {
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.scene-card:hover {
  border-color: #93c5fd;
  background: #f0f9ff;
}

.scene-card.active {
  border-color: #3b82f6;
  background: #eff6ff;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.scene-icon {
  margin-bottom: 12px;
  color: #3b82f6;
  display: flex;
  justify-content: center;
}

.scene-name {
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
}

.scene-desc {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
}

/* 内容类型标签 */
.content-type-tabs {
  display: flex;
  gap: 12px;
}

.tab-btn {
  flex: 1;
  padding: 12px 20px;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.tab-btn:hover {
  border-color: #93c5fd;
  background: #f0f9ff;
}

.tab-btn.active {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #3b82f6;
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
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
}

/* 图片上传区域 */
.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 40px;
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
  gap: 12px;
}

.upload-icon {
  color: #9ca3af;
  display: flex;
  justify-content: center;
}

.upload-prompt p {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #374151;
}

.upload-hint {
  font-size: 13px;
  color: #6b7280;
}

.image-preview-box {
  position: relative;
  display: inline-block;
  max-width: 100%;
}

.image-preview-box img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 6px;
  object-fit: contain;
}

.btn-remove {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(239, 68, 68, 0.9);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-remove:hover {
  background: #dc2626;
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