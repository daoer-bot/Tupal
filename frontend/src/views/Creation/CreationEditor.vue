<template>
  <div class="editor-container">
    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <span class="error-icon">!</span>
      <p>{{ error }}</p>
      <button @click="error = ''" class="btn-close"><X :size="14" /></button>
    </div>

    <div v-if="store.currentOutline" class="editor-layout">
      <!-- 左侧侧边栏：配置与操作 -->
      <aside class="editor-sidebar">
        <div class="sidebar-header">
          <div class="logo-area">
            <span class="app-name">✨ CREATION STUDIO</span>
          </div>
        </div>

        <div class="sidebar-content">
          <!-- 主题设置 -->
          <div class="config-group">
            <label class="group-label">Theme 核心主题</label>
            <div class="input-wrapper">
              <textarea
                v-model="mainCaption"
                class="sidebar-input textarea"
                placeholder="这个故事是关于什么的..."
                rows="4"
              ></textarea>
            </div>
          </div>

          <!-- 风格设置 -->
          <div class="config-group">
            <label class="group-label">Visual Style 画面风格</label>
            <div class="style-input-row">
              <input
                v-model="globalStyle"
                class="sidebar-input"
                placeholder="例如：赛博朋克、水彩..."
              />
              <div class="style-actions">
                <button @click="applyGlobalStyle('append')" class="btn-icon" title="追加到所有帧">
                  <Plus :size="14" />
                </button>
                <button @click="applyGlobalStyle('replace')" class="btn-icon" title="替换所有帧">
                  <RefreshCw :size="14" />
                </button>
              </div>
            </div>
          </div>

          <!-- 参数设置 -->
          <div class="config-group">
            <label class="group-label">Settings 生成参数</label>
            
            <div class="param-item">
              <!-- <span class="param-label">Quality</span> -->
              <div class="segment-control">
                <button
                  v-for="q in qualityOptions"
                  :key="q.value"
                  @click="selectQuality(q.value)"
                  class="segment-btn"
                  :class="{ active: store.imageGenerationConfig.quality === q.value }"
                >
                  {{ q.label }}
                </button>
              </div>
            </div>

            <div class="param-item">
              <!-- <span class="param-label">Ratio</span> -->
              <div class="ratio-grid">
                <button
                  v-for="ratio in ratioOptions"
                  :key="ratio.value"
                  @click="selectRatio(ratio.value)"
                  class="ratio-btn"
                  :class="{ active: store.imageGenerationConfig.aspectRatio === ratio.value }"
                  :title="ratio.label"
                >
                  <div class="ratio-box" :style="{ aspectRatio: ratio.value.replace(':', '/') }"></div>
                  <span>{{ ratio.label }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部生成按钮 -->
        <div class="sidebar-footer">
          <div class="status-indicator">
            <div class="status-dot" :class="{ 'pulsing': isGenerating }"></div>
            <span class="status-text">{{ isGenerating ? 'AI 正在思考...' : '准备生成' }}</span>
          </div>
          <button
            class="btn-generate"
            @click="handleGenerate"
            :disabled="isGenerating"
          >
            <Sparkles v-if="!isGenerating" :size="18" class="btn-icon-left" />
            <span v-if="isGenerating">正在生成画面...</span>
            <span v-else>✨ 开始生成分镜</span>
          </button>
        </div>
      </aside>

      <!-- 右侧主内容：脚本编辑 -->
      <main class="editor-main">
        <!-- 顶部导航 -->
        <header class="main-header">
          <div class="breadcrumb">
            <button class="crumb-btn" @click="goBack" title="返回首页">
              <ArrowLeft :size="18" />
            </button>
            <!-- <span class="separator">/</span> -->
            <span class="current">故事编辑器 Editor</span>
          </div>
          
          <div class="header-actions">
             <button @click="clearAllPrompts" class="action-link danger">清空所有</button>
          </div>
        </header>

        <!-- 脚本内容区 -->
        <div class="script-content">
          <div class="storyboard-header">
            <h2>分镜脚本 Storyboard</h2>
            <button @click="addNewPage" class="btn-add-frame">
              <Plus :size="16" />
              <span>添加新帧</span>
            </button>
          </div>

          <div class="script-list">
            <div
              v-for="(page, index) in store.currentOutline.pages"
              :key="page.page_number"
              class="script-row"
              :class="{ 'focused': focusedIndex === index }"
            >
              <div class="frame-index">
                <span>{{ String(page.page_number).padStart(2, '0') }}</span>
              </div>
              
              <div class="frame-content">
                <div class="frame-header">
                   <span class="frame-title">Frame {{ page.page_number }}</span>
                   <div class="frame-actions">
                    <button @click="copyPrompt(index)" class="icon-btn" title="Copy">
                      <Copy :size="14" />
                    </button>
                    <button @click="deletePage(index)" class="icon-btn danger" title="Delete">
                      <X :size="14" />
                    </button>
                   </div>
                </div>
                <div class="input-container">
                  <MentionInput
                    v-model="page.description"
                    placeholder="// 描述这一帧的画面..."
                    :multiline="true"
                    :rows="4"
                    input-class="script-input"
                    @focus="focusedIndex = index"
                    @blur="focusedIndex = null"
                  />
                </div>
              </div>
            </div>
          </div>
          
          <!-- 底部添加按钮占位，方便操作 -->
          <div class="bottom-spacer" @click="addNewPage">
            <div class="add-placeholder">
              <Plus :size="24" />
              <span>点击添加新画面</span>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- 空状态 -->
    <div v-if="!store.currentOutline" class="empty-state">
      <div class="empty-content">
        <FileText :size="48" class="empty-icon"/>
        <h3>暂无内容</h3>
        <p>请选择一个模板或开始新项目 🧁</p>
        <button @click="goToCreationHome" class="btn-primary">
          返回创作中心
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Copy, X, Sparkles, FileText, Plus, RefreshCw } from 'lucide-vue-next'
import { useAppStore } from '../../store'
import MentionInput from '../../components/MentionInput.vue'
import materialApi from '../../services/materialApi'

const router = useRouter()
const route = useRoute()
const store = useAppStore()

// 状态
const focusedIndex = ref<number | null>(null)
const error = ref('')
const isGenerating = ref(false)
const globalStyle = ref('')

// 配置选项
const qualityOptions = [
  { label: 'SD', value: '1k' as const },
  { label: 'HD', value: '2k' as const },
  { label: '4K', value: '4k' as const }
]

const ratioOptions = [
  { label: '1:1', value: '1:1' as const },
  { label: '4:3', value: '4:3' as const },
  { label: '3:4', value: '3:4' as const },
  { label: '16:9', value: '16:9' as const },
  { label: '9:16', value: '9:16' as const },
]

// 计算属性
const mainCaption = computed({
  get: () => {
    return store.currentOutline?.pages[0]?.xiaohongshu_content || ''
  },
  set: (val: string) => {
    if (!store.currentOutline) return
    store.currentOutline.pages.forEach(p => {
      p.xiaohongshu_content = val
    })
  }
})

// 方法
const goBack = () => {
  router.push('/creation')
}

const goToCreationHome = () => {
  router.push('/creation')
}

const applyGlobalStyle = (mode: 'append' | 'replace') => {
  if (!store.currentOutline || !globalStyle.value) return
  
  store.currentOutline.pages.forEach(p => {
    if (mode === 'replace') {
      p.description = globalStyle.value
    } else {
      p.description = p.description ? `${p.description} ${globalStyle.value}` : globalStyle.value
    }
  })
}

const copyPrompt = (index: number) => {
  if (!store.currentOutline) return
  const text = store.currentOutline.pages[index].description
  navigator.clipboard.writeText(text)
}

const deletePage = (index: number) => {
  if (!store.currentOutline) return
  if (store.currentOutline.pages.length <= 1) {
    error.value = 'At least one frame is required'
    return
  }
  
  if (confirm('Delete this frame?')) {
    store.currentOutline.pages.splice(index, 1)
    store.currentOutline.pages.forEach((p, i) => {
      p.page_number = i + 1
    })
  }
}

const clearAllPrompts = () => {
  if (!store.currentOutline) return
  if (confirm('Clear all prompts?')) {
    store.currentOutline.pages.forEach(p => p.description = '')
  }
}

const addNewPage = () => {
  if (!store.currentOutline) return
  const newPageNum = store.currentOutline.pages.length + 1
  store.currentOutline.pages.push({
    page_number: newPageNum,
    title: `Page ${newPageNum}`,
    description: '',
    xiaohongshu_content: mainCaption.value
  })
  // Scroll to bottom logic could be added here
}

const selectQuality = (quality: '1k' | '2k' | '4k') => {
  store.setImageGenerationConfig({
    ...store.imageGenerationConfig,
    quality
  })
}

const selectRatio = (aspectRatio: '4:3' | '3:4' | '16:9' | '9:16' | '2:3' | '3:2' | '1:1' | '4:5' | '5:4' | '21:9') => {
  store.setImageGenerationConfig({
    ...store.imageGenerationConfig,
    aspectRatio
  })
}

const handleGenerate = async () => {
  if (!store.currentOutline) return
  
  const hasEmptyPrompt = store.currentOutline.pages.some(p => !p.description || !p.description.trim())
  if (hasEmptyPrompt) {
    error.value = 'Please ensure all frames have prompts'
    return
  }
  
  if (!mainCaption.value || !mainCaption.value.trim()) {
    error.value = 'Please enter theme content'
    return
  }

  isGenerating.value = true
  error.value = ''
  
  try {
    const prompts = store.currentOutline.pages.map(p => p.description)
    const processResult = await materialApi.processBatchPrompts(prompts)
    
    if (processResult.success && processResult.enhanced_prompts) {
      processResult.enhanced_prompts.forEach((enhancedPrompt, index) => {
        if (store.currentOutline && store.currentOutline.pages[index]) {
          const page = store.currentOutline.pages[index] as any
          if (!page.original_description) {
            page.original_description = page.description
          }
          page.description = enhancedPrompt
        }
      })
      
      if (processResult.reference_images && processResult.reference_images.length > 0) {
        if (!store.referenceImage) {
          store.referenceImage = processResult.reference_images[0]
        }
      }
    }
    
    setTimeout(() => {
      isGenerating.value = false
      router.push('/result')
    }, 500)
    
  } catch (err: any) {
    error.value = err.message || 'Generation failed'
    isGenerating.value = false
  }
}

onMounted(() => {
  const topic = route.query.topic as string
  if (topic && store.currentOutline) {
    store.currentOutline.pages.forEach(p => {
      p.xiaohongshu_content = topic
    })
    router.replace({ query: {} })
  }
  
  if (!store.currentOutline) {
    console.warn('No outline available')
  }
})
</script>

<style scoped>
.editor-container {
  height: calc(100vh - var(--nav-height));
  width: 100%;
  position: relative;
  /* background: transparent; Let the global background show */
  overflow: hidden;
}

.editor-layout {
  display: flex;
  height: 100%;
  width: 100%;
}

/* Sidebar */
.editor-sidebar {
  width: 320px;
  background: rgba(255, 255, 255, 0.65); /* Glass effect */
  border-right: 1px solid white;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  box-shadow: 5px 0 30px rgba(0,0,0,0.02);
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.app-name {
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 2px;
  color: var(--macaron-pink-deep);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Config Groups */
.config-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.group-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-tertiary);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.sidebar-input {
  width: 100%;
  background: white;
  border: 1px solid transparent;
  border-radius: 16px;
  padding: 12px;
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  transition: all 0.3s;
  box-shadow: 0 4px 10px rgba(0,0,0,0.02);
}

.sidebar-input:focus {
  outline: none;
  border-color: var(--macaron-pink);
  box-shadow: 0 4px 15px rgba(255, 183, 178, 0.2);
  transform: translateY(-1px);
}

.sidebar-input.textarea {
  resize: vertical;
  min-height: 100px;
}

.style-input-row {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid transparent;
  border-radius: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 10px rgba(0,0,0,0.02);
}

.btn-icon:hover {
  background: var(--macaron-mint-light);
  color: #6DB398;
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(181, 234, 215, 0.3);
}

/* Segment Control */
.segment-control {
  display: flex;
  background: rgba(0, 0, 0, 0.03);
  padding: 4px;
  border-radius: 12px;
  gap: 4px;
}

.segment-btn {
  flex: 1;
  padding: 8px;
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.2s;
}

.segment-btn.active {
  background: white;
  color: var(--macaron-pink-deep);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* Ratio Grid */
.ratio-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 0.5rem;
}

.ratio-btn {
  background: white;
  border: 1px solid transparent;
  padding: 10px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}

.ratio-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.05);
}

.ratio-btn.active {
  border-color: var(--macaron-pink);
  background: #FFF5F5;
}

.ratio-box {
  width: 24px;
  height: 24px;
  border: 2px solid var(--text-tertiary);
  border-radius: 4px;
  transition: all 0.2s;
}

.ratio-btn.active .ratio-box {
  border-color: var(--macaron-pink-deep);
  background: rgba(255, 154, 162, 0.1);
}

.ratio-btn span {
  font-size: 10px;
  color: var(--text-secondary);
  font-weight: 700;
}

.ratio-btn.active span {
  color: var(--macaron-pink-deep);
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  background: rgba(255, 255, 255, 0.3);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 1rem;
  justify-content: center;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #8EC5B0;
  border-radius: 50%;
  box-shadow: 0 0 10px #8EC5B0;
}

.status-dot.pulsing {
  background: #FFD93D;
  box-shadow: 0 0 10px #FFD93D;
  animation: pulse 1.5s infinite;
}

.status-text {
  font-size: 11px;
  font-weight: 800;
  color: var(--text-secondary);
  letter-spacing: 1px;
}

.btn-generate {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, var(--macaron-pink-deep), var(--macaron-pink));
  color: white;
  border: none;
  border-radius: 16px;
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 1px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 6px 20px rgba(255, 154, 162, 0.4);
}

.btn-generate:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 10px 30px rgba(255, 154, 162, 0.6);
}

.btn-generate:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
  background: var(--text-tertiary);
}

/* Main Content */
.editor-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: transparent; /* Transparent to show global background */
}

.main-header {
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  /* No border/background to feel open */
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 13px;
  font-weight: 700;
}

.crumb-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: white;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 700;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}

.crumb-btn:hover {
  background: white;
  transform: translateY(-2px);
  color: var(--macaron-pink-deep);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.separator {
  color: var(--text-tertiary);
}

.current {
  color: var(--macaron-pink-deep);
  background: #FFF0F0;
  padding: 4px 12px;
  border-radius: 20px;
}

.action-link {
  background: white;
  border: none;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}

.action-link:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.action-link.danger:hover {
  color: white;
  background: #FF9AA2;
}

/* Script Content */
.script-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 15% 4rem; /* Centralize content */
}

.storyboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.storyboard-header h2 {
  font-size: 28px;
  font-weight: 800;
  margin: 0;
  color: var(--text-primary);
  letter-spacing: -1px;
}

.btn-add-frame {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  border: none;
  color: var(--macaron-pink-deep);
  padding: 10px 20px;
  border-radius: 24px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(255, 154, 162, 0.2);
}

.btn-add-frame:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 154, 162, 0.3);
}

/* Script List */
.script-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.script-row {
  display: flex;
  gap: 1.5rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  border: 2px solid white;
  border-radius: 24px;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
}

.script-row:hover,
.script-row.focused {
  background: white;
  transform: translateY(-4px) scale(1.01);
  box-shadow: 0 15px 40px rgba(0,0,0,0.05);
}

.script-row.focused {
  border-color: var(--macaron-pink);
  box-shadow: 0 15px 40px rgba(255, 154, 162, 0.2);
}

.frame-index {
  font-family: 'Quicksand', sans-serif;
  font-size: 24px;
  font-weight: 800;
  color: var(--macaron-pink-deep);
  opacity: 0.5;
  user-select: none;
  width: 50px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.script-row.focused .frame-index {
  opacity: 1;
  transform: scale(1.2);
}

.frame-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.frame-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.frame-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-tertiary);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.frame-actions {
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s;
  transform: translateX(10px);
}

.script-row:hover .frame-actions {
  opacity: 1;
  transform: translateX(0);
}

.icon-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  border: none;
  background: #f8fafc;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: var(--macaron-mint-light);
  color: #6DB398;
}

.icon-btn.danger:hover {
  background: #FFF0F0;
  color: #FF9AA2;
}

.input-container {
  /* Ensure input has enough space */
}

:deep(.script-input) {
  width: 100%;
  background: transparent !important;
  border: none !important;
  color: var(--text-primary) !important;
  font-size: 16px !important;
  line-height: 1.6 !important;
  padding: 0 !important;
  resize: none !important;
  font-family: inherit;
  font-weight: 600;
}

:deep(.script-input::placeholder) {
  color: var(--text-tertiary);
  font-weight: 500;
}

/* Bottom Spacer */
.bottom-spacer {
  margin-top: 2rem;
  padding-bottom: 4rem;
  cursor: pointer;
}

.add-placeholder {
  height: 80px;
  border: 2px dashed rgba(0, 0, 0, 0.05);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-tertiary);
  font-weight: 700;
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.3);
}

.bottom-spacer:hover .add-placeholder {
  border-color: var(--macaron-pink);
  color: var(--macaron-pink-deep);
  background: white;
  transform: scale(1.02);
  box-shadow: 0 10px 30px rgba(0,0,0,0.03);
}

/* Empty State */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
}

.empty-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: var(--text-secondary);
}

.btn-primary {
  margin-top: 1rem;
  padding: 12px 30px;
  background: linear-gradient(135deg, var(--macaron-pink-deep), var(--macaron-pink));
  color: white;
  border: none;
  border-radius: 30px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(255, 154, 162, 0.4);
  transition: all 0.3s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(255, 154, 162, 0.6);
}

/* Animations */
@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.8; }
  100% { transform: scale(1); opacity: 1; }
}

.error-message {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border: 2px solid #FF9AA2;
  color: var(--text-primary);
  padding: 10px 20px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 100;
  box-shadow: 0 10px 30px rgba(255, 154, 162, 0.3);
  font-weight: 600;
  animation: popDown 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes popDown {
  from { transform: translateX(-50%) translateY(-20px); opacity: 0; }
  to { transform: translateX(-50%) translateY(0); opacity: 1; }
}

.error-icon {
  width: 20px;
  height: 20px;
  background: #FF9AA2;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 12px;
}

.btn-close {
  background: #f1f5f9;
  border: none;
  color: var(--text-secondary);
  font-size: 10px;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 700;
}

.btn-close:hover {
  background: #e2e8f0;
}
</style>