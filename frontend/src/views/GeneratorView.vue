<template>
  <div class="generator-view">
    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="error = ''" class="btn-close">×</button>
    </div>

    <div v-if="store.currentOutline" class="script-layout">
      
      <!-- 左侧：文案与全局设置 -->
      <div class="sidebar-section">
        <div class="sidebar-sticky">
          <!-- 1. 小红书文案 (极简版) -->
          <div class="minimal-panel caption-panel">
            <div class="panel-header-minimal">
              <span class="panel-title">笔记文案</span>
              <div class="header-tools">
                <div class="template-dropdown">
                  <button class="tool-btn">模板 ▼</button>
                  <div class="dropdown-menu">
                    <div 
                      v-for="(tpl, idx) in captionTemplates" 
                      :key="idx"
                      class="dropdown-item"
                      @click="applyTemplate(tpl.content)"
                    >
                      {{ tpl.name }}
                    </div>
                  </div>
                </div>
                <span class="counter" :class="{ 'text-error': captionLength > 1000 }">
                  {{ captionLength }}/1000
                </span>
              </div>
            </div>
            
            <div class="textarea-wrapper-minimal">
              <textarea
                v-model="mainCaption"
                class="main-textarea-minimal"
                placeholder="输入笔记正文..."
              ></textarea>
              <div class="emoji-trigger-minimal" title="插入 Emoji">😊</div>
            </div>
          </div>

          <!-- 2. 全局风格 (折叠式) -->
          <div class="minimal-panel global-panel">
            <div class="panel-header-minimal clickable" @click="showGlobalStyle = !showGlobalStyle">
              <span class="panel-title">全局风格设定</span>
              <span class="toggle-icon">{{ showGlobalStyle ? '−' : '+' }}</span>
            </div>
            <div v-show="showGlobalStyle" class="panel-body-minimal">
              <textarea
                v-model="globalStyle"
                class="style-textarea-minimal"
                placeholder="输入全局风格提示词..."
                rows="2"
              ></textarea>
              <div class="global-actions-minimal">
                <button @click="applyGlobalStyle('append')" class="btn-text-sm">追加</button>
                <span class="divider">|</span>
                <button @click="applyGlobalStyle('replace')" class="btn-text-sm">覆盖</button>
              </div>
            </div>
          </div>

          <!-- 3. 图片配置 (折叠式) -->
          <div class="minimal-panel config-panel">
            <div class="panel-header-minimal clickable" @click="showImageConfig = !showImageConfig">
              <span class="panel-title">图片配置</span>
              <span class="toggle-icon">{{ showImageConfig ? '−' : '+' }}</span>
            </div>
            <div v-show="showImageConfig" class="panel-body-minimal">
              <!-- 清晰度选择 -->
              <div class="config-group">
                <label class="config-label">清晰度</label>
                <div class="config-options">
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
              
              <!-- 图片比例选择 -->
              <div class="config-group">
                <label class="config-label">图片比例</label>
                <div class="config-options ratio-grid">
                  <button
                    v-for="ratio in ratioOptions"
                    :key="ratio.value"
                    @click="selectRatio(ratio.value)"
                    class="config-btn ratio-btn"
                    :class="{ active: store.imageGenerationConfig.aspectRatio === ratio.value }"
                  >
                    {{ ratio.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 4. 生成按钮 -->
          <div class="generate-action">
            <button
              class="btn-generate"
              @click="handleGenerate"
              :disabled="isGenerating"
            >
              <span v-if="isGenerating" class="loading-dot"></span>
              <span v-if="isGenerating">生成中...</span>
              <span v-else>一键生成小红书图文</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 右侧：分镜脚本网格 -->
      <div class="grid-section">
        <div class="section-header-minimal">
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
            class="script-card-minimal"
            :class="{ 'focused': focusedIndex === index }"
          >
            <div class="page-badge-corner">P{{ page.page_number }}</div>
            
            <div class="card-content-wrapper">
              <div class="card-tools">
                <button @click="copyPrompt(index)" class="tool-icon" title="复制">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 01-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 011.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 00-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 01-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 00-3.375-3.375h-1.5" />
                  </svg>
                </button>
                <button @click="deletePage(index)" class="tool-icon" title="删除">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <textarea
                v-model="page.description"
                class="script-textarea-minimal"
                placeholder="描述画面细节..."
                @focus="focusedIndex = index"
                @blur="focusedIndex = null"
              ></textarea>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无大纲提示 -->
    <div v-if="!store.currentOutline" class="empty-state">
      <p>请先在首页生成内容大纲</p>
      <button @click="goHome" class="btn btn-primary">前往首页</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../store'

const router = useRouter()
const store = useAppStore()

// 状态
const focusedIndex = ref<number | null>(null)
const error = ref('')
const isGenerating = ref(false)
const globalStyle = ref('')
const showGlobalStyle = ref(true)
const showImageConfig = ref(false)

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

// 快捷标签
const quickTags = ['#特写', '#全景', '#对角线构图', '#自然光', '#极简背景']

// 文案模板
const captionTemplates = [
  { name: '种草', content: '宝子们！今天发现了一个超级好用的神器✨\n\n[产品名称] 真的绝绝子！\n亲测好用，强烈推荐给大家💖\n\n#好物推荐 #种草 #神器' },
  { name: '探店', content: '📍坐标：[地点]\n\n终于来打卡这家网红店啦！📸\n环境超级出片，味道也很赞😋\n\n建议集美们周末冲！\n\n#探店 #周末去哪儿 #美食' },
  { name: '干货', content: '纯干货分享！建议收藏🌟\n\n关于[主题]的几个关键点：\n1️⃣ 第一点\n2️⃣ 第二点\n3️⃣ 第三点\n\n学会了吗？评论区告诉我👇\n\n#干货 #知识分享 #学习' }
]

// 计算属性
const mainCaption = computed({
  get: () => {
    return store.currentOutline?.pages[0]?.xiaohongshu_content || ''
  },
  set: (val: string) => {
    if (!store.currentOutline) return
    // 同步更新所有页面的文案字段
    store.currentOutline.pages.forEach(p => {
      p.xiaohongshu_content = val
    })
  }
})

const captionLength = computed(() => mainCaption.value.length)

// 方法
const applyTemplate = (content: string) => {
  mainCaption.value = content
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

const appendTagToPage = (index: number, tag: string) => {
  if (!store.currentOutline) return
  const page = store.currentOutline.pages[index]
  page.description = page.description ? `${page.description} ${tag}` : tag
}

const copyPrompt = (index: number) => {
  if (!store.currentOutline) return
  const text = store.currentOutline.pages[index].description
  navigator.clipboard.writeText(text).then(() => {
    // 可以加个 toast 提示
  })
}

const clearPrompt = (index: number) => {
  if (!store.currentOutline) return
  store.currentOutline.pages[index].description = ''
}

const deletePage = (index: number) => {
  if (!store.currentOutline) return
  if (store.currentOutline.pages.length <= 1) {
    error.value = '至少需要保留一个分镜'
    return
  }
  
  if (confirm('确定要删除这个分镜吗？')) {
    store.currentOutline.pages.splice(index, 1)
    // 重新编号
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
    xiaohongshu_content: mainCaption.value // 继承当前文案
  })
}

// 图片配置方法
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

const handleGenerate = () => {
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
  
  setTimeout(() => {
    isGenerating.value = false
    router.push('/result')
  }, 800)
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  if (!store.currentOutline) {
    console.warn('No outline available')
  }
})
</script>

<style scoped>
.generator-view {
  max-width: 1600px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #f8fafc;
}

/* 错误提示 */
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

/* 布局 */
.script-layout {
  display: flex;
  gap: 40px;
  margin-top: 2rem;
  align-items: flex-start;
}

/* 左侧边栏 */
.sidebar-section {
  width: 400px;
  flex-shrink: 0;
}

.sidebar-sticky {
  position: sticky;
  top: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 极简面板 */
.minimal-panel {
  background: transparent;
}

.panel-header-minimal {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.panel-header-minimal.clickable {
  cursor: pointer;
  user-select: none;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.header-tools {
  display: flex;
  align-items: center;
  gap: 12px;
}

.counter {
  font-size: 12px;
  color: #999;
  font-family: monospace;
}

.text-error { color: #ff2442; }

/* 下拉菜单 */
.template-dropdown {
  position: relative;
}

.tool-btn {
  background: none;
  border: none;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.tool-btn:hover { background: #eee; }

.dropdown-menu {
  display: none;
  position: absolute;
  top: 100%;
  right: 0;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 10;
  min-width: 120px;
  padding: 4px 0;
}

.template-dropdown:hover .dropdown-menu {
  display: block;
}

.dropdown-item {
  padding: 8px 12px;
  font-size: 12px;
  color: #333;
  cursor: pointer;
}

.dropdown-item:hover {
  background: #f5f5f5;
  color: #ff2442;
}

/* 极简输入框 */
.textarea-wrapper-minimal {
  position: relative;
}

.main-textarea-minimal {
  width: 100%;
  min-height: 500px; /* 大幅增加高度 */
  padding: 0;
  border: none;
  background: transparent;
  font-size: 15px;
  line-height: 1.8;
  color: #333;
  resize: none;
  font-family: inherit;
}

.main-textarea-minimal:focus {
  outline: none;
}

.emoji-trigger-minimal {
  position: absolute;
  bottom: 0;
  right: 0;
  cursor: pointer;
  font-size: 18px;
  opacity: 0.4;
  transition: opacity 0.2s;
}

.emoji-trigger-minimal:hover { opacity: 1; }

/* 全局风格 */
.toggle-icon {
  font-size: 16px;
  color: #999;
}

.style-textarea-minimal {
  width: 100%;
  padding: 8px 0;
  border: none;
  border-bottom: 1px solid #eee;
  background: transparent;
  font-size: 14px;
  color: #333;
  resize: none;
  margin-bottom: 8px;
}

.style-textarea-minimal:focus {
  outline: none;
  border-bottom-color: #ff2442;
}

.global-actions-minimal {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-text-sm {
  background: none;
  border: none;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  padding: 0;
}

.btn-text-sm:hover { color: #ff2442; }

.divider { color: #eee; font-size: 10px; }

/* 图片配置 */
.config-panel {
  margin-top: 16px;
}

.config-group {
  margin-bottom: 16px;
}

.config-group:last-child {
  margin-bottom: 0;
}

.config-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
  font-weight: 500;
}

.config-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.ratio-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
}

.config-btn {
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  color: #666;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.config-btn:hover {
  background: #eee;
  border-color: #ccc;
}

.config-btn.active {
  background: #ff2442;
  border-color: #ff2442;
  color: white;
  font-weight: 500;
}

.ratio-btn {
  padding: 6px 8px;
  font-size: 11px;
}

/* 生成按钮 */
.btn-generate {
  width: 100%;
  background: #ff2442;
  color: white;
  font-size: 16px;
  font-weight: 600;
  padding: 16px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(255, 36, 66, 0.2);
}

.btn-generate:hover:not(:disabled) {
  background: #ff4d6a;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(255, 36, 66, 0.3);
}

.btn-generate:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 右侧网格区 */
.grid-section {
  flex: 1;
}

.section-header-minimal {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.section-header-minimal h2 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.count-badge {
  font-size: 12px;
  color: #999;
  font-weight: normal;
}

.section-actions {
  display: flex;
  gap: 16px;
}

.btn-text {
  background: none;
  border: none;
  color: #999;
  font-size: 13px;
  cursor: pointer;
}

.btn-text:hover { color: #333; }

.btn-text-primary {
  background: none;
  border: none;
  color: #ff2442;
  font-size: 13px;
  cursor: pointer;
  font-weight: 500;
}

/* 分镜网格 */
.script-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.script-card-minimal {
  background: #fff;
  border-radius: 8px;
  /* 去除边框，使用极淡的阴影 */
  box-shadow: 0 2px 12px rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
  transition: all 0.2s;
  position: relative;
  padding: 20px;
  margin-top: 16px; /* 为顶部标签留出空间 */
}

.script-card-minimal:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
  transform: translateY(-2px);
}

.script-card-minimal.focused {
  box-shadow: 0 8px 24px rgba(255, 36, 66, 0.08);
}

/* 左上角标签样式 - 位于卡片框外部上方 */
.page-badge-corner {
  position: absolute;
  top: -16px;
  left: 12px;
  background: #ff2442;
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px 4px 0 0;
  box-shadow: 0 2px 6px rgba(255, 36, 66, 0.25);
  z-index: 5;
  pointer-events: none;
  transition: all 0.2s;
}

.script-card-minimal:hover .page-badge-corner {
  box-shadow: 0 3px 8px rgba(255, 36, 66, 0.35);
}

.card-content-wrapper {
  position: relative;
  flex: 1;
}

.card-tools {
  position: absolute;
  top: -12px;
  right: -4px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 5;
}

.script-card-minimal:hover .card-tools {
  opacity: 1;
}

.tool-icon {
  background: #fff;
  border: 1px solid #eee;
  color: #999;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tool-icon:hover {
  color: #333;
  border-color: #ccc;
}

.w-4 { width: 14px; }
.h-4 { height: 14px; }

.script-textarea-minimal {
  width: 100%;
  min-height: 240px; /* 增加高度，去掉底部标签后有更多空间 */
  border: none;
  resize: none;
  font-size: 15px;
  line-height: 1.6;
  color: #333;
  font-family: inherit;
  background: transparent;
  padding: 0; /* 去掉顶部padding，不再需要为标签留空间 */
}

.script-textarea-minimal:focus {
  outline: none;
}

/* 响应式 */
@media (max-width: 1024px) {
  .script-layout {
    flex-direction: column;
  }
  
  .sidebar-section {
    width: 100%;
  }
  
  .sidebar-sticky {
    position: static;
  }
  
  .main-textarea-minimal {
    min-height: 300px;
  }
}
</style>