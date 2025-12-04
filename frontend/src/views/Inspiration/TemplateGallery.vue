<template>
  <div class="template-gallery">
    <div class="gallery-header">
      <h2 class="section-title">模板广场</h2>
      <p class="section-subtitle">精选优质模板，快速启动创作</p>
    </div>
    
    <div class="template-filters">
      <button 
        v-for="category in categories" 
        :key="category"
        class="filter-btn"
        :class="{ active: selectedCategory === category }"
        @click="selectedCategory = category"
      >
        {{ category }}
      </button>
    </div>
    
    <div class="template-grid">
      <div v-for="template in filteredTemplates" :key="template.id" class="template-card glass-card-premium">
        <div class="template-preview">
          <div class="preview-placeholder">{{ template.icon }}</div>
        </div>
        <div class="template-info">
          <h3>{{ template.name }}</h3>
          <p>{{ template.description }}</p>
          <button class="btn-ghost" @click="useTemplate(template)">使用模板</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const categories = ['全部', '系统模板', '灵感模板', '我的模板']
const selectedCategory = ref('全部')

const templates = ref([
  { id: 1, name: '穿搭分享', description: '时尚穿搭推荐模板', icon: '👗', category: '系统模板' },
  { id: 2, name: '美食探店', description: '餐厅美食推荐模板', icon: '🍜', category: '系统模板' },
  { id: 3, name: '旅行攻略', description: '旅游景点介绍模板', icon: '✈️', category: '灵感模板' },
  { id: 4, name: '好物推荐', description: '产品种草模板', icon: '🛍️', category: '灵感模板' }
])

const filteredTemplates = computed(() => {
  if (selectedCategory.value === '全部') return templates.value
  return templates.value.filter(t => t.category === selectedCategory.value)
})

const useTemplate = (template: any) => {
  console.log('使用模板:', template)
  // TODO: 实现模板使用逻辑
}
</script>

<style scoped>
.template-gallery {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.gallery-header {
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

.template-filters {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.filter-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: var(--primary-color);
}

.filter-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.template-card {
  padding: 1.5rem;
  transition: transform 0.3s ease;
}

.template-card:hover {
  transform: translateY(-4px);
}

.template-preview {
  margin-bottom: 1rem;
}

.preview-placeholder {
  width: 100%;
  height: 150px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
}

.template-info h3 {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.template-info p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.btn-ghost {
  width: 100%;
  padding: 0.75rem;
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: var(--primary-color);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--primary-color);
}
</style>