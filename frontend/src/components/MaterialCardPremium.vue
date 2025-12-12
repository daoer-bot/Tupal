<template>
  <div
    class="material-card-premium glass-card-premium aurora-glow float-element"
    :data-material-id="material.id"
    @click="$emit('click', material)"
    :style="{
      '--card-accent': getTypeColor(material.type),
      '--card-glow': getTypeGlow(material.type)
    }"
  >
    <!-- 卡片头部 -->
    <div class="card-header">
      <div class="type-indicator" :class="`type-${material.type}`">
        <component :is="getTypeIcon(material.type)" :size="16" />
        <span>{{ getTypeName(material.type) }}</span>
      </div>
      
      <div class="card-actions" @click.stop>
        <button 
          class="action-btn edit-btn" 
          @click="$emit('edit', material)"
          title="编辑"
        >
          <Pencil :size="14" />
        </button>
        <button 
          class="action-btn delete-btn" 
          @click="$emit('delete', material)"
          title="删除"
        >
          <Trash2 :size="14" />
        </button>
      </div>
    </div>
    
    <!-- 卡片内容 -->
    <div class="card-content">
      <h3 class="material-name">{{ material.name }}</h3>
      <p class="material-description" v-if="material.description">
        {{ material.description }}
      </p>
      
      <!-- 预览区域 -->
      <div class="preview-container">
        <div v-if="material.type === 'text'" class="preview-text">
          <div class="text-content">{{ getTextPreview(material.content) }}</div>
          <div class="text-stats">
            <span class="stat-item">
              <FileText :size="12" />
              {{ getTextLength(material.content) }} 字
            </span>
          </div>
        </div>
        
        <div v-else-if="material.type === 'image'" class="preview-image">
          <img :src="material.content.url" :alt="material.name" loading="lazy" />
          <div class="image-overlay">
            <span class="image-type">{{ getImageType(material.content.url) }}</span>
          </div>
        </div>
        
        <div v-else-if="material.type === 'reference'" class="preview-reference">
          <div class="reference-preview-card">
            <div class="reference-header">
              <BookOpen :size="16" />
              <span>参考素材</span>
            </div>
            <div class="reference-content">
              <div class="reference-type">
                <span class="reference-label">类型：</span>
                <span class="reference-value">{{ material.content.reference_type || '未设置' }}</span>
              </div>
              <div v-if="material.content.account" class="reference-account">
                <span class="reference-label">账号：</span>
                <span class="reference-value">{{ material.content.account }}</span>
              </div>
              <div v-if="material.content.content" class="reference-desc">
                {{ getTextPreview(material.content.content) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 卡片底部 -->
    <div class="card-footer">
      <div class="footer-left">
        <div class="category-tag">
        </div>
        
        <div class="tags-container" v-if="material.tags && material.tags.length > 0">
          <span 
            v-for="tag in material.tags.slice(0, 2)" 
            :key="tag"
            class="tag-item"
          >
            {{ tag }}
          </span>
          <span v-if="material.tags.length > 2" class="tag-more">
            +{{ material.tags.length - 2 }}
          </span>
        </div>
      </div>
      
      <div class="footer-right">
        <div class="update-time" :title="formatFullDate(material.updated_at)">
          {{ formatRelativeTime(material.updated_at) }}
        </div>
      </div>
    </div>
    
    <!-- 悬停效果层 -->
    <div class="hover-overlay">
      <div class="hover-content">
        <div class="hover-icon">
          <component :is="getTypeIcon(material.type)" :size="24" />
        </div>
        <span class="hover-text">点击查看详情</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  FileText,
  Image,
  BookOpen,
  Pencil,
  Trash2
} from 'lucide-vue-next'
import type { Material } from '../services/materialApi'
import type { Component } from 'vue'

const props = defineProps<{
  material: Material
}>()

const emit = defineEmits<{
  click: [material: Material]
  edit: [material: Material]
  delete: [material: Material]
}>()

const getTypeIcon = (type: string): Component => {
  const icons: Record<string, Component> = {
    text: FileText,
    image: Image,
    reference: BookOpen
  }
  return icons[type] || FileText
}

const getTypeName = (type: string): string => {
  const names: Record<string, string> = {
    text: '文本素材',
    image: '图片素材',
    reference: '参考素材'
  }
  return names[type] || type
}

const getTypeColor = (type: string): string => {
  const colors: Record<string, string> = {
    text: '#6366f1',
    image: '#ec4899',
    reference: '#8b5cf6'
  }
  return colors[type] || '#6366f1'
}

const getTypeGlow = (type: string): string => {
  const glows: Record<string, string> = {
    text: 'rgba(99, 102, 241, 0.3)',
    image: 'rgba(236, 72, 153, 0.3)',
    reference: 'rgba(139, 92, 246, 0.3)'
  }
  return glows[type] || 'rgba(99, 102, 241, 0.3)'
}

const getTextPreview = (content: any): string => {
  const text = typeof content === 'string' ? content : content.text || ''
  return text.length > 120 ? text.substring(0, 120) + '...' : text
}

const getTextLength = (content: any): number => {
  const text = typeof content === 'string' ? content : content.text || ''
  return text.length
}

const getImageType = (url: string): string => {
  const extension = url.split('.').pop()?.toLowerCase()
  const types: Record<string, string> = {
    'jpg': 'JPG',
    'jpeg': 'JPEG',
    'png': 'PNG',
    'gif': 'GIF',
    'webp': 'WEBP',
    'svg': 'SVG'
  }
  return types[extension || ''] || '图片'
}

const formatRelativeTime = (dateStr: string): string => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const formatFullDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.material-card-premium {
  padding: 1.5rem;
  cursor: pointer;
  position: relative;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 8px 32px rgba(31, 38, 135, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

.material-card-premium::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(
    circle at var(--card-accent),
    var(--card-glow) 0%,
    transparent 70%
  );
  opacity: 0;
  transition: opacity 0.4s ease;
  z-index: -1;
}

.material-card-premium:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 
    0 20px 60px rgba(31, 38, 135, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.material-card-premium:hover::before {
  opacity: 1;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.type-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.type-indicator.type-text {
  color: #6366f1;
  border-color: rgba(99, 102, 241, 0.3);
}

.type-indicator.type-image {
  color: #ec4899;
  border-color: rgba(236, 72, 153, 0.3);
}

.type-indicator.type-style {
  color: #8b5cf6;
  border-color: rgba(139, 92, 246, 0.3);
}

.type-indicator.type-product {
  color: #10b981;
  border-color: rgba(16, 185, 129, 0.3);
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.edit-btn:hover {
  color: #6366f1;
}

.delete-btn:hover {
  color: #ef4444;
}

/* 卡片内容 */
.card-content {
  margin-bottom: 1.5rem;
}

.material-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.material-description {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0 0 1rem 0;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 预览容器 */
.preview-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.preview-text {
  font-size: 0.85rem;
  line-height: 1.6;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.text-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.preview-image {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
}

.preview-image img {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
}

.preview-reference {
  font-size: 0.85rem;
}

.reference-preview-card {
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 8px;
  padding: 1rem;
}

.reference-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  color: #8b5cf6;
  font-weight: 600;
}

.reference-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.reference-type,
.reference-account {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.reference-label {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.reference-value {
  color: var(--text-primary);
  font-weight: 500;
}

.reference-desc {
  color: var(--text-secondary);
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  margin-top: 0.5rem;
}

/* 卡片底部 */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

.footer-left {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
}

.category-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.05);
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  width: fit-content;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-item {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 500;
}

.tag-more {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-tertiary);
  padding: 0.25rem 0.5rem;
  border-radius: 99px;
  font-size: 0.7rem;
}

.footer-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.update-time {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  white-space: nowrap;
}

/* 悬停效果 */
.hover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 24px;
}

.material-card-premium:hover .hover-overlay {
  opacity: 1;
}

.hover-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: white;
}

.hover-icon {
  font-size: 2rem;
}

.hover-text {
  font-size: 0.9rem;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .material-card-premium {
    padding: 1.25rem;
  }
  
  .card-footer {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .footer-right {
    align-items: flex-start;
  }
}
</style>