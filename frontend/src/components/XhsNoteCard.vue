<template>
  <article class="xhs-note-card glass-panel" @click="handleClick">
    <!-- 封面图 -->
    <div class="note-cover">
      <img 
        v-if="coverImage" 
        :src="coverImage" 
        :alt="note.title"
        loading="lazy"
        @error="handleImageError"
      />
      <div v-else class="cover-placeholder">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 19.5h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5z" />
        </svg>
      </div>
      <!-- 视频标识 -->
      <div v-if="isVideo" class="video-badge">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
        </svg>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="note-content">
      <h3 class="note-title">{{ note.title || '无标题' }}</h3>
      <p v-if="note.desc" class="note-desc">{{ truncatedDesc }}</p>
      
      <!-- 用户信息 -->
      <div class="note-user" v-if="note.user">
        <img 
          v-if="note.user.avatar" 
          :src="note.user.avatar" 
          :alt="note.user.nickname"
          class="user-avatar"
          @error="handleAvatarError"
        />
        <div v-else class="avatar-placeholder">
          <span>{{ note.user.nickname?.charAt(0) || '?' }}</span>
        </div>
        <span class="user-name">{{ note.user.nickname || '未知用户' }}</span>
      </div>

      <!-- 互动数据 -->
      <div class="note-stats">
        <span class="stat-item" v-if="note.liked_count !== undefined">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
          </svg>
          {{ formatCount(note.liked_count) }}
        </span>
        <span class="stat-item" v-if="note.collected_count !== undefined">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0z" />
          </svg>
          {{ formatCount(note.collected_count) }}
        </span>
        <span class="stat-item" v-if="note.comment_count !== undefined">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
          </svg>
          {{ formatCount(note.comment_count) }}
        </span>
      </div>

      <!-- 标签 -->
      <div class="note-tags" v-if="note.tag_list && note.tag_list.length > 0">
        <span v-for="tag in displayTags" :key="tag" class="tag">{{ tag }}</span>
        <span v-if="note.tag_list.length > 3" class="tag more">+{{ note.tag_list.length - 3 }}</span>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="note-actions">
      <button class="action-btn" @click.stop="handleCollect" title="收藏为素材">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
      </button>
      <button class="action-btn" @click.stop="handleOpenOriginal" title="查看原文">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
        </svg>
      </button>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { XhsNote } from '../services/xhsApi'

interface Props {
  note: XhsNote
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'click', note: XhsNote): void
  (e: 'collect', note: XhsNote): void
}>()

// 计算属性
const coverImage = computed(() => {
  if (props.note.image_list && props.note.image_list.length > 0) {
    return props.note.image_list[0].url
  }
  return null
})

const isVideo = computed(() => {
  return props.note.type === 'video' || !!props.note.video_url
})

const truncatedDesc = computed(() => {
  if (!props.note.desc) return ''
  return props.note.desc.length > 80 
    ? props.note.desc.substring(0, 80) + '...' 
    : props.note.desc
})

const displayTags = computed(() => {
  if (!props.note.tag_list) return []
  return props.note.tag_list.slice(0, 3)
})

// 方法
const formatCount = (count: number | string): string => {
  const num = typeof count === 'string' ? parseInt(count) : count
  if (isNaN(num)) return '0'
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return String(num)
}

const handleClick = () => {
  emit('click', props.note)
}

const handleCollect = () => {
  emit('collect', props.note)
}

const handleOpenOriginal = () => {
  const url = `https://www.xiaohongshu.com/explore/${props.note.note_id}`
  window.open(url, '_blank')
}

const handleImageError = (e: Event) => {
  const target = e.target as HTMLImageElement
  target.style.display = 'none'
}

const handleAvatarError = (e: Event) => {
  const target = e.target as HTMLImageElement
  target.style.display = 'none'
}
</script>

<style scoped>
.xhs-note-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.xhs-note-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.xhs-note-card:hover .note-actions {
  opacity: 1;
}

/* 封面图 */
.note-cover {
  position: relative;
  width: 100%;
  padding-top: 100%; /* 1:1 比例 */
  background: linear-gradient(135deg, #f5f5f5, #e8e8e8);
  overflow: hidden;
}

.note-cover img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.xhs-note-card:hover .note-cover img {
  transform: scale(1.05);
}

.cover-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ccc;
}

.cover-placeholder svg {
  width: 48px;
  height: 48px;
}

.video-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.video-badge svg {
  width: 16px;
  height: 16px;
}

/* 内容区 */
.note-content {
  padding: 1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.note-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.note-desc {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 用户信息 */
.note-user {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: auto;
}

.user-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff9aa2, #ffb17a);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
}

.user-name {
  font-size: 0.85rem;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 互动数据 */
.note-stats {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: var(--text-tertiary);
}

.stat-item svg {
  width: 14px;
  height: 14px;
}

/* 标签 */
.note-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tag {
  padding: 0.25rem 0.5rem;
  background: rgba(255, 154, 162, 0.1);
  color: var(--primary-color);
  border-radius: 999px;
  font-size: 0.75rem;
}

.tag.more {
  background: rgba(0, 0, 0, 0.05);
  color: var(--text-tertiary);
}

/* 操作按钮 */
.note-actions {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-btn:hover {
  background: var(--primary-color);
  color: white;
  transform: scale(1.1);
}

.action-btn svg {
  width: 16px;
  height: 16px;
}
</style>