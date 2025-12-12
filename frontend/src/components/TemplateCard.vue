<template>
  <div class="template-card glass-panel" @click="handleClick">
    <!-- 预览图区域 -->
    <div class="template-preview">
      <img 
        v-if="template.preview_image" 
        :src="template.preview_image" 
        :alt="template.name"
        class="preview-image"
      />
      <div v-else class="preview-placeholder">
        <component :is="getTypeIcon" :size="48" class="placeholder-icon" />
      </div>
      
      <!-- 模板类型标签 -->
      <div class="template-type-badge" :class="template.type">
        {{ template.type === 'official' ? '官方' : '我的' }}
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
          {{ tag }}
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
          <Sparkles :size="16" />
          <span>使用模板</span>
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
  if (props.template.type === 'personal') {
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
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.template-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(99, 102, 241, 0.15);
  border-color: rgba(99, 102, 241, 0.3);
}

/* 预览区域 */
.template-preview {
  position: relative;
  width: 100%;
  height: 160px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
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
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.08));
}

.placeholder-icon {
  color: rgba(99, 102, 241, 0.4);
}

/* 类型标签 */
.template-type-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(8px);
}

.template-type-badge.official {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.9), rgba(139, 92, 246, 0.9));
  color: white;
}

.template-type-badge.personal {
  background: rgba(255, 255, 255, 0.9);
  color: #6366f1;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

/* 信息区域 */
.template-info {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.template-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.template-description {
  margin: 0;
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.625rem;
}

/* 标签 */
.template-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  margin-top: 0.25rem;
}

.tag {
  padding: 2px 8px;
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
  font-size: 12px;
  border-radius: 4px;
  font-weight: 500;
}

.tag-more {
  padding: 2px 8px;
  background: rgba(100, 116, 139, 0.1);
  color: #64748b;
  font-size: 12px;
  border-radius: 4px;
}

/* 操作按钮 */
.template-actions {
  margin-top: auto;
  padding-top: 0.75rem;
}

.btn-use {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
}

.btn-use:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}

.btn-use:active {
  transform: translateY(0);
}

/* 响应式 */
@media (max-width: 640px) {
  .template-preview {
    height: 140px;
  }
  
  .template-info {
    padding: 0.875rem;
  }
  
  .template-name {
    font-size: 0.9375rem;
  }
  
  .template-description {
    font-size: 0.8125rem;
  }
}
</style>