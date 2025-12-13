<template>
  <div class="works-container animate-fade-in">
    <!-- 📊 数据概览卡片 -->
    <div class="stats-grid">
      <div class="stat-card glass-panel">
        <div class="stat-icon-wrapper pink">
          <BarChart2 :size="24" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ historyList.length }}</div>
          <div class="stat-label">Total Works</div>
        </div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon-wrapper mint">
          <CheckCircle2 :size="24" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ completedCount }}</div>
          <div class="stat-label">Completed</div>
        </div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon-wrapper purple">
          <Files :size="24" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ totalPages }}</div>
          <div class="stat-label">Total Pages</div>
        </div>
      </div>
    </div>

    <!-- 🏷️ 页面标题与操作 -->
    <div class="page-header">
      <h2 class="section-title">我的作品库</h2>
      <div class="header-actions">
        <button class="icon-btn refresh-btn" @click="loadHistory" :disabled="loading" title="刷新">
          <RefreshCw :size="20" :class="{ 'spinning': loading }" />
        </button>
      </div>
    </div>

    <!-- ⏳ 加载状态 -->
    <div v-if="loading && historyList.length === 0" class="state-container glass-panel">
      <div class="loading-spinner-pink"></div>
      <p>正在获取作品数据...</p>
    </div>

    <!-- 📭 空状态 -->
    <div v-else-if="historyList.length === 0" class="state-container empty-state glass-panel">
      <div class="empty-illustration">
        <FolderOpen :size="64" stroke-width="1" />
      </div>
      <h3>暂无作品</h3>
      <p>开始你的第一次创作之旅吧</p>
      <router-link to="/creation" class="btn btn-primary">
        <Sparkles :size="18" />
        立即创作
      </router-link>
    </div>

    <!-- 🖼️ 作品网格 -->
    <div v-else class="works-grid">
      <div 
        v-for="item in historyList" 
        :key="item.task_id" 
        class="work-card glass-panel" 
        @click="viewDetails(item)"
      >
        <!-- 预览图区域 -->
        <div class="card-preview">
          <div class="preview-bg" :style="getPreviewStyle(item)"></div>
          <div class="preview-overlay"></div>
          
          <!-- 状态标签 -->
          <div class="status-badge" :class="item.status">
            <span class="status-dot"></span>
            {{ getStatusText(item.status) }}
          </div>

          <!-- 悬浮操作栏 -->
          <div class="card-actions">
            <button
              class="action-circle-btn edit-btn"
              @click.stop="handleEdit(item)"
              title="编辑"
            >
              <Edit3 :size="16" />
            </button>
            <button
              class="action-circle-btn delete-btn"
              @click.stop="handleDelete(item)"
              :disabled="deleting.has(item.task_id || item.id)"
              title="删除"
            >
              <Trash2 :size="16" />
            </button>
          </div>
        </div>
        
        <!-- 内容区域 -->
        <div class="card-content">
          <h3 class="work-title" :title="item.topic">{{ item.topic }}</h3>
          <div class="work-meta">
            <div class="meta-item">
              <Calendar :size="14" />
              <span>{{ formatDate(item.created_at) }}</span>
            </div>
            <div class="meta-item">
              <Layers :size="14" />
              <span>{{ item.pages?.length || 0 }} 页</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getHistory, deleteHistory } from '../../services/api'
import { useAppStore } from '../../store'
import { 
  BarChart2, 
  CheckCircle2, 
  Files, 
  RefreshCw, 
  FolderOpen, 
  Sparkles,
  Edit3,
  Trash2,
  Calendar,
  Layers
} from 'lucide-vue-next'

const router = useRouter()
const store = useAppStore()
const historyList = ref<any[]>([])
const loading = ref(false)
const deleting = ref<Set<string>>(new Set())

// 计算统计数据
const completedCount = computed(() =>
  historyList.value.filter(item => item.status === 'completed').length
)

const totalPages = computed(() =>
  historyList.value.reduce((sum, item) => sum + (item.pages?.length || 0), 0)
)

const loadHistory = async () => {
  loading.value = true
  try {
    const response = await getHistory()
    if (response.success && response.data) {
      historyList.value = response.data.items || response.data || []
    } else {
      historyList.value = []
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
    historyList.value = []
  } finally {
    loading.value = false
  }
}

const viewDetails = (item: any) => {
  const outline = {
    task_id: item.task_id || item.id,
    topic: item.topic,
    pages: item.pages || []
  }
  store.setOutline(outline)
  if (item.reference_image) {
    store.setReferenceImage(item.reference_image)
  }
  router.push('/result')
}

const getPreviewStyle = (item: any) => {
  const firstImage = item.pages?.[0]?.image_url
  if (firstImage) {
    return {
      backgroundImage: `url(${firstImage})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  return {
    background: 'linear-gradient(135deg, #FFDAC1 0%, #FFB7B2 100%)'
  }
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    'completed': 'Completed',
    'failed': 'Failed',
    'pending': 'Processing'
  }
  return map[status] || status
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}

const handleDelete = async (item: any) => {
  const historyId = item.task_id || item.id
  if (!confirm(`Are you sure you want to delete "${item.topic}"?`)) {
    return
  }
  deleting.value.add(historyId)
  try {
    const response = await deleteHistory(historyId)
    if (response.success) {
      historyList.value = historyList.value.filter(h =>
        (h.task_id || h.id) !== historyId
      )
    }
  } catch (error: any) {
    console.error('Delete failed:', error)
  } finally {
    deleting.value.delete(historyId)
  }
}

const handleEdit = (item: any) => {
  const outline = {
    task_id: item.task_id || item.id,
    topic: item.topic,
    pages: item.pages || []
  }
  store.setOutline(outline)
  if (item.reference_image) {
    store.setReferenceImage(item.reference_image)
  }
  router.push({
    path: '/creation/editor',
    query: {
      edit: item.task_id || item.id,
      topic: item.topic
    }
  })
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.works-container {
  width: 100%;
}

/* --- 📊 Stats Cards --- */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 24px;
  border: 1px solid rgba(255,255,255,0.6);
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon-wrapper.pink { background: #FFF0F0; color: var(--macaron-pink-deep); }
.stat-icon-wrapper.mint { background: #F0FFF9; color: #6DB398; }
.stat-icon-wrapper.purple { background: #F8F7FF; color: #9FA8DA; }

.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 2rem; font-weight: 800; color: var(--text-primary); line-height: 1; margin-bottom: 4px; }
.stat-label { font-size: 0.85rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.5px; }

/* --- 🏷️ Header --- */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 0 0.5rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
  font-family: 'Quicksand', sans-serif;
}

.icon-btn {
  background: white;
  border: 1px solid rgba(0,0,0,0.05);
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: var(--macaron-pink);
  color: white;
  transform: rotate(15deg);
}

.spinning { animation: spin 1s linear infinite; }

/* --- 🖼️ Grid Layout --- */
.works-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
}

.work-card {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  cursor: pointer;
  background: white;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  border: 1px solid rgba(255,255,255,0.8);
}

.work-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px rgba(0,0,0,0.08);
}

/* Preview Area */
.card-preview {
  height: 200px;
  position: relative;
  overflow: hidden;
}

.preview-bg {
  width: 100%;
  height: 100%;
  transition: transform 0.6s ease;
}

.work-card:hover .preview-bg {
  transform: scale(1.1);
}

.preview-overlay {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background: linear-gradient(to bottom, rgba(0,0,0,0) 60%, rgba(0,0,0,0.4));
  opacity: 0.6;
}

/* Status Badge */
.status-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(4px);
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.status-dot { width: 6px; height: 6px; border-radius: 50%; background: #ccc; }
.status-badge.completed { color: #059669; }
.status-badge.completed .status-dot { background: #10B981; }
.status-badge.failed { color: #DC2626; }
.status-badge.failed .status-dot { background: #EF4444; }

/* Action Buttons */
.card-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transform: translateY(-10px);
  transition: all 0.3s ease;
}

.work-card:hover .card-actions {
  opacity: 1;
  transform: translateY(0);
}

.action-circle-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.edit-btn:hover { color: #6366F1; transform: scale(1.1); }
.delete-btn:hover { color: #EF4444; transform: scale(1.1); }

/* Content Area */
.card-content {
  padding: 1.2rem;
}

.work-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 0 0.8rem 0;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: 'Quicksand', sans-serif;
}

.work-meta {
  display: flex;
  gap: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  color: var(--text-tertiary);
  font-weight: 600;
}

/* States */
.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  border-radius: 24px;
}

.empty-illustration {
  color: var(--macaron-pink);
  margin-bottom: 1.5rem;
  opacity: 0.8;
}

.state-container h3 {
  font-size: 1.25rem;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.state-container p {
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

/* Loading Spinner */
.loading-spinner-pink {
  width: 30px;
  height: 30px;
  border: 3px solid #FFE0E0;
  border-top-color: var(--macaron-pink-deep);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Responsive */
@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr; gap: 1rem; }
  .works-grid { grid-template-columns: 1fr; }
}
</style>