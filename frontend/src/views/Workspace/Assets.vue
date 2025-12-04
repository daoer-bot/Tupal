<template>
  <div class="material-view-new">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <h1 class="page-title text-gradient-animated">素材中心</h1>
        <p class="page-subtitle">管理和组织你的创意素材库</p>
      </div>
    </div>
    
    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="container">
        <div class="bar-content glass-card-premium">
          <div class="search-section">
            <div class="search-input-wrapper">
              <Search :size="18" class="search-icon" />
              <input 
                v-model="searchQuery" 
                type="text" 
                placeholder="搜索素材..."
                class="search-input glass-input"
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
            <button
              class="filter-btn"
              :class="{ active: activeFilter === 'reference' }"
              @click="setFilter('reference')"
            >
              <Palette :size="16" />
              参考
            </button>
          </div>
          
          <div class="action-section">
            <button class="btn-3d add-btn" @click="showAddModal = true">
              <Plus :size="18" />
              添加素材
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 素材网格 -->
    <div class="materials-grid">
      <div class="container">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>正在加载素材...</p>
        </div>
        
        <div v-else-if="filteredMaterials.length === 0" class="empty-state">
          <div class="empty-icon">📦</div>
          <h3>暂无素材</h3>
          <p>开始添加你的第一个素材吧！</p>
          <button class="btn-3d" @click="showAddModal = true">
            <Plus :size="18" />
            添加素材
          </button>
        </div>
        
        <div v-else class="grid-container grid-enhanced">
          <MaterialCardPremium
            v-for="material in filteredMaterials"
            :key="material.id"
            :material="material"
            @click="handleMaterialClick"
            @edit="handleEdit"
            @delete="handleDelete"
            class="material-card"
          />
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
    </div>
    
    <!-- 添加/编辑模态框 -->
    <MaterialEditor
      :show="showAddModal || showEditModal"
      :material="editingMaterial || undefined"
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
  Palette, 
  Plus,
  ChevronLeft,
  ChevronRight
} from 'lucide-vue-next'
import MaterialCardPremium from '../../components/MaterialCardPremium.vue'
import MaterialEditor from '../../components/MaterialEditor.vue'
import materialApi, { type Material } from '../../services/materialApi'

// 状态
const materials = ref<Material[]>([])
const loading = ref(true)
const searchQuery = ref('')
const activeFilter = ref<'all' | 'text' | 'image' | 'reference'>('all')
const currentPage = ref(1)
const itemsPerPage = ref(12)
const showAddModal = ref(false)
const showEditModal = ref(false)
const editingMaterial = ref<Material | null>(null)

// 计算属性
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
  
  return filtered
})

const paginatedMaterials = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredMaterials.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredMaterials.value.length / itemsPerPage.value)
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
    const response = await materialApi.getMaterials()
    if (response.success) {
      materials.value = response.data.items || response.data
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
.material-view-new {
  min-height: 100vh;
  background: linear-gradient(
    135deg,
    rgba(99, 102, 241, 0.05) 0%,
    rgba(236, 72, 153, 0.05) 50%,
    rgba(139, 92, 246, 0.05) 100%
  );
}

.page-header {
  padding: 3rem 0 2rem;
  text-align: center;
}

.page-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

/* 操作栏 */
.action-bar {
  padding: 2rem 0;
}

.bar-content {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.search-section {
  flex: 1;
  min-width: 250px;
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
  padding-left: 3rem;
  padding-right: 1rem;
}

.filter-section {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
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
  padding: 0.875rem 1.75rem;
  font-size: 0.95rem;
}

/* 素材网格 */
.materials-grid {
  padding: 2rem 0 4rem;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.grid-container {
  margin-bottom: 3rem;
}

.material-card {
  transition: all 0.3s ease;
}

.material-card:hover {
  transform: translateY(-4px);
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 3rem;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .bar-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-section {
    width: 100%;
  }
  
  .filter-section {
    justify-content: center;
  }
  
  .action-section {
    margin-left: 0;
    display: flex;
    justify-content: center;
  }
  
  .add-btn {
    width: 100%;
  }
  
  .page-header {
    padding: 2rem 0 1rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
}
</style>