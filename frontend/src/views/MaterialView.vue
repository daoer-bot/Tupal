<template>
  <div class="material-view">
    <div class="view-header">
      <div class="header-left">
        <h1><Package class="header-icon" /> 素材中心</h1>
        <p class="subtitle">管理你的创作素材，让内容创作更高效</p>
      </div>
      <button class="btn btn-primary" @click="showCreateModal">
        <Plus :size="18" /> 创建素材
      </button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="category-tabs">
        <button
          class="tab-btn"
          :class="{ active: !filters.category }"
          @click="setCategory('')"
        >
          全部
        </button>
        <button
          v-for="cat in categories"
          :key="cat.name"
          class="tab-btn"
          :class="{ active: filters.category === cat.name }"
          @click="setCategory(cat.name)"
        >
          <component :is="cat.icon" :size="16" />
          <span>{{ cat.name }}</span>
        </button>
      </div>

      <div class="search-box">
        <input
          v-model="filters.keyword"
          type="text"
          placeholder="搜索素材..."
          @keyup.enter="loadMaterials"
        />
        <button class="btn-search" @click="loadMaterials">
          <Search :size="18" />
        </button>
      </div>
    </div>

    <!-- 素材列表 -->
    <div class="material-list" v-if="!loading && materials.length > 0">
      <MaterialCard
        v-for="material in materials"
        :key="material.id"
        :material="material"
        @click="viewMaterial"
        @edit="editMaterial"
        @delete="confirmDelete"
      />
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else-if="!loading && materials.length === 0">
      <div class="empty-icon">
        <Package :size="64" :stroke-width="1.5" />
      </div>
      <h3>还没有素材</h3>
      <p>创建你的第一个素材，开始高效创作之旅</p>
      <button class="btn btn-primary" @click="showCreateModal">
        <Plus :size="18" /> 创建素材
      </button>
    </div>

    <!-- 加载状态 -->
    <div class="loading-state" v-if="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="pagination.total_pages > 1">
      <button
        class="btn btn-secondary"
        :disabled="pagination.page === 1"
        @click="goToPage(pagination.page - 1)"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ pagination.page }} / {{ pagination.total_pages }} 页
      </span>
      <button
        class="btn btn-secondary"
        :disabled="pagination.page === pagination.total_pages"
        @click="goToPage(pagination.page + 1)"
      >
        下一页
      </button>
    </div>

    <!-- 素材编辑器模态框 -->
    <MaterialEditor
      v-if="showEditor"
      :material="editingMaterial"
      @close="closeEditor"
      @submit="handleSubmit"
    />

    <!-- 删除确认对话框 -->
    <div class="modal-overlay" v-if="showDeleteConfirm" @click.self="showDeleteConfirm = false">
      <div class="modal-dialog">
        <h3>确认删除</h3>
        <p>确定要删除素材 "{{ deletingMaterial?.name }}" 吗？此操作不可恢复。</p>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showDeleteConfirm = false">
            取消
          </button>
          <button class="btn btn-danger" @click="handleDelete">
            确认删除
          </button>
        </div>
      </div>
    </div>

    <!-- 提示消息 -->
    <div class="toast" :class="{ show: toast.show, [toast.type]: true }">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Package, Plus, Search, Image, BarChart3, Home, ZoomIn, Coffee, Scale, FileText } from 'lucide-vue-next'
import MaterialCard from '../components/MaterialCard.vue'
import MaterialEditor from '../components/MaterialEditor.vue'
import materialApi, { type Material } from '../services/materialApi'

// 状态管理
const loading = ref(false)
const materials = ref<Material[]>([])
const showEditor = ref(false)
const editingMaterial = ref<Material | undefined>()
const showDeleteConfirm = ref(false)
const deletingMaterial = ref<Material | undefined>()

// 7大分类定义（移除了数据类素材）
const categories = [
  { name: '封面素材', icon: Image },
  { name: '信息型素材', icon: BarChart3 },
  { name: '场景素材', icon: Home },
  { name: '细节特写素材', icon: ZoomIn },
  { name: '生活碎片素材', icon: Coffee },
  { name: '对比素材', icon: Scale },
  { name: '文案素材', icon: FileText },
]

// 筛选条件
const filters = reactive({
  category: '',
  keyword: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  page_size: 12,
  total: 0,
  total_pages: 0,
  has_more: false
})

// 提示消息
const toast = reactive({
  show: false,
  message: '',
  type: 'success'
})

// 设置分类筛选
function setCategory(category: string) {
  filters.category = category
  pagination.page = 1
  loadMaterials()
}

// 加载素材列表
async function loadMaterials() {
  loading.value = true
  try {
    const response = await materialApi.getMaterials({
      category: filters.category || undefined,
      keyword: filters.keyword || undefined,
      page: pagination.page,
      page_size: pagination.page_size
    })

    if (response.success && response.data) {
      materials.value = response.data.items
      Object.assign(pagination, response.data.pagination)
    }
  } catch (error) {
    showToast('加载素材列表失败', 'error')
    console.error('加载素材列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 显示创建模态框
function showCreateModal() {
  editingMaterial.value = undefined
  showEditor.value = true
}

// 查看素材详情
function viewMaterial(material: Material) {
  editMaterial(material)
}

// 编辑素材
function editMaterial(material: Material) {
  editingMaterial.value = material
  showEditor.value = true
}

// 确认删除
function confirmDelete(material: Material) {
  deletingMaterial.value = material
  showDeleteConfirm.value = true
}

// 处理删除
async function handleDelete() {
  if (!deletingMaterial.value) return

  try {
    const response = await materialApi.deleteMaterial(deletingMaterial.value.id)
    if (response.success) {
      showToast('素材删除成功', 'success')
      showDeleteConfirm.value = false
      deletingMaterial.value = undefined
      loadMaterials()
    } else {
      showToast(response.error || '删除失败', 'error')
    }
  } catch (error) {
    showToast('删除素材失败', 'error')
    console.error('删除素材失败:', error)
  }
}

// 关闭编辑器
function closeEditor() {
  showEditor.value = false
  editingMaterial.value = undefined
}

// 处理提交
async function handleSubmit(data: any) {
  try {
    let response
    if (data.material_id) {
      // 更新素材
      response = await materialApi.updateMaterial(data.material_id, {
        name: data.name,
        content: data.content,
        tags: data.tags,
        description: data.description,
        category: data.category
      })
    } else {
      // 创建素材
      response = await materialApi.createMaterial({
        name: data.name,
        type: data.type,
        category: data.category,
        content: data.content,
        tags: data.tags,
        description: data.description
      })
    }

    if (response.success) {
      showToast(data.material_id ? '素材更新成功' : '素材创建成功', 'success')
      closeEditor()
      loadMaterials()
    } else {
      showToast(response.error || '操作失败', 'error')
    }
  } catch (error) {
    showToast('操作失败', 'error')
    console.error('操作失败:', error)
  }
}

// 跳转到指定页
function goToPage(page: number) {
  pagination.page = page
  loadMaterials()
}

// 显示提示消息
function showToast(message: string, type: 'success' | 'error' | 'info' = 'success') {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => {
    toast.show = false
  }, 3000)
}

// 页面加载时初始化
onMounted(() => {
  loadMaterials()
})
</script>

<style scoped>
.material-view {
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.header-left h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 700;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  color: #3b82f6;
}

.subtitle {
  margin: 0;
  font-size: 16px;
  color: #6b7280;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 20px;
}

.category-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  flex: 1;
}

.tab-btn {
  padding: 8px 16px;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 20px;
  font-size: 14px;
  color: #4b5563;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.tab-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.search-box {
  display: flex;
  align-items: center;
}

.search-box input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-right: none;
  border-radius: 6px 0 0 6px;
  font-size: 14px;
  min-width: 200px;
}

.search-box input:focus {
  outline: none;
  border-color: #3b82f6;
}

.btn-search {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  border-left: none;
  background: white;
  border-radius: 0 6px 6px 0;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-search:hover {
  background: #f3f4f6;
}

.material-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 12px;
  border: 1px dashed #e5e7eb;
}

.empty-icon {
  margin-bottom: 16px;
  color: #9ca3af;
  display: flex;
  justify-content: center;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #111827;
}

.empty-state p {
  margin: 0 0 24px 0;
  color: #6b7280;
}

.loading-state {
  text-align: center;
  padding: 80px 20px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;
}

.page-info {
  font-size: 14px;
  color: #6b7280;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-dialog {
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
}

.modal-dialog h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
}

.modal-dialog p {
  margin: 0 0 20px 0;
  color: #6b7280;
  line-height: 1.6;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.toast {
  position: fixed;
  bottom: 32px;
  right: 32px;
  padding: 16px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  transform: translateY(100px);
  opacity: 0;
  transition: all 0.3s;
  z-index: 2000;
}

.toast.show {
  transform: translateY(0);
  opacity: 1;
}

.toast.success {
  background: #10b981;
  color: white;
}

.toast.error {
  background: #ef4444;
  color: white;
}

.toast.info {
  background: #3b82f6;
  color: white;
}
</style>