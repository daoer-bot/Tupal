<template>
  <div class="result-view">
    <ProcessSteps :current-step="3" />
    
    <div class="page-header">
      <h2>图文生成结果</h2>
      <div class="header-actions">
        <button @click="downloadAll" class="btn btn-primary" :disabled="!hasImages">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon-svg">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
          </svg>
          下载全部
        </button>
      </div>
    </div>

    <div v-if="store.currentOutline" class="result-content">
      <div class="cards-list">
        <div
          v-for="page in store.currentOutline.pages"
          :key="page.page_number"
          class="result-card"
        >
          <div class="card-image">
            <img 
              v-if="page.image_url" 
              :src="page.image_url" 
              :alt="`页面 ${page.page_number}`" 
              @click="previewImage(page.image_url)"
            />
            <div v-else class="image-placeholder">
              <span>暂无图片</span>
            </div>
            <div class="page-badge">P{{ page.page_number }}</div>
          </div>
          
          <div class="card-content">
            <div class="content-header">
              <h4>{{ page.title }}</h4>
              <a 
                v-if="page.image_url" 
                :href="page.image_url" 
                target="_blank" 
                class="download-link"
                title="下载此图"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                </svg>
              </a>
            </div>
            <p class="description">{{ page.description }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="empty-state">
      <p>暂无生成结果</p>
      <button @click="goHome" class="btn btn-primary">返回首页</button>
    </div>

    <div class="actions-footer">
      <button @click="goBack" class="btn btn-secondary">返回上一步</button>
      <button @click="goHome" class="btn btn-outline">回到首页</button>
    </div>

    <!-- 图片预览模态框 -->
    <div v-if="previewUrl" class="image-modal" @click="closePreview">
      <div class="modal-content">
        <img :src="previewUrl" alt="预览图片" />
        <button class="close-btn" @click="closePreview">×</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../store'
import ProcessSteps from '../components/ProcessSteps.vue'

const router = useRouter()
const store = useAppStore()
const previewUrl = ref('')

const hasImages = computed(() => {
  return store.currentOutline?.pages.some(p => !!p.image_url)
})

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.push('/generator')
}

const previewImage = (url: string) => {
  previewUrl.value = url
}

const closePreview = () => {
  previewUrl.value = ''
}

const downloadAll = () => {
  if (!store.currentOutline) return
  
  store.currentOutline.pages.forEach(page => {
    if (page.image_url) {
      const link = document.createElement('a')
      link.href = page.image_url
      link.download = `page_${page.page_number}.jpg`
      link.click()
    }
  })
}

onMounted(() => {
  if (!store.currentOutline) {
    router.push('/')
  }
})
</script>

<style scoped>
.result-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.cards-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.result-card {
  display: flex;
  background: var(--surface-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  transition: var(--transition);
}

.result-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.card-image {
  width: 300px;
  min-width: 300px;
  position: relative;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.image-placeholder {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.page-badge {
  position: absolute;
  top: 1rem;
  left: 1rem;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.card-content {
  padding: 2rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.content-header h4 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--text-primary);
  font-weight: 600;
}

.download-link {
  color: var(--text-secondary);
  transition: color 0.2s;
  padding: 0.5rem;
  border-radius: 50%;
}

.download-link:hover {
  color: var(--primary-color);
  background: var(--bg-color);
}

.description {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 1rem;
  white-space: pre-wrap;
}

.actions-footer {
  margin-top: 3rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.empty-state {
  text-align: center;
  padding: 4rem;
  background: var(--surface-color);
  border-radius: var(--radius-lg);
  border: 1px dashed var(--border-color);
}

.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  cursor: zoom-out;
}

.modal-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.modal-content img {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 4px;
}

.close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: none;
  border: none;
  color: white;
  font-size: 2rem;
  cursor: pointer;
}

@media (max-width: 768px) {
  .result-card {
    flex-direction: column;
  }
  
  .card-image {
    width: 100%;
    height: 300px;
  }
}
</style>