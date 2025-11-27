<template>
  <div class="generator">
    <ProcessSteps :current-step="2" />

    <div class="page-header">
      <h2>文案大纲确认</h2>
      <div class="header-actions" v-if="store.currentOutline">
        <button @click="addNewPage" class="btn btn-secondary">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon-svg">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          添加页面
        </button>
        <button @click="goToResult" class="btn btn-primary">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon-svg">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l-.249 1.74" />
          </svg>
          开始生成图片
        </button>
      </div>
    </div>
    
    <!-- 大纲预览和编辑区 -->
    <div v-if="store.currentOutline" class="outline-section">
      <div class="section-title">
        <h3>内容大纲：{{ store.currentOutline.topic }}</h3>
      </div>
      
      <div class="pages-grid">
        <div
          v-for="(page, index) in store.currentOutline.pages"
          :key="page.page_number"
          class="page-card"
          :class="{ 'editing': editingIndex === index }"
        >
          <div class="page-header-row">
            <div class="page-number">P{{ page.page_number }}</div>
            <div class="page-actions">
              <button
                v-if="editingIndex !== index"
                @click="startEdit(index)"
                class="btn-icon"
                title="编辑"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon-svg-sm">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                </svg>
              </button>
              <button
                @click="deletePage(index)"
                class="btn-icon btn-danger"
                title="删除"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon-svg-sm">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                </svg>
              </button>
            </div>
          </div>

          <!-- 编辑模式 -->
          <template v-if="editingIndex === index">
            <div class="edit-form">
              <div class="form-group">
                <label>标题</label>
                <input
                  v-model="editForm.title"
                  type="text"
                  class="form-input"
                  placeholder="输入页面标题"
                />
              </div>
              <div class="form-group">
                <label>描述</label>
                <textarea
                  v-model="editForm.description"
                  class="form-textarea"
                  placeholder="输入页面描述"
                  rows="4"
                ></textarea>
              </div>
              <div class="form-actions">
                <button @click="saveEdit" class="btn btn-sm btn-primary">保存</button>
                <button @click="cancelEdit" class="btn btn-sm btn-secondary">取消</button>
              </div>
            </div>
          </template>

          <!-- 查看模式 -->
          <template v-else>
            <h4>{{ page.title }}</h4>
            <p>{{ page.description }}</p>
          </template>
        </div>
      </div>
    </div>
    
    <!-- 无大纲提示 -->
    <div v-if="!store.currentOutline" class="empty-state">
      <p>请先在首页生成内容大纲</p>
      <button @click="goHome" class="btn btn-primary">前往首页</button>
    </div>

    <!-- 底部操作按钮 -->
    <div class="actions-footer" v-if="store.currentOutline">
      <button @click="goHome" class="btn btn-secondary">返回首页</button>
      <button
        v-if="hasGeneratedImages"
        @click="goToResult"
        class="btn btn-outline"
      >
        查看生成结果
      </button>
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

// 编辑状态
const editingIndex = ref<number | null>(null)
const editForm = ref({
  title: '',
  description: ''
})

// 检查是否有生成的图片
const hasGeneratedImages = computed(() => {
  return store.currentOutline?.pages?.some(p => !!p.image_url) ?? false
})

// 开始编辑
const startEdit = (index: number) => {
  if (!store.currentOutline) return
  
  editingIndex.value = index
  const page = store.currentOutline.pages[index]
  editForm.value = {
    title: page.title,
    description: page.description
  }
}

// 保存编辑
const saveEdit = () => {
  if (!store.currentOutline || editingIndex.value === null) return
  
  const index = editingIndex.value
  store.currentOutline.pages[index] = {
    ...store.currentOutline.pages[index],
    title: editForm.value.title,
    description: editForm.value.description
  }
  
  cancelEdit()
}

// 取消编辑
const cancelEdit = () => {
  editingIndex.value = null
  editForm.value = {
    title: '',
    description: ''
  }
}

// 删除页面
const deletePage = (index: number) => {
  if (!store.currentOutline) return
  
  if (confirm('确定要删除这个页面吗？')) {
    store.currentOutline.pages.splice(index, 1)
    // 重新调整页码
    store.currentOutline.pages.forEach((page, idx) => {
      page.page_number = idx + 1
    })
  }
}

// 添加新页面
const addNewPage = () => {
  if (!store.currentOutline) return
  
  const newPageNumber = store.currentOutline.pages.length + 1
  store.currentOutline.pages.push({
    page_number: newPageNumber,
    title: `新页面 ${newPageNumber}`,
    description: '请编辑页面描述'
  })
  
  // 自动进入编辑模式
  startEdit(store.currentOutline.pages.length - 1)
}

// 跳转到结果页并开始生成
const goToResult = () => {
  if (!store.currentOutline) {
    console.warn('没有可用的大纲')
    return
  }
  // 跳转到结果页，结果页会自动开始生成
  router.push('/result')
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 挂载时检查是否有大纲
onMounted(() => {
  if (!store.currentOutline) {
    console.warn('No outline available')
  }
})
</script>

<style scoped>
.generator {
  max-width: 1200px;
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

.header-actions {
  display: flex;
  gap: 1rem;
}

/* 大纲区域 */
.outline-section {
  margin-bottom: 3rem;
}

.section-title {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.section-title h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 600;
}

.pages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.page-card {
  background: var(--surface-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  transition: var(--transition);
}

.page-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--border-hover);
}

.page-card.editing {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px var(--primary-light);
}

.page-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.page-number {
  display: inline-block;
  background: var(--primary-light);
  color: var(--primary-color);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.page-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--text-secondary);
  transition: var(--transition);
}

.btn-icon:hover {
  background: var(--hover-bg);
  color: var(--primary-color);
}

.btn-icon.btn-danger:hover {
  background: #fee;
  color: #dc2626;
}

.icon-svg-sm {
  width: 1.125rem;
  height: 1.125rem;
}

.page-card h4 {
  margin: 0 0 0.75rem;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 600;
}

.page-card p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.6;
}

/* 编辑表单 */
.edit-form {
  margin-top: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 500;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 0.95rem;
  color: var(--text-primary);
  background: var(--bg-color);
  transition: var(--transition);
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px var(--primary-light);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.empty-state {
  text-align: center;
  padding: 6rem 2rem;
  background: var(--surface-color);
  border-radius: var(--radius-lg);
  border: 1px dashed var(--border-color);
}

.empty-state p {
  color: var(--text-secondary);
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.actions-footer {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: center;
  gap: 1rem;
}
</style>