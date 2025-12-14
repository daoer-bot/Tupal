<template>
  <div class="cases-container animate-fade-in">
    <!-- ✨ 图文采集入口 -->
    <section class="collector-section">
      <div class="section-header">
        <div class="section-title-wrapper">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="section-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
          </svg>
          <div>
            <h2 class="section-title">图文采集</h2>
            <p class="section-desc">粘贴链接即可采集灵感，直接存入灵感收藏</p>
          </div>
        </div>
      </div>

      <div class="collector-card glass-panel">
        <div class="input-row">
          <input
            v-model="contentUrl"
            type="text"
            class="url-input"
            placeholder="粘贴小红书、微博等平台的内容链接..."
            @keyup.enter="handleCollect"
          />
          <button
            class="collect-btn"
            @click="handleCollect"
            :disabled="!contentUrl || isCollecting"
          >
            <span v-if="isCollecting" class="loading-spinner"></span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="btn-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
            </svg>
            {{ isCollecting ? '采集中...' : '采集' }}
          </button>
        </div>
      </div>

      <transition name="slide-fade">
        <div v-if="collectedContent" class="collected-preview glass-panel">
          <div class="preview-header">
            <h3 class="preview-title">采集预览</h3>
            <button
              class="save-btn"
              @click="handleSave"
              :disabled="isSaving"
            >
              <span v-if="isSaving" class="loading-spinner"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="btn-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0z" />
              </svg>
              {{ isSaving ? '保存中...' : '保存到灵感收藏' }}
            </button>
          </div>

          <div class="preview-content">
            <div class="content-meta">
              <div class="meta-item">
                <span class="meta-label">作者</span>
                <span class="meta-value">{{ collectedContent.author }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">标题</span>
                <span class="meta-value">{{ collectedContent.title }}</span>
              </div>
            </div>

            <div v-if="collectedContent.desc" class="content-description">
              <span class="meta-label">描述</span>
              <p>{{ collectedContent.desc }}</p>
            </div>

            <div v-if="collectedContent.cover" class="content-cover">
              <span class="meta-label">封面</span>
              <img :src="collectedContent.cover" alt="封面" class="preview-image" />
            </div>

            <div v-if="collectedContent.imgurl && collectedContent.imgurl.length" class="content-images">
              <span class="meta-label">图片 ({{ collectedContent.imgurl.length }})</span>
              <div class="image-grid">
                <img v-for="(img, idx) in collectedContent.imgurl" :key="idx" :src="img" alt="图片" class="preview-image" />
              </div>
            </div>
          </div>
        </div>
      </transition>
    </section>

    <!-- 📊 数据概览 (使用更精致的图标) -->
    <div class="stats-grid">
      <div class="stat-card glass-panel">
        <div class="stat-icon-wrapper orange">
          <BookOpen :size="24" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ cases.length }}</div>
          <div class="stat-label">Total Cases</div>
        </div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon-wrapper yellow">
          <Star :size="24" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ templateCount }}</div>
          <div class="stat-label">Templates</div>
        </div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon-wrapper blue">
          <Link :size="24" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ sourceCount }}</div>
          <div class="stat-label">Sources</div>
        </div>
      </div>
    </div>

    <!-- 🛠️ 顶部工具栏 -->
    <div class="toolbar glass-panel">
      <!-- 搜索 -->
      <div class="search-box">
        <Search :size="18" class="search-icon" />
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search collected cases..."
          class="search-input"
        />
      </div>

      <!-- 筛选切换器 (Toggle Group) -->
      <div class="filter-group">
        <button 
          class="filter-pill" 
          :class="{ active: activeFilter === 'all' }"
          @click="setFilter('all')"
        >
          All
        </button>
        <button 
          class="filter-pill" 
          :class="{ active: activeFilter === 'template' }"
          @click="setFilter('template')"
        >
          <Star :size="14" :fill="activeFilter === 'template' ? 'currentColor' : 'none'" />
          Templates
        </button>
        <button 
          class="filter-pill" 
          :class="{ active: activeFilter === 'normal' }"
          @click="setFilter('normal')"
        >
          Normal
        </button>
      </div>
      
      <!-- 刷新按钮 -->
      <button class="icon-btn refresh-btn" @click="loadCases" :disabled="loading">
        <RefreshCw :size="18" :class="{ 'spinning': loading }" />
      </button>
    </div>

    <!-- ⏳ 加载状态 -->
    <div v-if="loading" class="state-container glass-panel">
      <div class="loading-spinner-orange"></div>
      <p>Loading your inspiration collection...</p>
    </div>
    
    <!-- 📭 空状态 -->
    <div v-else-if="filteredCases.length === 0" class="state-container empty-state glass-panel">
      <div class="empty-illustration">
        <Compass :size="64" stroke-width="1" />
      </div>
      <h3>No Cases Found</h3>
      <p>Collect inspiration from social media to get started</p>
      <router-link to="/inspiration/collector" class="btn btn-primary">
        <Download :size="18" />
        Go Collect
      </router-link>
    </div>
    
    <!-- 🖼️ 案例网格 -->
    <div v-else class="cases-grid">
      <div 
        v-for="caseItem in filteredCases" 
        :key="caseItem.id" 
        class="case-card glass-panel"
        @click="viewCase(caseItem)"
      >
        <!-- 预览图 -->
        <div class="card-preview">
          <img 
            v-if="caseItem.content?.preview_image || caseItem.content?.image_url"
            :src="caseItem.content?.preview_image || caseItem.content?.image_url" 
            :alt="caseItem.name"
            class="preview-image"
          />
          <div v-else class="preview-placeholder">
            <BookOpen :size="32" opacity="0.5" />
          </div>
          
          <!-- 悬浮操作栏 -->
          <div class="card-actions">
            <button
              class="action-circle-btn star-btn"
              :class="{ 'is-active': caseItem.content?.is_template }"
              @click.stop="toggleTemplate(caseItem)"
              :title="caseItem.content?.is_template ? 'Remove Template' : 'Set as Template'"
            >
              <Star :size="16" :fill="caseItem.content?.is_template ? 'currentColor' : 'none'" />
            </button>
            <button
              class="action-circle-btn delete-btn"
              @click.stop="handleDelete(caseItem)"
              title="Delete"
            >
              <Trash2 :size="16" />
            </button>
          </div>

          <!-- 来源标签 -->
          <div v-if="caseItem.content?.source_url" class="source-tag">
            <Link :size="10" />
            {{ getSourceName(caseItem.content?.source_url) }}
          </div>
        </div>
        
        <!-- 内容区域 -->
        <div class="card-content">
          <div class="content-header">
            <h3 class="card-title" :title="caseItem.name">{{ caseItem.name }}</h3>
            <span v-if="caseItem.content?.is_template" class="template-mark">
              TEMPLATE
            </span>
          </div>
          
          <p class="card-desc">{{ truncateText(caseItem.description, 60) }}</p>
          
          <div class="card-footer">
            <span class="date">{{ formatDate(caseItem.created_at) }}</span>
            <button 
              v-if="caseItem.content?.is_template"
              class="use-template-btn"
              @click.stop="useAsTemplate(caseItem)"
            >
              <Zap :size="12" />
              Use
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination">
      <button 
        class="page-btn" 
        :disabled="currentPage === 1"
        @click="currentPage--"
      >
        <ChevronLeft :size="16" />
      </button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button 
        class="page-btn" 
        :disabled="currentPage === totalPages"
        @click="currentPage++"
      >
        <ChevronRight :size="16" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search,
  Star,
  BookOpen,
  RefreshCw,
  Download,
  Trash2,
  Link,
  Zap,
  ChevronLeft,
  ChevronRight,
  Compass
} from 'lucide-vue-next'
import materialApi, { type Material } from '../../services/materialApi'
import templateApi from '../../services/templateApi'

const router = useRouter()
const cases = ref<Material[]>([])
const loading = ref(true)
const searchQuery = ref('')
const activeFilter = ref<'all' | 'template' | 'normal'>('all')
const currentPage = ref(1)
const itemsPerPage = ref(12)
const contentUrl = ref('')
const isCollecting = ref(false)
const isSaving = ref(false)
const collectedContent = ref<any | null>(null)

const templateCount = computed(() => cases.value.filter(c => c.content?.is_template).length)
const sourceCount = computed(() => new Set(cases.value.filter(c => c.content?.source_url).map(c => getSourceName(c.content?.source_url))).size)

const filteredCases = computed(() => {
  let filtered = cases.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(caseItem => 
      caseItem.name.toLowerCase().includes(query) ||
      caseItem.description?.toLowerCase().includes(query)
    )
  }
  if (activeFilter.value === 'template') filtered = filtered.filter(c => c.content?.is_template)
  else if (activeFilter.value === 'normal') filtered = filtered.filter(c => !c.content?.is_template)
  
  const start = (currentPage.value - 1) * itemsPerPage.value
  return filtered.slice(start, start + itemsPerPage.value)
})

const totalPages = computed(() => {
  let filtered = cases.value
  // ... (duplicate logic for brevity, ideally shared)
  if (activeFilter.value === 'template') filtered = filtered.filter(c => c.content?.is_template)
  else if (activeFilter.value === 'normal') filtered = filtered.filter(c => !c.content?.is_template)
  return Math.ceil(filtered.length / itemsPerPage.value)
})

const loadCases = async () => {
  loading.value = true
  try {
    const response = await materialApi.getMaterials({ type: 'reference' })
    if (response.success) cases.value = response.data.items || []
  } catch (error) {
    console.error('Failed to load cases:', error)
  } finally {
    loading.value = false
  }
}

const setFilter = (filter: typeof activeFilter.value) => {
  activeFilter.value = filter
  currentPage.value = 1
}

const truncateText = (text: string, max: number) => text?.length > max ? text.slice(0, max) + '...' : text
const formatDate = (d: string) => d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : ''
const getSourceName = (url: string) => {
  if (!url) return 'Unknown'
  try {
    const host = new URL(url).hostname
    if (host.includes('xiaohongshu')) return 'RedBook'
    if (host.includes('weibo')) return 'Weibo'
    if (host.includes('douyin')) return 'Douyin'
    return host.replace('www.', '').split('.')[0]
  } catch { return 'Web' }
}

const viewCase = (item: Material) => { /* Preview logic */ }

const toggleTemplate = async (item: Material) => {
  try {
    const isTemplate = item.content?.is_template
    const res = isTemplate 
      ? await templateApi.unmarkAsTemplate(item.id)
      : await templateApi.markAsTemplate(item.id, item.name)
      
    if (res.success) {
      const idx = cases.value.findIndex(c => c.id === item.id)
      if (idx !== -1) {
        cases.value[idx].content = { ...cases.value[idx].content, is_template: !isTemplate }
      }
    }
  } catch (err) { console.error(err) }
}

const useAsTemplate = (item: Material) => {
  router.push({ path: '/creation', query: { template_id: item.id } })
}

const handleDelete = async (item: Material) => {
  if (confirm(`Delete "${item.name}"?`)) {
    const res = await materialApi.deleteMaterial(item.id)
    if (res.success) await loadCases()
  }
}

const handleCollect = async () => {
  if (!contentUrl.value) return
  isCollecting.value = true
  try {
    const response = await fetch('http://localhost:5030/api/xiaohongshu/parse', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url: contentUrl.value })
    })

    const result = await response.json()
    if (result.success) {
      collectedContent.value = result.data
    } else {
      alert('解析失败: ' + (result.error || '未知错误'))
    }
  } catch (error) {
    alert('请求失败: ' + error)
  } finally {
    isCollecting.value = false
  }
}

const handleSave = async () => {
  if (!collectedContent.value) return

  isSaving.value = true
  try {
    const response = await materialApi.createMaterial({
      name: collectedContent.value.title || '未命名素材',
      type: 'reference',
      category: '小红书采集',
      content: {
        author: collectedContent.value.author,
        title: collectedContent.value.title,
        description: collectedContent.value.desc,
        cover: collectedContent.value.cover,
        images: collectedContent.value.imgurl || [],
        source_url: contentUrl.value,
        reference_type: 'xiaohongshu'
      },
      description: collectedContent.value.desc || '',
      tags: ['小红书', '采集']
    })

    if (response.success) {
      alert('素材已保存到灵感收藏')
      collectedContent.value = null
      contentUrl.value = ''
      await loadCases()
    } else {
      alert('保存失败: ' + (response.error || '未知错误'))
    }
  } catch (error) {
    alert('保存失败: ' + error)
  } finally {
    isSaving.value = false
  }
}

watch([searchQuery, activeFilter], () => { currentPage.value = 1 })
onMounted(() => { loadCases() })
</script>

<style scoped>
.collector-section {
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-icon {
  width: 28px;
  height: 28px;
  color: var(--primary-color);
}

.section-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.section-desc {
  margin: 0.25rem 0 0;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.collector-card {
  padding: 1.5rem;
}

.input-row {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.url-input {
  flex: 1;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  border: 1px solid rgba(99, 102, 241, 0.2);
  background: rgba(255, 255, 255, 0.8);
  color: var(--text-primary);
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.url-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.collect-btn,
.save-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, var(--primary-color), var(--accent-color, #8b5cf6));
  color: white;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.collect-btn:disabled,
.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.collect-btn:not(:disabled):hover,
.save-btn:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
}

.collected-preview {
  padding: 1.5rem;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.preview-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.content-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.meta-item {
  background: rgba(99, 102, 241, 0.04);
  padding: 0.75rem 1rem;
  border-radius: 12px;
}

.meta-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-tertiary);
  letter-spacing: 0.05em;
}

.meta-value {
  display: block;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 0.35rem;
}

.content-description p {
  margin: 0.25rem 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.content-cover,
.content-images {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.75rem;
}

.preview-image {
  width: 100%;
  border-radius: 12px;
  object-fit: cover;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.cases-container { width: 100%; }

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 20px;
}

.stat-icon-wrapper {
  width: 50px; height: 50px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon-wrapper.orange { background: #FFF7ED; color: #F97316; }
.stat-icon-wrapper.yellow { background: #FEFCE8; color: #EAB308; }
.stat-icon-wrapper.blue { background: #EFF6FF; color: #3B82F6; }

.stat-value { font-size: 1.8rem; font-weight: 800; color: var(--text-primary); line-height: 1; margin-bottom: 4px; }
.stat-label { font-size: 0.8rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; }

/* Toolbar */
.toolbar {
  display: flex;
  align-items: center;
  padding: 0.8rem 1.2rem;
  margin-bottom: 2rem;
  background: white;
  border-radius: 16px;
  gap: 1rem;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  background: #F8F9FA;
  border-radius: 10px;
  padding: 0 1rem;
}

.search-input {
  border: none; background: transparent; width: 100%; padding: 0.8rem 0;
  font-size: 0.95rem; color: var(--text-primary);
}

.filter-group {
  display: flex;
  background: #F1F5F9;
  padding: 4px;
  border-radius: 12px;
}

.filter-pill {
  border: none;
  background: transparent;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.2s;
}

.filter-pill.active { background: white; color: var(--text-primary); box-shadow: 0 2px 5px rgba(0,0,0,0.05); }

.icon-btn {
  width: 36px; height: 36px;
  border: none; background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 8px;
}
.icon-btn:hover { background: #F8F9FA; color: var(--text-primary); }
.spinning { animation: spin 1s linear infinite; }

/* Grid */
.cases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.case-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(0,0,0,0.03);
}

.case-card:hover { transform: translateY(-4px); box-shadow: 0 12px 30px rgba(0,0,0,0.06); }

.card-preview {
  height: 180px;
  position: relative;
  overflow: hidden;
  background: #F1F5F9;
}

.preview-image { width: 100%; height: 100%; object-fit: cover; }
.preview-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #94A3B8; }

.source-tag {
  position: absolute;
  bottom: 8px; left: 8px;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  color: white;
  font-size: 0.7rem;
  padding: 4px 8px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Actions */
.card-actions {
  position: absolute;
  top: 8px; right: 8px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transform: translateY(-5px);
  transition: all 0.2s;
}

.case-card:hover .card-actions { opacity: 1; transform: translateY(0); }

.action-circle-btn {
  width: 30px; height: 30px;
  border-radius: 50%;
  border: none;
  background: rgba(255,255,255,0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.star-btn:hover { color: #EAB308; transform: scale(1.1); }
.star-btn.is-active { color: #EAB308; }
.delete-btn:hover { color: #EF4444; transform: scale(1.1); }

/* Content */
.card-content { padding: 1rem; }
.content-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.card-title { font-size: 1rem; font-weight: 700; color: var(--text-primary); margin: 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; max-width: 70%; }

.template-mark {
  font-size: 0.65rem;
  font-weight: 800;
  color: #EAB308;
  background: #FEFCE8;
  padding: 2px 6px;
  border-radius: 4px;
}

.card-desc { font-size: 0.85rem; color: var(--text-secondary); line-height: 1.4; margin-bottom: 1rem; }

.card-footer { display: flex; justify-content: space-between; align-items: center; }
.date { font-size: 0.75rem; color: var(--text-tertiary); }

.use-template-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border: none;
  background: linear-gradient(135deg, #F59E0B, #D97706);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
}

/* States */
.state-container { padding: 4rem; text-align: center; }
.loading-spinner-orange { width: 30px; height: 30px; border: 3px solid #FFEDD5; border-top-color: #F97316; border-radius: 50%; animation: spin 1s infinite; margin: 0 auto 1rem; }
.empty-illustration { color: #F97316; opacity: 0.5; margin-bottom: 1rem; }

@keyframes spin { to { transform: rotate(360deg); } }

/* Responsive */
@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr; }
  .cases-grid { grid-template-columns: 1fr; }
}
</style>
