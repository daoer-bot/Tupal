<template>
  <div class="template-creation">
    <div class="creation-header">
      <h2 class="section-title">模板创作</h2>
      <p class="section-subtitle">选择模板快速开始创作</p>
    </div>
    
    <div class="template-selector glass-card-premium">
      <h3>选择创作模板</h3>
      <div class="template-list">
        <div 
          v-for="template in templates" 
          :key="template.id"
          class="template-item"
          :class="{ selected: selectedTemplate?.id === template.id }"
          @click="selectedTemplate = template"
        >
          <div class="template-icon">{{ template.icon }}</div>
          <div class="template-name">{{ template.name }}</div>
        </div>
      </div>
    </div>
    
    <div v-if="selectedTemplate" class="creation-form glass-card-premium">
      <h3>填写创作内容</h3>
      <div class="input-group">
        <label class="input-label">创作主题</label>
        <input 
          v-model="topic" 
          type="text" 
          class="text-input glass-input"
          placeholder="输入你的创作主题..."
        />
      </div>
      
      <button 
        class="btn-3d primary-action"
        @click="handleCreate"
        :disabled="!topic || isCreating"
      >
        <span v-if="isCreating" class="loading-spinner"></span>
        {{ isCreating ? '生成中...' : '开始创作' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const templates = ref([
  { id: 1, name: '穿搭分享', icon: '👗' },
  { id: 2, name: '美食探店', icon: '🍜' },
  { id: 3, name: '旅行攻略', icon: '✈️' },
  { id: 4, name: '好物推荐', icon: '🛍️' }
])

const selectedTemplate = ref<any>(null)
const topic = ref('')
const isCreating = ref(false)

const handleCreate = async () => {
  isCreating.value = true
  // TODO: 实现模板创作逻辑
  setTimeout(() => {
    console.log('创作:', selectedTemplate.value, topic.value)
    isCreating.value = false
  }, 1000)
}
</script>

<style scoped>
.template-creation {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.creation-header {
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

.template-selector {
  padding: 2rem;
  margin-bottom: 2rem;
}

.template-selector h3 {
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.template-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
}

.template-item {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid transparent;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.template-item:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.template-item.selected {
  border-color: var(--primary-color);
  background: rgba(99, 102, 241, 0.1);
}

.template-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.template-name {
  font-size: 0.9rem;
  color: var(--text-primary);
  font-weight: 500;
}

.creation-form {
  padding: 2rem;
}

.creation-form h3 {
  margin-bottom: 1.5rem;
  color: var(--text-primary);
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

.text-input {
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
</style>