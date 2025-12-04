<template>
  <div class="material-selector">
    <div class="selector-header">
      <h3>📦 选择素材</h3>
      <div class="search-box">
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索素材..."
          @input="handleSearch"
        />
      </div>
    </div>

    <!-- 筛选器 -->
    <div class="selector-filters">
      <button
        v-for="type in materialTypes"
        :key="type.value"
        class="filter-btn"
        :class="{ active: selectedType === type.value }"
        @click="selectedType = type.value; loadMaterials()"
      >
        {{ type.label }}
      </button>
    </div>

    <!-- 已选择的素材 -->
    <div class="selected-materials" v-if="modelValue.length > 0">
      <div class="section-title">
        <span>已选择 ({{ modelValue.length }})</span>
        <button class="btn-text" @click="clearSelection">清空</button>
      </div>
      <div class="selected-list">
        <div
          v-for="material in selectedMaterialsData"
          :key="material.id"
          class="selected-item"
        >
          <span class="item-icon">{{ getTypeIcon(material.type) }}</span>
          <span class="item-name">{{ material.name }}</span>
          <button class="btn-remove" @click="removeMaterial(material.id)">✕</button>
        </div>
      </div>
    </div>

    <!-- 素材列表 -->
    <div class="materials-list">
      <div class="section-title">可选素材</div>
      
      <div v-if="loading" class="loading-state">
        <div class="spinner-small"></div>
        <span>加载中...</span>
      </div>

      <div v-else-if="materials.length === 0" class="empty-state-small">
        <p>暂无素材</p>
        <router-link to="/materials" class="link">前往创建</router-link>
      </div>

      <div v-else class="material-items">
        <div
          v-for="material in materials"
          :key="material.id"
          class="material-item"
          :class="{ selected: isSelected(material.id) }"
          @click="toggleMaterial(material)"
        >
          <div class="item-header">
            <span class="item-type-badge" :class="`type-${material.type}`">
              {{ getTypeIcon(material.type) }}
            </span>
            <span class="item-name">{{ material.name }}</span>
          </div>
          <div class="item-preview">
            {{ getPreviewText(material) }}
          </div>
          <div class="item-footer">
            <span v-if="isSelected(material.id)" class="check-icon">✓</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载更多 -->
    <div class="load-more" v-if="hasMore && !loading">
      <button class="btn-load-more" @click="loadMore">
        加载更多
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import materialApi, { type Material } from '../services/materialApi'

const props = defineProps<{
  modelValue: string[]  // 已选择的素材ID列表
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

// 状态
const loading = ref(false)
const materials = ref<Material[]>([])
const selectedMaterialsData = ref<Material[]>([])
const searchKeyword = ref('')
const selectedType = ref('')
const page = ref(1)
const hasMore = ref(false)

// 素材类型
const materialTypes = [
  { value: '', label: '全部' },
  { value: 'text', label: '📝 文本' },
  { value: 'image', label: '🖼️ 图片' },
  { value: 'reference', label: '📚 参考' }
]

// 加载素材列表
async function loadMaterials(append = false) {
  loading.value = true
  try {
    const response = await materialApi.getMaterials({
      type: selectedType.value || undefined,
      keyword: searchKeyword.value || undefined,
      page: page.value,
      page_size: 20
    })

    if (response.success && response.data) {
      if (append) {
        materials.value.push(...response.data.items)
      } else {
        materials.value = response.data.items
      }
      hasMore.value = response.data.pagination.has_more
    }
  } catch (error) {
    console.error('加载素材失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载已选择的素材详情
async function loadSelectedMaterials() {
  if (props.modelValue.length === 0) {
    selectedMaterialsData.value = []
    return
  }

  try {
    const response = await materialApi.getMaterialsBatch(props.modelValue)
    if (response.success && response.data) {
      selectedMaterialsData.value = response.data
    }
  } catch (error) {
    console.error('加载已选素材失败:', error)
  }
}

// 加载更多
function loadMore() {
  page.value++
  loadMaterials(true)
}

// 搜索处理
let searchTimer: any = null
function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    loadMaterials()
  }, 500)
}

// 判断是否已选择
function isSelected(materialId: string): boolean {
  return props.modelValue.includes(materialId)
}

// 切换素材选择状态
function toggleMaterial(material: Material) {
  const newValue = [...props.modelValue]
  const index = newValue.indexOf(material.id)
  
  if (index > -1) {
    newValue.splice(index, 1)
    selectedMaterialsData.value = selectedMaterialsData.value.filter(m => m.id !== material.id)
  } else {
    newValue.push(material.id)
    selectedMaterialsData.value.push(material)
  }
  
  emit('update:modelValue', newValue)
}

// 移除素材
function removeMaterial(materialId: string) {
  const newValue = props.modelValue.filter(id => id !== materialId)
  selectedMaterialsData.value = selectedMaterialsData.value.filter(m => m.id !== materialId)
  emit('update:modelValue', newValue)
}

// 清空选择
function clearSelection() {
  selectedMaterialsData.value = []
  emit('update:modelValue', [])
}

// 获取类型图标
function getTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    text: '📝',
    image: '🖼️',
    reference: '📚'
  }
  return icons[type] || '📄'
}

// 获取预览文本
function getPreviewText(material: Material): string {
  if (material.type === 'text') {
    const text = material.content.text || ''
    return text.length > 60 ? text.substring(0, 60) + '...' : text
  } else if (material.type === 'image') {
    return material.content.description || '图片素材'
  } else if (material.type === 'reference') {
    const content = material.content.content || ''
    return content.length > 60 ? content.substring(0, 60) + '...' : (material.content.reference_type || '参考素材')
  }
  return ''
}

// 监听选中ID变化，加载详情
watch(() => props.modelValue, () => {
  loadSelectedMaterials()
}, { immediate: true })

// 页面加载时初始化
onMounted(() => {
  loadMaterials()
})
</script>

<style scoped>
.material-selector {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.selector-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.selector-header h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.search-box input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.selector-filters {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  overflow-x: auto;
}

.filter-btn {
  padding: 6px 12px;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.filter-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.selected-materials {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 12px;
}

.btn-text {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: 13px;
}

.selected-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.selected-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.item-icon {
  font-size: 16px;
}

.item-name {
  flex: 1;
  font-size: 14px;
  color: #374151;
}

.btn-remove {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  font-size: 16px;
  padding: 0 4px;
}

.btn-remove:hover {
  color: #ef4444;
}

.materials-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 32px;
  color: #6b7280;
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state-small {
  text-align: center;
  padding: 32px 16px;
  color: #6b7280;
}

.empty-state-small p {
  margin: 0 0 8px 0;
}

.link {
  color: #3b82f6;
  text-decoration: none;
}

.material-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.material-item {
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.material-item:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.material-item.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.item-type-badge {
  font-size: 16px;
}

.item-name {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
}

.item-preview {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
  margin-bottom: 8px;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.check-icon {
  color: #3b82f6;
  font-weight: bold;
}

.load-more {
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  text-align: center;
}

.btn-load-more {
  padding: 8px 20px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-load-more:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}
</style>