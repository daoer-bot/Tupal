<template>
  <div class="knowledge-container">
    <!-- 数据概览卡片 -->
    <div class="stats-grid">
      <div class="stat-card glass-panel">
        <div class="stat-icon">📚</div>
        <div class="stat-info">
          <div class="stat-value">{{ materials.length }}</div>
          <div class="stat-label">总素材数</div>
        </div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon">📝</div>
        <div class="stat-info">
          <div class="stat-value">{{ textCount }}</div>
          <div class="stat-label">文本素材</div>
        </div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon">🖼️</div>
        <div class="stat-info">
          <div class="stat-value">{{ imageCount }}</div>
          <div class="stat-label">图片素材</div>
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
            placeholder="搜索素材..."
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
          :class="{ active: activeFilter === 'text' }"
          @click="setFilter('text')"
        >
          <FileText :size="16" />
          文本
        </button>
        <button 
          class="filter-btn" 
          :class="{ active: activeFilter === 'image' }"
          @click="setFilter('image')"
        >
          <Image :size="16" />
          图片
        </button>
      </div>
      
      <div class="action-section">
        <button class="btn btn-primary add-btn" @click="showAddModal = true">
          <Plus :size="18" />
          添加素材
        </button>
      </div>
    </div>

    <!-- 素材网格 -->
    <div v-if="loading" class="loading-state glass-panel">
      <div class="spinner"></div>
      <p>正在加载素材...</p>
    </div>
    
    <div v-else-if="filteredMaterials.length === 0" class="empty-state glass-panel">
      <div class="empty-icon">📦</div>
      <h3>暂无素材</h3>
      <p>添加可复用的图片或文本素材，在创作时通过@引用</p>
      <button class="btn btn-primary" @click="showAddModal = true">
        <Plus :size="18" />
        添加素材
      </button>
    </div>
    
    <div v-else class="materials-grid">
      <div 
        v-for="material in filteredMaterials" 
        :key="material.id" 
        class="material-card glass-panel"
        @click="handleMaterialClick(material)"
      >
        <!-- 图片类型素材 -->
        <div v-if="material.type === 'image'" class="card-preview image-preview">
          <img 
            :src="material.content?.url || material.content?.image_url" 
            :alt="material.name"
            class="preview-image"
          />
        </div>
        
        <!-- 文本类型素材 -->
        <div v-else class="card-preview text-preview">
          <div class="text-content">
            {{ truncateText(material.content?.text || material.content, 100) }}
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <button
            class="action-btn edit-btn"
            @click.stop="handleEdit(material)"
            title="编辑"
          >
            <Edit :size="16" />
          </button>
          <button
            class="action-btn delete-btn"
            @click.stop="handleDelete(material)"
            title="删除"
          >
            <Trash2 :size="16" />
          </button>
        </div>
        
        <!-- 类型标签 -->
        <div class="type-badge" :class="material.type">
          {{ material.type === 'text' ? '文本' : '图片' }}
        </div>
        
        <div class="card-content">
          <h3 class="card-title" :title="material.name">{{ material.name }}</h3>
          <div class="card-meta">
            <span class="meta-item">
              <span class="icon">📅</span>
              {{ formatDate(material.created_at) }}
            </span>
            <span v-if="material.tags?.length" class="meta-item tags">
              <span v-for="tag in material.tags.slice(0, 2)" :key="tag" class="tag">
                {{ tag }}
              </span>
            </span>
          </div>
          <p v-if="material.description" class="card-description">
            {{ truncateText(material.description, 50) }}
          </p>
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
    
    <!-- 添加/编辑模态框 -->
    <MaterialEditor
      :show="showAddModal || showEditModal"
      :material="editingMaterial || undefined"
      :allowed-types="['text', 'image']"
      @close="closeModal"
      @save="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import {
  Search,
  FileText,
  Image,
  Plus,
  Edit,
  Trash2,
  ChevronLeft,
  ChevronRight
} from 'lucide-vue-next'
import MaterialEditor from '../../components/MaterialEditor.vue'
import materialApi, { type Material } from '../../services/materialApi'

// 状态
const materials = ref<Material[]>([])
const loading = ref(true)
const searchQuery = ref('')
const activeFilter = ref<'all' | 'text' | 'image'>('all')
const currentPage = ref(1)
const itemsPerPage = ref(12)
const showAddModal = ref(false)
const showEditModal = ref(false)
const editingMaterial = ref<Material | null>(null)

// 计算属性
const textCount = computed(() =>
  materials.value.filter(m => m.type === 'text').length
)

const imageCount = computed(() =>
  materials.value.filter(m => m.type === 'image').length
)

const filteredMaterials = computed(() => {
  let filtered = materials.value
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(material => 
      material.name.toLowerCase().includes(query) ||
      material.description?.toLowerCase().includes(query) ||
      material.tags?.some(tag => tag.toLowerCase().includes(query))
    )
  }
  
  // 类型过滤
  if (activeFilter.value !== 'all') {
    filtered = filtered.filter(material => material.type === activeFilter.value)
  }
  
  // 分页
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filtered.slice(start, end)
})

const totalPages = computed(() => {
  let filtered = materials.value
  if (activeFilter.value !== 'all') {
    filtered = filtered.filter(m => m.type === activeFilter.value)
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
const loadMaterials = async () => {
  loading.value = true
  try {
    // 只获取 text 和 image 类型的素材
    const response = await materialApi.getMaterials({ type: 'text,image' })
    if (response.success) {
      materials.value = response.data.items || []
    }
  } catch (error) {
    console.error('加载素材失败:', error)
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

const handleMaterialClick = (material: Material) => {
  // 可以添加预览功能
  console.log('点击素材:', material)
}

const handleEdit = (material: Material) => {
  editingMaterial.value = material
  showEditModal.value = true
}

const handleDelete = async (material: Material) => {
  if (confirm(`确定要删除素材 "${material.name}" 吗？`)) {
    try {
      const response = await materialApi.deleteMaterial(material.id)
      if (response.success) {
        await loadMaterials()
      }
    } catch (error) {
      console.error('删除素材失败:', error)
      alert('删除失败，请重试')
    }
  }
}

const handleSave = async (material: Partial<Material>) => {
  try {
    if (editingMaterial.value) {
      // 编辑
      const response = await materialApi.updateMaterial(editingMaterial.value.id, material)
      if (response.success) {
        await loadMaterials()
        closeModal()
      }
    } else {
      // 添加
      const response = await materialApi.createMaterial(material as any)
      if (response.success) {
        await loadMaterials()
        closeModal()
      }
    }
  } catch (error) {
    console.error('保存素材失败:', error)
    alert('保存失败，请重试')
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  editingMaterial.value = null
}

// 监听
watch([searchQuery, activeFilter], () => {
  currentPage.value = 1
})

onMounted(() => {
  loadMaterials()
})
</script>

<style scoped>
.knowledge-container {
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

.add-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
}

/* 素材网格 */
.materials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.material-card {
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.material-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-preview {
  height: 160px;
  position: relative;
  overflow: hidden;
}

.image-preview {
  background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.material-card:hover .preview-image {
  transform: scale(1.05);
}

.text-preview {
  background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-content {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.6;
  text-align: center;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
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

.material-card:hover .action-buttons {
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

.edit-btn:hover {
  background: #e0e7ff;
  color: #6366f1;
}

.delete-btn:hover {
  background: #fee2e2;
  color: #ef4444;
}

/* 类型标签 */
.type-badge {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  padding: 0.375rem 0.875rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.type-badge.text {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.9), rgba(139, 92, 246, 0.9));
  color: white;
}

.type-badge.image {
  background: linear-gradient(135deg, rgba(236, 72, 153, 0.9), rgba(244, 114, 182, 0.9));
  color: white;
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

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-secondary);
  font-size: 0.8rem;
  margin-bottom: 0.5rem;
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

.card-description {
  margin: 0;
  font-size: 0.8rem;
  color: var(--text-tertiary);
  line-height: 1.4;
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
  }
  
  .action-section {
    margin-left: 0;
  }
  
  .add-btn {
    width: 100%;
    justify-content: center;
  }
  
  .materials-grid {
    grid-template-columns: 1fr;
  }
}
</style>