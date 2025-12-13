<template>
  <div class="template-card" @click="handleClick">
    <!-- 预览图区域 -->
    <div class="template-preview">
      <img
        v-if="template.preview_image"
        :src="template.preview_image"
        :alt="template.name"
        class="preview-image"
      />
      <div v-else class="preview-placeholder">
        <component :is="getTypeIcon" :size="32" class="placeholder-icon" />
      </div>
      
      <!-- 模板类型标签 -->
      <div class="template-type-badge" :class="template.type">
        {{ template.type === 'system' ? 'OFFICIAL' : 'CUSTOM' }}
      </div>
    </div>
    
    <!-- 模板信息 -->
    <div class="template-info">
      <h3 class="template-name">{{ template.name }}</h3>
      <p class="template-description">{{ template.description || '暂无描述' }}</p>
      
      <!-- 标签 -->
      <div v-if="template.tags && template.tags.length > 0" class="template-tags">
        <span
          v-for="tag in displayTags"
          :key="tag"
          class="tag"
        >
          #{{ tag }}
        </span>
        <span v-if="template.tags.length > 3" class="tag-more">
          +{{ template.tags.length - 3 }}
        </span>
      </div>
      
      <!-- 操作按钮 -->
      <div class="template-actions">
        <button
          class="btn-use"
          @click.stop="handleUse"
        >
          <Sparkles :size="14" />
          <span>LOAD TEMPLATE</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Sparkles, FileText, Image, Bookmark } from 'lucide-vue-next'
import type { Template } from '../services/templateApi'

interface Props {
  template: Template
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'use': [template: Template]
  'click': [template: Template]
}>()

// 根据模板类型获取图标
const getTypeIcon = computed(() => {
  if (props.template.content_structure?.layout === 'image') {
    return Image
  }
  if (props.template.type === 'user') {
    return Bookmark
  }
  return FileText
})

// 显示的标签（最多3个）
const displayTags = computed(() => {
  return props.template.tags?.slice(0, 3) || []
})

// 点击卡片
const handleClick = () => {
  emit('click', props.template)
}

// 使用模板
const handleUse = () => {
  emit('use', props.template)
}
</script>

<style scoped>
.template-card {
  display: flex;
  flex-direction: column;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
  border: 1px solid rgba(0,0,0,0.05);
  box-shadow: 0 4px 10px rgba(0,0,0,0.02);
}

.template-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(99, 102, 241, 0.15);
}

/* 预览区域 */
.template-preview {
  position: relative;
  width: 100%;
  height: 140px;
  overflow: hidden;
  background: #f8fafc;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.template-card:hover .preview-image {
  transform: scale(1.05);
}

.preview-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
}

.placeholder-icon {
  color: #cbd5e1;
}

/* 类型标签 */
.template-type-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  backdrop-filter: blur(4px);
}

.template-type-badge.system {
  background: rgba(255, 255, 255, 0.9);
  color: var(--primary-color);
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.template-type-badge.user {
  background: rgba(0, 0, 0, 0.8);
  color: white;
}

/* 信息区域 */
.template-info {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
}

.template-name {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.template-description {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-tertiary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.5rem;
}

/* 标签 */
.template-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.tag {
  padding: 2px 8px;
  background: #f1f5f9;
  color: var(--text-secondary);
  font-size: 11px;
  border-radius: 4px;
  font-weight: 600;
}

.tag-more {
  padding: 2px 6px;
  color: var(--text-tertiary);
  font-size: 11px;
}

/* 操作按钮 */
.template-actions {
  margin-top: auto;
  padding-top: 1rem;
}

.btn-use {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3);
}

.btn-use:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(99, 102, 241, 0.4);
}

.btn-use:active {
  transform: translateY(1px);
}

/* 响应式 */
@media (max-width: 640px) {
  .template-preview {
    height: 120px;
  }
  
  .template-info {
    padding: 1rem;
  }
}
</style>