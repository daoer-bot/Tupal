<template>
  <div class="creation-home">
    <div class="main-content animate-fade-in">

      <!-- 🍭 标题区 -->
      <div class="greeting-section">
        <h1 class="greeting-title">
          <span class="highlight-pink">Create</span>
          <span class="highlight-mint">Something</span>
          <br>
          <span class="highlight-purple">Sweet Today</span>
        </h1>
        <p class="greeting-subtitle">✨ AI Creative Studio · 你的灵感甜品站 ✨</p>
      </div>

      <!-- 🍬 棉花糖输入框 -->
      <div class="input-section">
        <div class="macaron-input-box glass-panel" :class="{ focused: inputFocused }">
          <!-- 输入区域 -->
          <div class="input-area">
            <MentionInput
              v-model="topic"
              placeholder="我想做一个关于...的甜美创意 🧁"
              :multiline="true"
              :rows="1"
              input-class="transparent-input"
              @focus="inputFocused = true"
              @blur="inputFocused = false"
              @keydown="handleKeydown"
            />
          </div>

          <!-- 发送按钮 -->
          <div class="input-actions-right">
            <button
              class="btn-primary send-btn"
              :disabled="!canCreate || isCreating"
              @click="startCreation"
            >
              <span v-if="isCreating" class="loading-spinner"></span>
              <ArrowUp v-else :size="24" stroke-width="3" />
            </button>
          </div>
        </div>

        <!-- 已选配置标签 (Chip) - 仅展示，不可直接关闭，引导下方修改 -->
        <div v-if="selectedTemplate || hasCustomImageConfig" class="selected-configs animate-pop-up">
          <div v-if="selectedTemplate" class="config-chip pink-chip">
            <span class="chip-icon">📄</span>
            <span class="chip-text">{{ selectedTemplate.name }}</span>
            <button class="chip-close" @click="clearTemplate"><X :size="12" /></button>
          </div>
          <div v-if="hasCustomImageConfig" class="config-chip mint-chip">
            <span class="chip-icon">🖼️</span>
            <span class="chip-text">{{ imageConfig.quality.toUpperCase() }} · {{ imageConfig.aspectRatio }}</span>
          </div>
        </div>
      </div>

      <!-- 🍰 底部配置面板 (直接展示) -->
      <div class="bottom-panel glass-panel">
        <div class="panel-tabs">
          <button
            class="panel-tab"
            :class="{ active: activeTab === 'templates' }"
            @click="activeTab = 'templates'"
          >
            🔥 热门模版
          </button>
          <button
            class="panel-tab"
            :class="{ active: activeTab === 'myTemplates' }"
            @click="activeTab = 'myTemplates'"
          >
            💖 我的收藏
          </button>
          <button
            class="panel-tab"
            :class="{ active: activeTab === 'settings' }"
            @click="activeTab = 'settings'"
          >
            🎨 画质与比例
          </button>
        </div>

        <div class="panel-content-area">
          <!-- 热门模版列表 -->
          <div v-if="activeTab === 'templates'" class="templates-view">
            <div v-if="loadingTemplates" class="loading-state">
              <div class="loading-spinner-pink"></div>
            </div>
            <div v-else-if="officialTemplates.length === 0" class="empty-state">
              <div class="empty-icon">📑</div>
              <p class="empty-text">暂无热门模版</p>
            </div>
            <div v-else class="templates-grid">
              <div
                v-for="tpl in officialTemplates"
                :key="tpl.id"
                class="template-card"
                :class="{ selected: selectedTemplate?.id === tpl.id }"
                @click="selectTemplate(tpl)"
              >
                <div class="tpl-preview">
                   <div class="tpl-icon">📑</div>
                </div>
                <div class="tpl-info">
                  <span class="tpl-name">{{ tpl.name }}</span>
                  <span class="tpl-desc">{{ tpl.description || '暂无描述' }}</span>
                </div>
                <div class="tpl-select-indicator" v-if="selectedTemplate?.id === tpl.id">
                  <Check :size="14" />
                </div>
              </div>
            </div>
          </div>

          <!-- 我的收藏模版列表 -->
          <div v-if="activeTab === 'myTemplates'" class="templates-view">
            <div v-if="loadingMyTemplates" class="loading-state">
              <div class="loading-spinner-pink"></div>
            </div>
            <div v-else-if="myTemplates.length === 0" class="empty-state">
              <div class="empty-icon">💖</div>
              <p class="empty-text">还没有收藏的模版</p>
              <p class="empty-hint">在工作台的案例库中，可以将喜欢的案例设为模版哦~</p>
            </div>
            <div v-else class="templates-grid">
              <div
                v-for="tpl in myTemplates"
                :key="tpl.id"
                class="template-card user-template"
                :class="{ selected: selectedTemplate?.id === tpl.id }"
                @click="selectTemplate(tpl)"
              >
                <div class="tpl-preview">
                  <img v-if="tpl.preview_image" :src="tpl.preview_image" alt="预览" class="tpl-preview-img" />
                  <div v-else class="tpl-icon">💖</div>
                </div>
                <div class="tpl-info">
                  <span class="tpl-name">{{ tpl.name }}</span>
                  <span class="tpl-desc">{{ tpl.description || '我的收藏模版' }}</span>
                </div>
                <div class="tpl-badge">收藏</div>
                <div class="tpl-select-indicator" v-if="selectedTemplate?.id === tpl.id">
                  <Check :size="14" />
                </div>
              </div>
            </div>
          </div>

          <!-- 画质设置 -->
          <div v-if="activeTab === 'settings'" class="settings-view">
            <div class="setting-group">
              <label>画质 Quality</label>
              <div class="options-row">
                <button
                  v-for="q in qualityOptions"
                  :key="q.value"
                  class="option-btn"
                  :class="{ active: imageConfig.quality === q.value }"
                  @click="selectQuality(q.value)"
                >
                  {{ q.label }}
                </button>
              </div>
            </div>

            <div class="setting-group">
              <label>比例 Aspect Ratio</label>
              <div class="options-row">
                <button
                  v-for="ratio in ratioOptions"
                  :key="ratio.value"
                  class="option-btn"
                  :class="{ active: imageConfig.aspectRatio === ratio.value }"
                  @click="selectRatio(ratio.value)"
                >
                  {{ ratio.label }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷提示 -->
      <div class="quick-suggestions">
        <button
          v-for="tip in quickTips"
          :key="tip"
          class="suggestion-bubble"
          @click="topic = tip"
        >
          ✨ {{ tip }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowUp, X, Check } from 'lucide-vue-next'
import { useAppStore } from '../../store'
import MentionInput from '../../components/MentionInput.vue'
import templateApi, { type Template } from '../../services/templateApi'
import { generateOutline } from '../../services/api'

const router = useRouter()
const store = useAppStore()

// 状态
const topic = ref('')
const isCreating = ref(false)
const inputFocused = ref(false)
const activeTab = ref<'templates' | 'myTemplates' | 'settings'>('templates')

// 快捷提示
const quickTips = [
  '今日OOTD穿搭',
  '周末探店指南',
  '梦幻旅行计划',
  '治愈系好物'
]

// 图片配置
const imageConfig = ref({
  quality: store.imageGenerationConfig.quality,
  aspectRatio: store.imageGenerationConfig.aspectRatio
})

// 模板状态
const selectedTemplate = ref<Template | null>(null)
const loadingTemplates = ref(false)
const loadingMyTemplates = ref(false)
const officialTemplates = ref<Template[]>([])
const myTemplates = ref<Template[]>([])

// 选项数据
const qualityOptions = [
  { label: '标准 1K', value: '1k' as const },
  { label: '高清 2K', value: '2k' as const },
  { label: '超清 4K', value: '4k' as const }
]

const ratioOptions = [
  { label: '3:4', value: '3:4' as const },
  { label: '4:3', value: '4:3' as const },
  { label: '1:1', value: '1:1' as const },
  { label: '9:16', value: '9:16' as const },
  { label: '16:9', value: '16:9' as const }
]

const hasCustomImageConfig = computed(() => {
  return imageConfig.value.quality !== '2k' || imageConfig.value.aspectRatio !== '3:4'
})

const canCreate = computed(() => {
  return topic.value.trim().length > 0
})

const selectTemplate = (template: Template) => {
  if (selectedTemplate.value?.id === template.id) {
    selectedTemplate.value = null // toggle off
  } else {
    selectedTemplate.value = template
  }
}

const clearTemplate = () => {
  selectedTemplate.value = null
}

const selectQuality = (quality: '1k' | '2k' | '4k') => {
  imageConfig.value.quality = quality
  store.setImageGenerationConfig({
    ...store.imageGenerationConfig,
    quality
  })
}

const selectRatio = (aspectRatio: '4:3' | '3:4' | '16:9' | '9:16' | '2:3' | '3:2' | '1:1' | '4:5' | '5:4' | '21:9') => {
  imageConfig.value.aspectRatio = aspectRatio
  store.setImageGenerationConfig({
    ...store.imageGenerationConfig,
    aspectRatio
  })
}

const handleKeydown = (event: KeyboardEvent) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault()
    if (canCreate.value && !isCreating.value) {
      startCreation()
    }
  }
}

const startCreation = async () => {
  if (!canCreate.value || isCreating.value) return

  isCreating.value = true

  try {
    // 如果选择了模板，使用模板创建
    if (selectedTemplate.value) {
      const response = await templateApi.useTemplate(selectedTemplate.value.id, topic.value)
      
      if (response.success && response.data) {
        // 将模板生成的大纲设置到store
        store.setOutline({
          task_id: response.data.task_id,
          topic: response.data.topic,
          pages: response.data.pages
        })
        router.push('/creation/editor')
      }
    } else {
      // 没有选择模板，使用普通方式创建
      const response = await generateOutline({
        topic: topic.value,
        generator_type: store.textModelConfig.generatorType,
        text_model_config: store.textModelConfig
      })

      if (response.success && response.data) {
        store.setOutline(response.data)
        router.push('/creation/editor')
      }
    }
  } catch (error) {
    console.error('创建失败:', error)
  } finally {
    isCreating.value = false
  }
}

const loadTemplates = async () => {
  loadingTemplates.value = true
  try {
    const res = await templateApi.getOfficialTemplates({ page_size: 20 })
    if (res.success && res.data) {
      officialTemplates.value = res.data.items
    }
  } catch (error) {
    console.error('加载模板失败:', error)
    // Mock data fallback
    officialTemplates.value = [
      { id: 'tpl-1', name: '穿搭分享', description: '适合展示OOTD', type: 'system', tags: ['穿搭'], created_at: new Date().toISOString() },
      { id: 'tpl-2', name: '美食探店', description: '记录味蕾之旅', type: 'system', tags: ['美食'], created_at: new Date().toISOString() },
      { id: 'tpl-3', name: '旅行Vlog', description: '风景与故事', type: 'system', tags: ['旅行'], created_at: new Date().toISOString() },
      { id: 'tpl-4', name: '好物种草', description: '分享生活好物', type: 'system', tags: ['好物'], created_at: new Date().toISOString() },
    ]
  } finally {
    loadingTemplates.value = false
  }
}

const loadMyTemplates = async () => {
  loadingMyTemplates.value = true
  try {
    const res = await templateApi.getPersonalTemplates({ page_size: 50 })
    if (res.success && res.data) {
      myTemplates.value = res.data.items
    }
  } catch (error) {
    console.error('加载我的模板失败:', error)
    // 如果API失败，显示空列表
    myTemplates.value = []
  } finally {
    loadingMyTemplates.value = false
  }
}

// 当切换到"我的收藏"标签时加载数据
watch(activeTab, (newTab) => {
  if (newTab === 'myTemplates' && myTemplates.value.length === 0 && !loadingMyTemplates.value) {
    loadMyTemplates()
  }
})

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.creation-home {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  padding: 2rem;
  box-sizing: border-box;
}

.main-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 800px;
  z-index: 10;
}

/* --- 🍭 标题样式 --- */
.greeting-section {
  text-align: center;
  margin-bottom: 2rem;
}

.greeting-title {
  font-family: 'Quicksand', sans-serif;
  margin: 0;
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 0.5rem;
  text-align: center;
  letter-spacing: -1px;
}

.highlight-pink { color: var(--macaron-pink-deep); }
.highlight-mint { color: #8EC5B0; }
.highlight-purple {
  background: linear-gradient(135deg, #C7CEEA 0%, #FF9AA2 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.greeting-subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
  font-weight: 600;
  margin-top: 0.5rem;
  letter-spacing: 1px;
  opacity: 0.8;
}

/* --- 🍬 输入框样式 --- */
.input-section {
  width: 100%;
  position: relative;
  z-index: 20;
  margin-bottom: 1.5rem;
}

.macaron-input-box {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem 1rem;
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.9);
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 10px 30px rgba(0,0,0,0.03);
}

.macaron-input-box.focused {
  transform: scale(1.01);
  background: #fff;
  box-shadow:
    0 20px 50px -10px rgba(255, 154, 162, 0.2),
    inset 0 0 0 2px var(--macaron-pink);
}

/* 输入区域 */
.input-area {
  flex: 1;
  min-width: 0;
}

:deep(.transparent-input) {
  width: 100%;
  padding: 0.5rem 1rem !important;
  border: none !important;
  background: transparent !important;
  font-size: 1.1rem !important;
  color: var(--text-primary) !important;
  font-family: 'Quicksand', sans-serif;
  font-weight: 600;
}

:deep(.transparent-input::placeholder) {
  color: var(--text-tertiary);
  font-weight: 500;
}

/* 发送按钮 */
.send-btn {
  width: 48px;
  height: 48px;
  border-radius: 20px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--macaron-pink);
  border: none;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: var(--macaron-pink-deep);
  transform: scale(1.05);
}

/* --- 🏷️ 已选标签 --- */
.selected-configs {
  display: flex;
  gap: 0.8rem;
  margin-top: 1rem;
  padding-left: 1rem;
}

.config-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 4px 10px rgba(0,0,0,0.03);
  transition: all 0.2s;
}

.pink-chip {
  background: #FFF0F0;
  color: var(--macaron-pink-deep);
  border: 1px solid #FFD0D0;
}

.mint-chip {
  background: #F0FFF9;
  color: #6DB398;
  border: 1px solid #D0F0E0;
}

.chip-close {
  background: transparent;
  border: none;
  color: currentColor;
  opacity: 0.6;
  cursor: pointer;
  padding: 2px;
  display: flex;
  border-radius: 50%;
}

.chip-close:hover { opacity: 1; background: rgba(0,0,0,0.05); }

/* --- 🍰 底部配置面板 --- */
.bottom-panel {
  width: 100%;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.5);
  display: flex;
  flex-direction: column;
}

.panel-tabs {
  display: flex;
  padding: 8px 8px 0;
  gap: 8px;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.panel-tab {
  padding: 10px 20px;
  border: none;
  background: transparent;
  border-radius: 12px 12px 0 0;
  color: var(--text-tertiary);
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.panel-tab:hover {
  color: var(--text-primary);
  background: rgba(255,255,255,0.4);
}

.panel-tab.active {
  background: white;
  color: var(--macaron-pink-deep);
  box-shadow: 0 -4px 10px rgba(0,0,0,0.02);
}

.panel-content-area {
  padding: 20px;
  background: white;
  min-height: 200px;
}

/* 模版网格 */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.template-card {
  border: 1px solid #f0f0f0;
  border-radius: 16px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  background: #fff;
}

.template-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.05);
  border-color: var(--macaron-pink);
}

.template-card.selected {
  border-color: var(--macaron-pink-deep);
  background: #FFF5F5;
  box-shadow: 0 0 0 2px var(--macaron-pink-deep);
}

/* 用户模板特殊样式 */
.template-card.user-template {
  border-color: #FFE0E8;
  background: linear-gradient(135deg, #FFF5F8 0%, #FFFFFF 100%);
}

.template-card.user-template:hover {
  border-color: var(--macaron-pink);
  box-shadow: 0 8px 20px rgba(255, 154, 162, 0.15);
}

.tpl-preview {
  height: 80px;
  background: #f8fafc;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  overflow: hidden;
}

.tpl-preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.tpl-icon {
  font-size: 2rem;
}

.tpl-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tpl-name {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--text-primary);
}

.tpl-desc {
  font-size: 0.8rem;
  color: var(--text-tertiary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tpl-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background: linear-gradient(135deg, #FF9AA2 0%, #FFB7B2 100%);
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 10px;
}

.tpl-select-indicator {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 20px;
  height: 20px;
  background: var(--macaron-pink-deep);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-text {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 0.85rem;
  color: var(--text-tertiary);
  margin: 0;
  max-width: 280px;
}

/* 设置面板 */
.settings-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.setting-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.options-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.option-btn {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  background: white;
  color: var(--text-secondary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.option-btn:hover {
  border-color: var(--macaron-mint);
  color: #6DB398;
}

.option-btn.active {
  background: var(--macaron-mint);
  color: white;
  border-color: var(--macaron-mint);
  box-shadow: 0 4px 10px rgba(109, 179, 152, 0.3);
}

/* --- ✨ 快捷提示气泡 --- */
.quick-suggestions {
  display: flex;
  gap: 0.8rem;
  margin-top: 2rem;
  justify-content: center;
  flex-wrap: wrap;
}

.suggestion-bubble {
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid white;
  padding: 0.6rem 1.2rem;
  border-radius: 24px;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 10px rgba(0,0,0,0.02);
}

.suggestion-bubble:hover {
  transform: translateY(-2px);
  background: white;
  color: var(--macaron-pink-deep);
}

/* Loading */
.loading-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.loading-spinner-pink {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 154, 162, 0.2);
  border-top-color: var(--macaron-pink);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* 响应式 */
@media (max-width: 640px) {
  .greeting-title { font-size: 2.5rem; }
  .templates-grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }
  .panel-tabs { flex-wrap: wrap; }
  .panel-tab { font-size: 0.85rem; padding: 8px 14px; }
}
</style>