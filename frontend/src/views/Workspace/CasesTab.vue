<template>
  <div class="cases-container">
    <!-- 数据概览卡片 -->
    <div class="stats-grid">
      <div class="stat-card glass-panel">
        <div class="stat-icon">📑</div>
        <div class="stat-info">
          <div class="stat-value">{{ cases.length }}</div>
          <div class="stat-label">总案例数</div>
        </div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon">⭐</div>
        <div class="stat-info">
          <div class="stat-value">{{ templateCount }}</div>
          <div class="stat-label">已设为模板</div>
        </div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon">🔗</div>
        <div class="stat-info">
          <div class="stat-value">{{ sourceCount }}</div>
          <div class="stat-label">采集来源</div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar glass-panel-heavy">
      <div class="search-section">
        <div class="search-input-wrapper">
          <Search :size="18" class="search-icon" />
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索案例..."
            class="search-input"
          />
        </div>
      </div>
      
      <div class="filter-section">
        <button 
          class="filter-btn" 
          :class="{ active: activeFilter === 'all' }"
          @click="setFilter('all')"
        >
          全部
        </button>
        <button 
          class="filter-btn" 
          :class="{ active: activeFilter === 'template' }"
          @click="setFilter('template')"
        >
          <Star :size="16" />
          已设为模板
        </button>
        <button 
          class="filter-btn" 
          :class="{ active: activeFilter === 'normal' }"
          @click="setFilter('normal')"
        >
          <FileText :size="16" />
          普通案例
        </button>
      </div>
      
      <div class="action-section">
        <button class="btn btn-secondary" @click="loadCases" :disabled="loading">
          <RefreshCw :size="18" :class="{ 'spinning': loading }" />
          刷新
        </button>
      </div>
    </div>

    <!-- 案例网格 -->
    <div v-if="loading" class="loading-state glass-panel">
      <div class="spinner"></div>
      <p>正在加载案例...</p>
    </div>
    
    <div v-else-if="filteredCases.length === 0" class="empty-state glass-panel">
      <div class="empty-icon">📋</div>
      <h3>暂无案例</h3>
      <p>通过"灵感与发现"页面的图文采集功能添加优秀案例</p>
      <router-link to="/inspiration/collector" class="btn btn-primary">
        <Download :size="18" />
        去采集
      </router-link>
    </div>
    
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
            <FileText :size="48" />
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <button
            class="action-btn template-btn"
            :class="{ 'is-template': caseItem.content?.is_template }"
            @click.stop="toggleTemplate(caseItem)"
            :title="caseItem.content?.is_template ? '取消模板' : '设为模板'"
          >
            <Star :size="16" :fill="caseItem.content?.is_template ? 'currentColor' : 'none'" />
          </button>
          <button
            class="action-btn delete-btn"
            @click.stop="handleDelete(caseItem)"
            title="删除"
          >
            <Trash2 :size="16" />
          </button>
        </div>
        
        <!-- 模板标签 -->
        <div v-if="caseItem.content?.is_template" class="template-badge">
          <Star :size="12" fill="currentColor" />
          模板
        </div>
        
        <!-- 来源标签 -->
        <div v-if="caseItem.content?.source_url" class="source-badge">
          <Link :size="12" />
          {{ getSourceName(caseItem.content?.source_url) }}
        </div>
        
        <div class="card-content">
          <h3 class="card-title" :title="caseItem.name">{{ caseItem.name }}</h3>
          <p v-if="caseItem.description" class="card-description">
            {{ truncateText(caseItem.description, 60) }}
          </p>
          <div class="card-meta">
            <span class="meta-item">
              <span class="icon">📅</span>
              {{ formatDate(caseItem.created_at) }}
            </span>
            <span v-if="caseItem.tags?.length" class="meta-item tags">
              <span v-for="tag in caseItem.tags.slice(0, 2)" :key="tag" class="tag">
                {{ tag }}
              </span>
            </span>
          </div>
          
          <!-- 快捷操作 -->
          <div class="card-actions">
            <button 
              class="quick-action-btn"
              :class="{ active: caseItem.content?.is_template }"
              @click.stop="toggleTemplate(caseItem)"
            >
              <Star :size="14" :fill="caseItem.content?.is_template ? 'currentColor' : 'none'" />
              {{ caseItem.content?.is_template ? '已设为模板' : '设为模板' }}
            </button>
            <button 
              v-if="caseItem.content?.is_template"
              class="quick-action-btn use-btn"
              @click.stop="useAsTemplate(caseItem)"
            >
              <Zap :size="14" />
              使用模板
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
      
      <div class="page-numbers">
        <button 
          v-for="page in visiblePages" 
          :key="page"
          class="page-number"
          :class="{ active: page === currentPage }"
          @click="currentPage = page"
        >
          {{ page }}
        </button>
      </div>
      
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
  FileText,
  RefreshCw,
  Download,
  Trash2,
  Link,
  Zap,
  ChevronLeft,
  ChevronRight
} from 'lucide-vue-next'
import materialApi, { type Material } from '../../services/materialApi'
import templateApi from '../../services/templateApi'

const router = useRouter()

// 状态
const cases = ref<Material[]>([])
const loading = ref(true)
const searchQuery = ref('')
const activeFilter = ref<'all' | 'template' | 'normal'>('all')
const currentPage = ref(1)
const itemsPerPage = ref(12)

// 计算属性
const templateCount = computed(() =>
  cases.value.filter(c => c.content?.is_template).length
)

const sourceCount = computed(() => {
  const sources = new Set(
    cases.value
      .filter(c => c.content?.source_url)
      .map(c => getSourceName(c.content?.source_url))
  )
  return sources.size
})

const filteredCases = computed(() => {
  let filtered = cases.value
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(caseItem => 
      caseItem.name.toLowerCase().includes(query) ||
      caseItem.description?.toLowerCase().includes(query) ||
      caseItem.tags?.some(tag => tag.toLowerCase().includes(query))
    )
  }
  
  // 类型过滤
  if (activeFilter.value === 'template') {
    filtered = filtered.filter(c => c.content?.is_template)
  } else if (activeFilter.value === 'normal') {
    filtered = filtered.filter(c => !c.content?.is_template)
  }
  
  // 分页
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filtered.slice(start, end)
})

const totalPages = computed(() => {
  let filtered = cases.value
  if (activeFilter.value === 'template') {
    filtered = filtered.filter(c => c.content?.is_template)
  } else if (activeFilter.value === 'normal') {
    filtered = filtered.filter(c => !c.content?.is_template)
  }
  return Math.ceil(filtered.length / itemsPerPage.value)
})

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// 方法
const loadCases = async () => {
  loading.value = true
  try {
    // 只获取 reference 类型的素材（案例）
    const response = await materialApi.getMaterials({ type: 'reference' })
    if (response.success) {
      cases.value = response.data.items || []
    }
  } catch (error) {
    console.error('加载案例失败:', error)
  } finally {
    loading.value = false
  }
}

const setFilter = (filter: typeof activeFilter.value) => {
  activeFilter.value = filter
  currentPage.value = 1
}

const truncateText = (text: string, maxLength: number) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit'
  })
}

const getSourceName = (url: string) => {
  if (!url) return '未知'
  try {
    const hostname = new URL(url).hostname
    if (hostname.includes('xiaohongshu')) return '小红书'
    if (hostname.includes('weibo')) return '微博'
    if (hostname.includes('douyin')) return '抖音'
    if (hostname.includes('bilibili')) return 'B站'
    if (hostname.includes('zhihu')) return '知乎'
    return hostname.replace('www.', '').split('.')[0]
  } catch {
    return '未知'
  }
}

const viewCase = (caseItem: Material) => {
  // 可以添加详情预览功能
  console.log('查看案例:', caseItem)
}

const toggleTemplate = async (caseItem: Material) => {
  try {
    const isTemplate = caseItem.content?.is_template
    
    if (isTemplate) {
      // 取消模板
      const response = await templateApi.unmarkAsTemplate(caseItem.id)
      if (response.success) {
        // 更新本地状态
        const index = cases.value.findIndex(c => c.id === caseItem.id)
        if (index !== -1) {
          cases.value[index] = {
            ...cases.value[index],
            content: {
              ...cases.value[index].content,
              is_template: false,
              template_name: null
            }
          }
        }
      }
    } else {
      // 设为模板
      const response = await templateApi.markAsTemplate(caseItem.id, caseItem.name)
      if (response.success) {
        // 更新本地状态
        const index = cases.value.findIndex(c => c.id === caseItem.id)
        if (index !== -1) {
          cases.value[index] = {
            ...cases.value[index],
            content: {
              ...cases.value[index].content,
              is_template: true,
              template_name: caseItem.name
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('切换模板状态失败:', error)
    alert('操作失败，请重试')
  }
}

const useAsTemplate = (caseItem: Material) => {
  // 跳转到创作页面，使用该模板
  router.push({
    path: '/creation',
    query: {
      template_id: caseItem.id,
      template_name: caseItem.name
    }
  })
}

const handleDelete = async (caseItem: Material) => {
  if (confirm(`确定要删除案例 "${caseItem.name}" 吗？`)) {
    try {
      const response = await materialApi.deleteMaterial(caseItem.id)
      if (response.success) {
        await loadCases()
      }
    } catch (error) {
      console.error('删除案例失败:', error)
      alert('删除失败，请重试')
    }
  }
}

// 监听
watch([searchQuery, activeFilter], () => {
  currentPage.value = 1
})

onMounted(() => {
  loadCases()
})
</script>

<style scoped>
.cases-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* 数据概览 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 2.5rem;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(236, 72, 153, 0.1));
  border-radius: 16px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

/* 操作栏 */
.action-bar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem 1.5rem;
  margin-bottom: 2rem;
  border-radius: 16px;
  flex-wrap: wrap;
}

.search-section {
  flex: 1;
  min-width: 200px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: var(--text-secondary);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  background: rgba(255, 255, 255, 0.15);
}

.filter-section {
  display: flex;
  gap: 0.5rem;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
}

.filter-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: var(--text-primary);
}

.filter-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-section {
  margin-left: auto;
}

.spinning {
  animation: spin 1s linear infinite;
}

/* 案例网格 */
.cases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.case-card {
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.case-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-preview {
  height: 180px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.case-card:hover .preview-image {
  transform: scale(1.05);
}

.preview-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
  color: var(--text-tertiary);
}

/* 操作按钮 */
.action-buttons {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 10;
}

.case-card:hover .action-buttons {
  opacity: 1;
}

.action-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.action-btn:hover {
  transform: scale(1.1);
}

.template-btn:hover,
.template-btn.is-template {
  background: #fef3c7;
  color: #f59e0b;
}

.delete-btn:hover {
  background: #fee2e2;
  color: #ef4444;
}

/* 模板标签 */
.template-badge {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.9), rgba(251, 191, 36, 0.9));
  color: white;
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 来源标签 */
.source-badge {
  position: absolute;
  bottom: 0.75rem;
  left: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.625rem;
  border-radius: 0.5rem;
  font-size: 0.7rem;
  font-weight: 500;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  backdrop-filter: blur(8px);
}

.card-content {
  padding: 1.25rem;
}

.card-title {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-description {
  margin: 0 0 0.75rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-secondary);
  font-size: 0.8rem;
  margin-bottom: 0.75rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.tags {
  display: flex;
  gap: 0.25rem;
}

.tag {
  padding: 0.125rem 0.5rem;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 4px;
  font-size: 0.7rem;
  color: var(--primary-color);
}

/* 快捷操作 */
.card-actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.quick-action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-action-btn:hover {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
  border-color: var(--primary-color);
}

.quick-action-btn.active {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  border-color: #f59e0b;
}

.quick-action-btn.use-btn {
  background: linear-gradient(135deg, #6366f1, #ec4899);
  color: white;
  border: none;
}

.quick-action-btn.use-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* 空状态和加载状态 */
.empty-state,
.loading-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0 0 0.5rem;
  color: var(--text-primary);
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(99, 102, 241, 0.2);
  border-top-color: #6366f1;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.page-btn,
.page-number {
  width: 40px;
  height: 40px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.page-btn:hover,
.page-number:hover {
  background: rgba(255, 255, 255, 0.2);
  color: var(--text-primary);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-number.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.page-numbers {
  display: flex;
  gap: 0.5rem;
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-section {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .action-section {
    margin-left: 0;
  }
  
  .cases-grid {
    grid-template-columns: 1fr;
  }
  
  .card-actions {
    flex-direction: column;
  }
}
</style>