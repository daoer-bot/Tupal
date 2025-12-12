<template>
  <div class="editor-view">
    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="error = ''" class="btn-close">×</button>
    </div>

    <!-- 返回按钮 -->
    <div class="editor-header">
      <button class="btn-back" @click="goBack">
        <ArrowLeft :size="20" />
        <span>返回</span>
      </button>
      <h1 class="editor-title">创作编辑器</h1>
    </div>

    <div v-if="store.currentOutline" class="editor-container">
      <!-- 顶部配置区 -->
      <div class="config-section glass-panel-heavy">
        <!-- 主题输入 -->
        <div class="config-group">
          <label class="config-label">创作主题</label>
          <textarea
            v-model="mainCaption"
            class="theme-input"
            placeholder="描述你的创作主题和想法..."
            rows="5"
          ></textarea>
        </div>

        <!-- 全局风格和图片配置 -->
        <div class="config-row-wrapper">
          <!-- 全局风格 -->
          <div class="config-group flex-1">
            <label class="config-label">全局风格</label>
            <div class="style-tags">
              <input
                v-model="globalStyle"
                class="style-input"
                placeholder="如：极简风格、暖色调、自然光..."
              />
              <div class="style-actions">
                <button @click="applyGlobalStyle('append')" class="action-btn-sm">追加</button>
                <button @click="applyGlobalStyle('replace')" class="action-btn-sm">覆盖</button>
              </div>
            </div>
          </div>

          <!-- 图片配置 -->
          <div class="config-group">
            <label class="config-label">图片配置</label>
            <div class="image-config-inline">
              <div class="config-item">
                <span class="config-item-label">清晰度</span>
                <div class="config-buttons">
                  <button
                    v-for="q in qualityOptions"
                    :key="q.value"
                    @click="selectQuality(q.value)"
                    class="config-btn"
                    :class="{ active: store.imageGenerationConfig.quality === q.value }"
                  >
                    {{ q.label }}
                  </button>
                </div>
              </div>
              <div class="config-item">
                <span class="config-item-label">比例</span>
                <div class="config-buttons">
                  <button
                    v-for="ratio in ratioOptions"
                    :key="ratio.value"
                    @click="selectRatio(ratio.value)"
                    class="config-btn"
                    :class="{ active: store.imageGenerationConfig.aspectRatio === ratio.value }"
                  >
                    {{ ratio.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分镜脚本区 -->
      <div class="script-section">
        <div class="section-header">
          <h2>分镜脚本 <span class="count-badge">{{ store.currentOutline.pages.length }}</span></h2>
          <div class="section-actions">
            <button @click="clearAllPrompts" class="btn-text">清空</button>
            <button @click="addNewPage" class="btn-text-primary">+ 添加</button>
          </div>
        </div>

        <div class="script-grid">
          <div
            v-for="(page, index) in store.currentOutline.pages"
            :key="page.page_number"
            class="script-card"
            :class="{ 'focused': focusedIndex === index }"
          >
            <div class="page-badge">P{{ page.page_number }}</div>
            
            <div class="card-tools">
              <button @click="copyPrompt(index)" class="tool-icon" title="复制">
                <Copy :size="16" />
              </button>
              <button @click="deletePage(index)" class="tool-icon" title="删除">
                <X :size="16" />
              </button>
            </div>

            <MentionInput
              v-model="page.description"
              placeholder="描述画面细节...（输入 @ 可引用素材）"
              :multiline="true"
              :rows="12"
              input-class="script-textarea"
              @focus="focusedIndex = index"
              @blur="focusedIndex = null"
            />
          </div>
        </div>
      </div>

      <!-- 底部操作栏 -->
      <div class="bottom-action-bar">
        <button
          class="btn-generate"
          @click="handleGenerate"
          :disabled="isGenerating"
        >
          <span v-if="isGenerating" class="loading-dot"></span>
          <Sparkles v-else :size="20" />
          <span v-if="isGenerating">生成中...</span>
          <span v-else>一键生成小红书图文</span>
        </button>
      </div>
    </div>

    <!-- 无大纲提示 -->
    <div v-if="!store.currentOutline" class="empty-state">
      <div class="empty-icon">
        <FileText :size="48" />
      </div>
      <h3>还没有创作内容</h3>
      <p>请先在创作主页输入主题或选择模板开始创作</p>
      <button @click="goToCreationHome" class="btn-primary">
        <Sparkles :size="18" />
        <span>前往创作</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Copy, X, Sparkles, FileText } from 'lucide-vue-next'
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
  { label: '1K', value: '1k' as const },
  { label: '2K', value: '2k' as const },
  { label: '4K', value: '4k' as const }
]

const ratioOptions = [
  { label: '4:3', value: '4:3' as const },
  { label: '3:4', value: '3:4' as const },
  { label: '16:9', value: '16:9' as const },
  { label: '9:16', value: '9:16' as const },
  { label: '2:3', value: '2:3' as const },
  { label: '3:2', value: '3:2' as const },
  { label: '1:1', value: '1:1' as const },
  { label: '4:5', value: '4:5' as const },
  { label: '5:4', value: '5:4' as const },
  { label: '21:9', value: '21:9' as const }
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
    error.value = '至少需要保留一个分镜'
    return
  }
  
  if (confirm('确定要删除这个分镜吗？')) {
    store.currentOutline.pages.splice(index, 1)
    store.currentOutline.pages.forEach((p, i) => {
      p.page_number = i + 1
    })
  }
}

const clearAllPrompts = () => {
  if (!store.currentOutline) return
  if (confirm('确定要清空所有提示词吗？')) {
    store.currentOutline.pages.forEach(p => p.description = '')
  }
}

const addNewPage = () => {
  if (!store.currentOutline) return
  const newPageNum = store.currentOutline.pages.length + 1
  store.currentOutline.pages.push({
    page_number: newPageNum,
    title: `页面 ${newPageNum}`,
    description: '',
    xiaohongshu_content: mainCaption.value
  })
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
    error.value = '请确保所有分镜都有提示词'
    return
  }
  
  if (!mainCaption.value || !mainCaption.value.trim()) {
    error.value = '请输入小红书文案'
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
    error.value = err.message || '处理素材引用失败'
    isGenerating.value = false
  }
}

onMounted(() => {
  // 接收热点话题参数
  const topic = route.query.topic as string
  if (topic && store.currentOutline) {
    // 自动填充到主题输入框
    store.currentOutline.pages.forEach(p => {
      p.xiaohongshu_content = topic
    })
    // 清除 query 参数
    router.replace({ query: {} })
  }
  
  if (!store.currentOutline) {
    console.warn('No outline available')
  }
})
</script>

<style scoped>
.editor-view {
  max-width: 1600px;
  margin: 0 auto;
  padding: 1rem 0;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.editor-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 8px;
  color: #64748b;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.9);
  color: #6366f1;
  border-color: rgba(99, 102, 241, 0.4);
}

.editor-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.error-message {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: #fee;
  color: #ff2442;
  padding: 10px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #ffcdd2;
}

.btn-close {
  background: none;
  border: none;
  color: #ff2442;
  font-size: 18px;
  cursor: pointer;
}

.editor-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding-bottom: 100px;
}

.config-section {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.glass-panel-heavy {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
  border-radius: 24px;
}

.config-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.config-group.flex-1 {
  flex: 1;
}

.config-label {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.theme-input {
  width: 100%;
  min-height: 128px;
  padding: 1rem;
  border: 2px solid rgba(99, 102, 241, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.6);
  font-size: 15px;
  line-height: 1.6;
  color: #1e293b;
  resize: vertical;
  font-family: inherit;
  transition: all 0.3s;
}

.theme-input:focus {
  outline: none;
  border-color: #6366f1;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

.config-row-wrapper {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

.style-tags {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.style-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  color: #1e293b;
  transition: all 0.2s;
}

.style-input:focus {
  outline: none;
  border-color: #6366f1;
  background: rgba(255, 255, 255, 0.9);
}

.style-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn-sm {
  flex: 1;
  padding: 0.5rem 1rem;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: #6366f1;
  font-size: 13px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn-sm:hover {
  background: #6366f1;
  color: white;
  transform: translateY(-1px);
}

.image-config-inline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.config-item-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  min-width: 60px;
}

.config-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.config-btn {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.6);
  border: 1.5px solid #e0e0e0;
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.config-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
  transform: translateY(-1px);
}

.config-btn.active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.script-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 2px solid rgba(99, 102, 241, 0.2);
}

.section-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.count-badge {
  font-size: 14px;
  color: #94a3b8;
  font-weight: 400;
}

.section-actions {
  display: flex;
  gap: 1rem;
}

.btn-text {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s;
}

.btn-text:hover {
  color: #1e293b;
}

.btn-text-primary {
  background: none;
  border: none;
  color: #6366f1;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s;
}

.btn-text-primary:hover {
  color: #8b5cf6;
}

.script-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.5rem;
}

.script-card {
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
  position: relative;
  min-height: 320px;
}

.script-card:hover {
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
  transform: translateY(-4px);
}

.script-card.focused {
  border-color: rgba(99, 102, 241, 0.5);
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
}

.page-badge {
  position: absolute;
  top: -12px;
  left: 1rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.card-tools {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.script-card:hover .card-tools {
  opacity: 1;
}

.tool-icon {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(99, 102, 241, 0.2);
  color: #64748b;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.tool-icon:hover {
  background: #6366f1;
  color: white;
  border-color: transparent;
}

.script-textarea {
  width: 100%;
  min-height: 280px;
  border: none;
  resize: none;
  font-size: 15px;
  line-height: 1.6;
  color: #1e293b;
  font-family: inherit;
  background: transparent;
  padding: 0;
}

.script-textarea:focus {
  outline: none;
}

.bottom-action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(99, 102, 241, 0.2);
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: center;
  z-index: 100;
}

.btn-generate {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 3rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
}

.btn-generate:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
}

.btn-generate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: white;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 4rem 2rem;
  min-height: 400px;
}

.empty-icon {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
  border-radius: 24px;
  margin-bottom: 1.5rem;
  color: #6366f1;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
}

.empty-state p {
  margin: 0 0 2rem 0;
  font-size: 1rem;
  color: #64748b;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
}

@media (max-width: 1024px) {
  .config-row-wrapper {
    flex-direction: column;
  }
  
  .script-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 640px) {
  .editor-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .script-grid {
    grid-template-columns: 1fr;
  }
  
  .btn-generate {
    width: 100%;
    justify-content: center;
  }
}
</style>