<template>
  <div class="cases-container animate-fade-in">
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

watch([searchQuery, activeFilter], () => { currentPage.value = 1 })
onMounted(() => { loadCases() })
</script>

<style scoped>
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