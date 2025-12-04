<template>
  <div class="material-card" @click="$emit('click', material)">
    <div class="material-header">
      <div class="material-type-badge" :class="`type-${material.type}`">
        <component :is="getTypeIcon(material.type)" :size="14" />
        <span>{{ getTypeName(material.type) }}</span>
      </div>
      <div class="material-actions" @click.stop>
        <button class="btn-icon" @click="$emit('edit', material)" title="编辑">
          <Pencil :size="16" />
        </button>
        <button class="btn-icon" @click="$emit('delete', material)" title="删除">
          <Trash2 :size="16" />
        </button>
      </div>
    </div>

    <div class="material-content">
      <h3 class="material-name">{{ material.name }}</h3>
      <p class="material-description" v-if="material.description">
        {{ material.description }}
      </p>
      
      <!-- 预览内容 -->
      <div class="material-preview">
        <div v-if="material.type === 'text'" class="preview-text">
          {{ getTextPreview(material.content) }}
        </div>
        <div v-else-if="material.type === 'image'" class="preview-image">
          <img :src="material.content.url" :alt="material.name" />
        </div>
        <div v-else-if="material.type === 'reference'" class="preview-reference">
          <div class="reference-desc">{{ getTextPreview(material.content.content) }}</div>
          <div class="reference-type" v-if="material.content.reference_type">
            类型：{{ material.content.reference_type }}
          </div>
        </div>
      </div>
    </div>

    <div class="material-footer">
      <div class="material-tags" v-if="material.tags && material.tags.length > 0">
        <span v-for="tag in material.tags.slice(0, 3)" :key="tag" class="tag">
          {{ tag }}
        </span>
        <span v-if="material.tags.length > 3" class="tag-more">
          +{{ material.tags.length - 3 }}
        </span>
      </div>
    </div>

    <div class="material-meta">
      <span class="meta-date">{{ formatDate(material.updated_at) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FileText, Image, BookOpen, Pencil, Trash2 } from 'lucide-vue-next'
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
    text: '文本',
    image: '图片',
    reference: '参考'
  }
  return names[type] || type
}

const getTextPreview = (content: any): string => {
  const text = typeof content === 'string' ? content : content.text || ''
  return text.length > 100 ? text.substring(0, 100) + '...' : text
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    return '今天'
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}
</script>

<style scoped>
.material-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.material-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.material-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.material-type-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.type-text {
  background: #dbeafe;
  color: #1e40af;
}

.type-image {
  background: #fce7f3;
  color: #be185d;
}

.type-reference {
  background: #f3e8ff;
  color: #7e22ce;
}

.material-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  opacity: 0.6;
  transition: all 0.2s;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.btn-icon:hover {
  opacity: 1;
  background: #f3f4f6;
  color: #111827;
}

.material-content {
  margin-bottom: 12px;
}

.material-name {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.material-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 12px 0;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  word-break: break-word;
}

.material-preview {
  background: #f9fafb;
  border-radius: 6px;
  padding: 12px;
  font-size: 14px;
}

.preview-text {
  color: #374151;
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  word-break: break-word;
}

.preview-image img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
}

.preview-reference {
  color: #7e22ce;
  font-weight: 500;
}

.preview-reference .reference-desc {
  color: #374151;
  margin-bottom: 8px;
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  word-break: break-word;
}

.preview-reference .reference-type {
  color: #6b7280;
  font-size: 12px;
}

.material-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 8px;
}

.material-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.tag {
  font-size: 11px;
  background: #e5e7eb;
  color: #4b5563;
  padding: 2px 8px;
  border-radius: 10px;
}

.tag-more {
  font-size: 11px;
  color: #6b7280;
}

.material-meta {
  text-align: right;
}

.meta-date {
  font-size: 12px;
  color: #9ca3af;
}
</style>