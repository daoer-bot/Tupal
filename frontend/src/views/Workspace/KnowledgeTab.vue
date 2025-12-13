<template>
  <div class="knowledge-container animate-fade-in">
    <!-- 🛠️ 顶部工具栏 -->
    <div class="toolbar glass-panel">
      <div class="search-box">
        <Search :size="18" class="search-icon" />
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search materials..."
          class="search-input"
        />
      </div>
      
      <div class="toolbar-divider"></div>
      
      <div class="stats-text">
        <Database :size="16" />
        <span>{{ materials.length }} Items</span>
      </div>
      
      <div class="toolbar-actions">
        <button class="btn btn-primary add-btn" @click="showAddModal = true">
          <Plus :size="18" />
          <span>New Material</span>
        </button>
      </div>
    </div>

    <!-- ⏳ 加载状态 -->
    <div v-if="loading" class="state-container glass-panel">
      <div class="loading-spinner-mint"></div>
      <p>Loading your knowledge base...</p>
    </div>
    
    <!-- 📭 空状态 -->
    <div v-else-if="filteredMaterials.length === 0" class="state-container empty-state glass-panel">
      <div class="empty-illustration">
        <Box :size="64" stroke-width="1" />
      </div>
      <h3>No Materials Yet</h3>
      <p>Add text or images to build your knowledge base</p>
      <button class="btn btn-primary" @click="showAddModal = true">
        <Plus :size="18" />
        Add Material
      </button>
    </div>
    
    <!-- 🧩 素材瀑布流 -->
    <div v-else class="materials-grid">
      <div
        v-for="material in filteredMaterials"
        :key="material.id"
        class="material-card glass-panel"
        @click="handleMaterialClick(material)"
      >
        <!-- 卡片内容区域 -->
        <div class="card-body" :class="getCardTypeClass(material)">
          
          <!-- Mixed 类型: 图文 -->
          <template v-if="material.type === 'mixed'">
            <div v-if="material.content?.images?.length" class="image-grid" :class="getImageGridClass(material.content.images.length)">
              <div 
                v-for="(img, idx) in material.content.images.slice(0, 4)" 
                :key="idx" 
                class="image-item"
                :style="{ backgroundImage: `url(${img})` }"
              ></div>
              <div v-if="material.content.images.length > 4" class="more-overlay">
                +{{ material.content.images.length - 4 }}
              </div>
            </div>
            
            <div class="text-preview">
              <p v-if="material.content?.text">{{ truncateText(material.content.text, 80) }}</p>
              <p v-else class="no-text">No text description</p>
            </div>
          </template>

          <!-- Reference 类型: 案例 -->
          <template v-else-if="material.type === 'reference'">
            <div class="reference-cover">
              <img 
                v-if="material.content?.cover || material.content?.images?.[0]"
                :src="material.content.cover || material.content.images[0]" 
                class="cover-img"
              />
              <div v-else class="cover-placeholder">
                <FileText :size="32" />
              </div>
              <div class="ref-badge">Reference</div>
            </div>
            <div class="text-preview">
              <h4>{{ material.name }}</h4>
              <p>{{ truncateText(material.description || material.content?.description, 60) }}</p>
            </div>
          </template>

        </div>
        
        <!-- 底部信息栏 -->
        <div class="card-footer">
          <div class="footer-left">
            <span class="date">{{ formatDate(material.created_at) }}</span>
          </div>
          <div class="footer-actions">
            <button class="icon-btn-small edit" @click.stop="handleEdit(material)">
              <Edit2 :size="14" />
            </button>
            <button class="icon-btn-small delete" @click.stop="handleDelete(material)">
              <Trash2 :size="14" />
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
    
    <!-- 添加/编辑模态框 -->
    <MaterialEditor
      :show="showAddModal || showEditModal"
      :material="editingMaterial || undefined"
      @close="closeModal"
      @submit="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import {
  Search,
  Plus,
  Edit2,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Database,
  Box,
  FileText
} from 'lucide-vue-next'
import MaterialEditor from '../../components/MaterialEditor.vue'
import materialApi, { type Material } from '../../services/materialApi'

const materials = ref<Material[]>([])
const loading = ref(true)
const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = ref(12)
const showAddModal = ref(false)
const showEditModal = ref(false)
const editingMaterial = ref<Material | null>(null)

const filteredMaterials = computed(() => {
  let filtered = materials.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(material => 
      material.name.toLowerCase().includes(query) ||
      material.content?.text?.toLowerCase().includes(query)
    )
  }
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filtered.slice(start, end)
})

const totalPages = computed(() => {
  let filtered = materials.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(material => 
      material.name.toLowerCase().includes(query) ||
      material.content?.text?.toLowerCase().includes(query)
    )
  }
  return Math.ceil(filtered.length / itemsPerPage.value)
})

const loadMaterials = async () => {
  loading.value = true
  try {
    const response = await materialApi.getMaterials({ type: 'mixed' })
    if (response.success) {
      materials.value = response.data.items || []
    }
  } catch (error) {
    console.error('Failed to load materials:', error)
  } finally {
    loading.value = false
  }
}

const truncateText = (text: string, maxLength: number) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

const getCardTypeClass = (material: Material) => {
  return material.type === 'reference' ? 'is-reference' : 'is-mixed'
}

const getImageGridClass = (count: number) => {
  if (count === 1) return 'grid-1'
  if (count === 2) return 'grid-2'
  if (count === 3) return 'grid-3'
  return 'grid-4'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}

const handleMaterialClick = (material: Material) => {
  // Preview logic
}

const handleEdit = (material: Material) => {
  editingMaterial.value = material
  showEditModal.value = true
}

const handleDelete = async (material: Material) => {
  if (confirm(`Delete "${material.name}"?`)) {
    try {
      const response = await materialApi.deleteMaterial(material.id)
      if (response.success) await loadMaterials()
    } catch (error) {
      console.error('Delete failed:', error)
    }
  }
}

const handleSave = async (material: Partial<Material>) => {
  try {
    if (editingMaterial.value) {
      const response = await materialApi.updateMaterial(editingMaterial.value.id, material)
      if (response.success) {
        await loadMaterials()
        closeModal()
      }
    } else {
      const response = await materialApi.createMaterial(material as any)
      if (response.success) {
        await loadMaterials()
        closeModal()
      }
    }
  } catch (error) {
    console.error('Save failed:', error)
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  editingMaterial.value = null
}

watch(searchQuery, () => { currentPage.value = 1 })
onMounted(() => { loadMaterials() })
</script>

<style scoped>
.knowledge-container {
  width: 100%;
}

/* --- 🛠️ Toolbar --- */
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
  border: 1px solid transparent;
  transition: all 0.2s;
}

.search-box:focus-within {
  background: white;
  border-color: var(--macaron-mint);
  box-shadow: 0 0 0 3px rgba(181, 234, 215, 0.2);
}

.search-icon { color: var(--text-tertiary); margin-right: 0.5rem; }

.search-input {
  border: none;
  background: transparent;
  width: 100%;
  padding: 0.8rem 0;
  font-size: 0.95rem;
  color: var(--text-primary);
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: #EEE;
}

.stats-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 600;
}

.add-btn {
  padding: 0.6rem 1.2rem;
  font-size: 0.9rem;
  border-radius: 12px;
  background: linear-gradient(135deg, #6DB398, #4AAE8C);
  box-shadow: 0 4px 12px rgba(109, 179, 152, 0.3);
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(109, 179, 152, 0.4);
}

/* --- 🧩 Grid Layout --- */
.materials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.5rem;
}

.material-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
}

.material-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.06);
}

.card-body {
  padding: 1rem;
  flex: 1;
}

/* Image Grid Styles */
.image-grid {
  border-radius: 12px;
  overflow: hidden;
  height: 160px;
  margin-bottom: 1rem;
  display: grid;
  gap: 2px;
  position: relative;
}

.image-item {
  background-size: cover;
  background-position: center;
  width: 100%;
  height: 100%;
}

.grid-1 { grid-template-columns: 1fr; }
.grid-2 { grid-template-columns: 1fr 1fr; }
.grid-3 { grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; }
.grid-3 .image-item:first-child { grid-row: span 2; }
.grid-4 { grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; }

.more-overlay {
  position: absolute;
  bottom: 0; right: 0;
  width: 50%; height: 50%;
  background: rgba(0,0,0,0.5);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

/* Text Styles */
.text-preview {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.no-text { color: var(--text-tertiary); font-style: italic; }

/* Reference Styles */
.reference-cover {
  height: 140px;
  background: #FEF3C7;
  border-radius: 12px;
  margin-bottom: 1rem;
  position: relative;
  overflow: hidden;
}

.cover-img { width: 100%; height: 100%; object-fit: cover; }
.cover-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #D97706; }

.ref-badge {
  position: absolute;
  top: 8px; right: 8px;
  background: rgba(255,255,255,0.9);
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 700;
  color: #D97706;
}

/* Card Footer */
.card-footer {
  padding: 0.8rem 1rem;
  border-top: 1px solid #F5F5F5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date { font-size: 0.75rem; color: var(--text-tertiary); }

.footer-actions {
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.material-card:hover .footer-actions { opacity: 1; }

.icon-btn-small {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn-small:hover { background: #F0F0F0; color: var(--text-primary); }
.icon-btn-small.delete:hover { background: #FFF0F0; color: #EF4444; }

/* States */
.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  border-radius: 20px;
}

.empty-illustration { color: #6DB398; opacity: 0.6; margin-bottom: 1rem; }
.loading-spinner-mint {
  width: 30px; height: 30px;
  border: 3px solid #E2F0CB;
  border-top-color: #6DB398;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.page-btn {
  width: 36px; height: 36px;
  border-radius: 10px;
  border: 1px solid #EEE;
  background: white;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) { border-color: var(--macaron-mint); color: #6DB398; }
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.page-info { font-size: 0.9rem; color: var(--text-secondary); font-weight: 600; }
</style>