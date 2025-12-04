<template>
  <div class="content-collector">
    <div class="collector-header">
      <h2 class="section-title">图文采集器</h2>
      <p class="section-subtitle">从网络采集优质图文内容，快速构建素材库</p>
    </div>
    
    <div class="collector-card glass-card-premium">
      <div class="input-group">
        <label class="input-label">输入内容链接</label>
        <input 
          v-model="contentUrl" 
          type="text" 
          class="url-input glass-input"
          placeholder="粘贴小红书、微博等平台的内容链接..."
        />
      </div>
      
      <button 
        class="btn-3d primary-action"
        @click="handleCollect"
        :disabled="!contentUrl || isCollecting"
      >
        <span v-if="isCollecting" class="loading-spinner"></span>
        {{ isCollecting ? '采集中...' : '开始采集' }}
      </button>
    </div>
    
    <div v-if="collectedContent" class="collected-preview glass-card-premium">
      <h3>采集预览</h3>
      <div class="preview-content">
        <p>{{ collectedContent }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const contentUrl = ref('')
const isCollecting = ref(false)
const collectedContent = ref('')

const handleCollect = async () => {
  isCollecting.value = true
  // TODO: 实现采集逻辑
  setTimeout(() => {
    collectedContent.value = '采集功能开发中...'
    isCollecting.value = false
  }, 1000)
}
</script>

<style scoped>
.content-collector {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.collector-header {
  text-align: center;
  margin-bottom: 2rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.section-subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
}

.collector-card {
  padding: 2rem;
  margin-bottom: 2rem;
}

.input-group {
  margin-bottom: 1.5rem;
}

.input-label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--text-primary);
}

.url-input {
  width: 100%;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  font-size: 0.95rem;
}

.primary-action {
  width: 100%;
  padding: 1rem;
  font-size: 1rem;
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.collected-preview {
  padding: 2rem;
}

.collected-preview h3 {
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.preview-content {
  color: var(--text-secondary);
}
</style>