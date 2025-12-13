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
  border: 1px solid rgba(0,0,0,0.05);
  border-radius: 16px;
  overflow: hidden;
  color: var(--text-primary);
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.selector-header {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  background: #f8fafc;
}

.selector-header h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.search-box input {
  width: 100%;
  padding: 10px 12px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-primary);
  transition: all 0.2s;
}

.search-box input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.selector-filters {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
  overflow-x: auto;
  background: white;
}

.filter-btn {
  padding: 6px 12px;
  border: 1px solid rgba(0,0,0,0.05);
  background: #f1f5f9;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  color: var(--text-secondary);
}

.filter-btn:hover {
  color: var(--primary-color);
  background: white;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.filter-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.selected-materials {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  background: #f8fafc;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.btn-text {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  font-size: 12px;
  text-decoration: none;
}

.btn-text:hover {
  color: var(--error);
  text-decoration: underline;
}

.btn-text:hover {
  opacity: 1;
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
  border: 1px solid rgba(0,0,0,0.05);
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}

.item-icon {
  font-size: 14px;
  filter: none;
}

.item-name {
  flex: 1;
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.btn-remove {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  font-size: 14px;
  padding: 0 4px;
  transition: color 0.2s;
}

.btn-remove:hover {
  color: var(--error);
}

.materials-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: white;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 32px;
  color: var(--text-tertiary);
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0,0,0,0.1);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state-small {
  text-align: center;
  padding: 32px 16px;
  color: var(--text-tertiary);
}

.empty-state-small p {
  margin: 0 0 8px 0;
}

.link {
  color: var(--primary-color);
  text-decoration: underline;
  font-size: 12px;
}

.material-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.material-item {
  padding: 12px;
  border: 1px solid rgba(0,0,0,0.05);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: #f8fafc;
}

.material-item:hover {
  border-color: var(--primary-color);
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.material-item.selected {
  border-color: var(--primary-color);
  background: rgba(99, 102, 241, 0.05);
}

.item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.item-type-badge {
  font-size: 14px;
  filter: none;
}

.item-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.item-preview {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 6px;
}

.item-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.check-icon {
  color: var(--primary-color);
  font-weight: bold;
  font-size: 12px;
}

.load-more {
  padding: 16px;
  border-top: 1px solid rgba(0,0,0,0.05);
  text-align: center;
  background: #f8fafc;
}

.btn-load-more {
  padding: 8px 20px;
  background: white;
  border: 1px solid rgba(0,0,0,0.1);
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.btn-load-more:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}
</style>