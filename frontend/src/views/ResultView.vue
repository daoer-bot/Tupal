<template>
  <div class="studio-container">
    <!-- 背景装饰：网格纸 + 漂浮糖果 -->
    <div class="studio-bg-decor">
      <div class="grid-pattern"></div>
      <div class="floating-shapes">
        <div class="shape shape-circle"></div>
        <div class="shape shape-triangle"></div>
        <div class="shape shape-wave"></div>
        <div class="shape shape-donut"></div>
      </div>
    </div>

    <!-- 主体布局：三列结构 -->
    <div v-if="store.currentOutline" class="studio-layout">
      
      <!-- 左列：手机预览 (导航) -->
      <div class="zone-preview">
        <div class="showcase-stage">
          <div class="phone-mockup-real" :style="phoneStyle">
            <!-- 物理按键 -->
            <div class="btn-volume-up"></div>
            <div class="btn-volume-down"></div>
            <div class="btn-power"></div>
            
            <!-- 灵动岛 -->
            <div class="dynamic-island">
              <div class="camera-lens"></div>
              <div class="sensor"></div>
            </div>

            <!-- 屏幕内容 -->
            <div class="screen-content">
              <!-- 顶部状态栏 -->
              <div class="status-bar">
                <span class="time">21:59</span>
                <div class="status-icons">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor"><path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33C7 21.4 7.6 22 8.33 22h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4z"/></svg>
                </div>
              </div>

              <!-- 小红书顶部导航栏 -->
              <div class="xhs-nav-bar">
                <div class="nav-left">
                  <button class="nav-back-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
                  </button>
                  <div class="nav-author">
                    <div class="nav-avatar">
                      <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="avatar" />
                    </div>
                    <span class="nav-author-name">iOS同学</span>
                  </div>
                </div>
                <div class="nav-right">
                  <button class="nav-follow-btn">关注</button>
                  <button class="nav-share-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg>
                  </button>
                </div>
              </div>

              <!-- 小红书风格内容区 -->
              <div class="xhs-content">
                <!-- 图片滑动区域 -->
                <div
                  class="xhs-image-area"
                  :class="{ 'is-dragging': isDragging }"
                  @touchstart="handleTouchStart"
                  @touchmove="handleTouchMove"
                  @touchend="handleTouchEnd"
                  @mousedown="handleMouseDown"
                >
                  <div class="xhs-image-slider" :style="sliderStyle">
                    <div
                      v-for="(page, index) in store.currentOutline.pages"
                      :key="`slide-${page.page_number}`"
                      class="xhs-image-slide"
                    >
                      <img
                        v-if="page.image_url"
                        :src="page.image_url"
                        class="xhs-image"
                        draggable="false"
                      />
                      <div v-else class="xhs-image-placeholder">
                        <div v-if="isGenerating && isPageGenerating(page.page_number)" class="loading-spinner-lg"></div>
                        <div v-else class="xhs-empty-state">
                          <span class="icon">🖼️</span>
                          <span>等待生成</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <!-- 页码指示器 -->
                  <div class="xhs-page-indicator">
                    {{ selectedPageIndex + 1 }} / {{ store.currentOutline.pages.length }}
                  </div>
                </div>

                <!-- 圆点指示器 -->
                <div class="xhs-dots">
                  <span
                    v-for="(page, index) in store.currentOutline.pages"
                    :key="`dot-${page.page_number}`"
                    class="xhs-dot"
                    :class="{ active: selectedPageIndex === index }"
                    @click="selectPage(index)"
                  ></span>
                </div>

                <!-- 文案内容区 -->
                <div class="xhs-text-area">
                  <!-- 标题 -->
                  <div class="xhs-title">{{ store.currentOutline.topic }}</div>

                  <!-- 正文内容 -->
                  <div class="xhs-body">
                    {{ selectedPage?.xiaohongshu_content || '暂无文案内容...' }}
                  </div>

                  <!-- 标签 -->
                  <div class="xhs-tags">
                    <span class="xhs-tag">#创意</span>
                    <span class="xhs-tag">#AI生成</span>
                    <span class="xhs-tag">#灵感</span>
                  </div>

                  <!-- 发布时间和地点 -->
                  <div class="xhs-meta">
                    <span>12-14 上海</span>
                  </div>
                </div>
              </div>

              <!-- 底部互动栏 -->
              <div class="xhs-bottom-bar">
                <div class="xhs-comment-input">
                  <svg class="icon-edit" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  <span>说点什么...</span>
                </div>
                <div class="xhs-actions">
                  <div class="xhs-action-item">
                    <svg class="xhs-action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                    <span class="xhs-action-count">33</span>
                  </div>
                  <div class="xhs-action-item">
                    <svg class="xhs-action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                    <span class="xhs-action-count">30</span>
                  </div>
                  <div class="xhs-action-item">
                    <svg class="xhs-action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
                    <span class="xhs-action-count">21</span>
                  </div>
                </div>
              </div>

              <div class="home-indicator"></div>
            </div>
          </div>
          <div class="phone-shadow" :style="phoneShadowStyle"></div>
        </div>
      </div>

      <!-- 中列：图文详情 (画廊) -->
      <div class="zone-detail">
        <div class="zone-header">
          <h3>图文详情</h3>
          <div class="page-indicator">
            <button class="nav-btn" :disabled="selectedPageIndex === 0" @click="selectPage(selectedPageIndex - 1)">‹</button>
            <span>{{ selectedPageIndex + 1 }} / {{ store.currentOutline.pages.length }}</span>
            <button class="nav-btn" :disabled="selectedPageIndex === store.currentOutline.pages.length - 1" @click="selectPage(selectedPageIndex + 1)">›</button>
          </div>
        </div>

        <div class="detail-gallery">
          <!-- 大图展示 -->
          <div class="main-image-container">
            <div v-if="selectedPage?.image_url" class="image-wrapper">
              <img :src="selectedPage.image_url" class="main-image" @click="openPreview(selectedPage.image_url)" />
              <button class="btn-zoom-large" @click="openPreview(selectedPage.image_url)">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607zM10.5 7.5v6m3-3h-6" /></svg>
              </button>
            </div>
            <div v-else class="placeholder-large">
              <div v-if="isGenerating && isPageGenerating(selectedPage?.page_number)" class="loading-spinner-lg"></div>
              <div v-else class="empty-state">
                <span class="icon">🖼️</span>
                <span>等待生成...</span>
              </div>
            </div>
          </div>

          <!-- 缩略图列表 -->
          <div class="thumbnail-strip">
            <div 
              v-for="(page, index) in store.currentOutline.pages" 
              :key="page.page_number"
              class="thumbnail-item"
              :class="{ active: selectedPageIndex === index }"
              @click="selectPage(index)"
            >
              <img v-if="page.image_url" :src="page.image_url" />
              <div v-else class="thumb-placeholder">{{ page.page_number }}</div>
            </div>
          </div>

        </div>
      </div>

      <!-- 右列：画面提示词 -->
      <div class="zone-editor">
        <div class="editor-content">
          <div class="editor-grid">
            <!-- 提示词编辑 -->
            <div class="candy-card editor-card stretch">
              <div class="card-header-sm">
                <span class="icon">🎨</span>
                <span>画面提示词</span>
              </div>
              <textarea
                v-model="currentEditingPrompt"
                class="candy-input prompt-area"
                placeholder="描述你想要的画面细节..."
                :disabled="isGenerating"
              ></textarea>
            </div>
          </div>

          <!-- 操作区 -->
          <div class="action-area">
            <button
              class="btn btn-primary btn-block btn-regen"
              @click="regenerateCurrent"
              :disabled="isGenerating"
            >
              <span v-if="isGenerating && isPageGenerating(selectedPage?.page_number)" class="loading-spinner-sm"></span>
              <span v-else>✨ 重新生成此图</span>
            </button>
            
            <div class="btn-row">
              <button class="btn btn-secondary" @click="restoreDefaultPrompt" :disabled="isGenerating">
                ↺ 恢复默认
              </button>
              <button v-if="selectedPage?.image_url" @click="downloadSingle" class="btn btn-secondary">
                ⬇ 下载
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
    
    <!-- 空状态 -->
    <div v-if="!store.currentOutline && !isGenerating" class="empty-state-container">
      <div class="candy-card empty-card">
        <div class="empty-icon">📭</div>
        <h2>暂无内容</h2>
        <p>似乎还没有生成任何内容，去首页找找灵感吧！</p>
        <button @click="goHome" class="btn btn-primary">返回首页</button>
      </div>
    </div>

    <!-- 全屏预览模态框 -->
    <Teleport to="body">
      <div v-if="previewUrl" class="preview-modal" @click="closePreview">
        <div class="modal-backdrop"></div>
        <div class="modal-content-wrapper">
          <img :src="previewUrl" class="modal-image" @click.stop />
          <button class="modal-close" @click="closePreview">×</button>
          <button v-if="canGoPrev" class="modal-nav prev" @click.stop="goToPrevImage">‹</button>
          <button v-if="canGoNext" class="modal-nav next" @click.stop="goToNextImage">›</button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../store'
import { generateImages, subscribeProgress, saveHistory, type ProgressData } from '../services/api'
import materialApi from '../services/materialApi'
import toast from '../utils/toast'

const router = useRouter()
const store = useAppStore()

// 视图状态
const selectedPageIndex = ref<number>(0)
const editingPrompts = ref<Record<number, string>>({})
const initialPrompts = ref<Record<number, string>>({})
const editingCaptions = ref<Record<number, string>>({})
const previewUrl = ref('')
const previewImageIndex = ref<number>(0)
const phoneScale = ref(1)

// 滑动相关状态
const isDragging = ref(false)
const touchStartX = ref(0)
const touchCurrentX = ref(0)
const dragOffset = ref(0)

// 状态
const isGenerating = ref(false)
const generatingPages = ref<Set<number>>(new Set())
const eventSource = ref<EventSource | null>(null)
const selectedGenerator = ref(store.imageModelConfig.generatorType || 'image_api')

// 进度数据
const progressData = ref<ProgressData>({
  task_id: '',
  status: 'pending',
  progress: 0,
  total_pages: 0,
  completed_pages: 0,
  current_page: 0,
  message: '准备开始...',
  images: [],
  failed_pages: [],
  timestamp: ''
})

// 计算属性
const hasImages = computed(() => {
  return store.currentOutline?.pages?.some(p => !!p.image_url) ?? false
})

const imagesWithUrls = computed(() => {
  if (!store.currentOutline) return []
  return store.currentOutline.pages.filter(p => !!p.image_url)
})

const canGoPrev = computed(() => previewImageIndex.value > 0)
const canGoNext = computed(() => previewImageIndex.value < imagesWithUrls.value.length - 1)

const selectedPage = computed(() => {
  if (!store.currentOutline) return null
  return store.currentOutline.pages[selectedPageIndex.value]
})

const phoneStyle = computed(() => ({
  width: `${393 * phoneScale.value}px`,
  height: `${852 * phoneScale.value}px`
}))

// 滑动样式
const sliderStyle = computed(() => {
  const baseOffset = -selectedPageIndex.value * 100
  const dragPercent = dragOffset.value
  return {
    transform: `translateX(calc(${baseOffset}% + ${dragPercent}px))`,
    transition: isDragging.value ? 'none' : 'transform 0.3s ease-out'
  }
})

const phoneShadowStyle = computed(() => ({
  width: `${330 * phoneScale.value}px`,
  height: `${24 * phoneScale.value}px`
}))

const currentEditingPrompt = computed({
  get: () => {
    if (!selectedPage.value) return ''
    return editingPrompts.value[selectedPageIndex.value] ?? selectedPage.value.description
  },
  set: (val: string) => {
    if (selectedPage.value) {
      editingPrompts.value[selectedPageIndex.value] = val
    }
  }
})

const currentEditingCaption = computed({
  get: () => {
    if (!selectedPage.value) return ''
    return editingCaptions.value[selectedPageIndex.value] ?? selectedPage.value.xiaohongshu_content
  },
  set: (val: string) => {
    if (selectedPage.value && store.currentOutline) {
      editingCaptions.value[selectedPageIndex.value] = val
      store.currentOutline.pages[selectedPageIndex.value].xiaohongshu_content = val
    }
  }
})

// 方法
const selectPage = (index: number) => {
  if (!store.currentOutline) return
  const maxIndex = store.currentOutline.pages.length - 1
  const clampedIndex = Math.max(0, Math.min(index, maxIndex))
  selectedPageIndex.value = clampedIndex
  if (editingPrompts.value[clampedIndex] === undefined && store.currentOutline) {
    editingPrompts.value[clampedIndex] = store.currentOutline.pages[clampedIndex].description
  }
  if (editingCaptions.value[clampedIndex] === undefined && store.currentOutline) {
    editingCaptions.value[clampedIndex] = store.currentOutline.pages[clampedIndex].xiaohongshu_content || ''
  }
}

// 滑动处理方法
const SWIPE_THRESHOLD = 50 // 滑动阈值

const handleTouchStart = (e: TouchEvent) => {
  isDragging.value = true
  touchStartX.value = e.touches[0].clientX
  touchCurrentX.value = e.touches[0].clientX
  dragOffset.value = 0
}

const handleTouchMove = (e: TouchEvent) => {
  if (!isDragging.value) return
  touchCurrentX.value = e.touches[0].clientX
  dragOffset.value = touchCurrentX.value - touchStartX.value
}

const handleTouchEnd = () => {
  if (!isDragging.value) return
  handleSwipeEnd()
}

const handleMouseDown = (e: MouseEvent) => {
  isDragging.value = true
  touchStartX.value = e.clientX
  touchCurrentX.value = e.clientX
  dragOffset.value = 0
  
  // 添加全局鼠标事件监听
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const handleMouseMove = (e: MouseEvent) => {
  if (!isDragging.value) return
  touchCurrentX.value = e.clientX
  dragOffset.value = touchCurrentX.value - touchStartX.value
}

const handleMouseUp = () => {
  if (!isDragging.value) return
  handleSwipeEnd()
  
  // 移除全局鼠标事件监听
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}

const handleSwipeEnd = () => {
  const swipeDistance = dragOffset.value
  
  if (Math.abs(swipeDistance) > SWIPE_THRESHOLD) {
    if (swipeDistance < 0) {
      // 向左滑动 -> 下一页
      selectPage(selectedPageIndex.value + 1)
    } else {
      // 向右滑动 -> 上一页
      selectPage(selectedPageIndex.value - 1)
    }
  }
  
  isDragging.value = false
  dragOffset.value = 0
}

const handleImageClick = (e: MouseEvent) => {
  // 只有在没有拖拽的情况下才触发点击预览
  if (Math.abs(dragOffset.value) < 5 && selectedPage.value?.image_url) {
    openPreview(selectedPage.value.image_url)
  }
}

const openPreview = (url: string) => {
  previewUrl.value = url
  const index = imagesWithUrls.value.findIndex(p => p.image_url === url)
  if (index !== -1) {
    previewImageIndex.value = index
  }
}

const closePreview = () => {
  previewUrl.value = ''
}

const goToPrevImage = () => {
  if (canGoPrev.value) {
    previewImageIndex.value--
    previewUrl.value = imagesWithUrls.value[previewImageIndex.value].image_url || ''
  }
}

const goToNextImage = () => {
  if (canGoNext.value) {
    previewImageIndex.value++
    previewUrl.value = imagesWithUrls.value[previewImageIndex.value].image_url || ''
  }
}

const appendTag = (tag: string) => {
  if (currentEditingPrompt.value) {
    currentEditingPrompt.value += ` ${tag}`
  } else {
    currentEditingPrompt.value = tag
  }
}

const restoreDefaultPrompt = () => {
  if (initialPrompts.value[selectedPageIndex.value]) {
    currentEditingPrompt.value = initialPrompts.value[selectedPageIndex.value]
  }
}

const isPageGenerating = (pageNumber: number | undefined) => {
  return pageNumber !== undefined && generatingPages.value.has(pageNumber)
}

const buildFullOutline = () => {
  if (!store.currentOutline) return ''
  const pages = store.currentOutline.pages
  return pages.map(page => `${page.title}\n${page.description}`).join('\n\n<page>\n\n')
}

const copyText = (text: string | undefined) => {
  if (!text) return
  navigator.clipboard.writeText(text).then(() => {
    toast.success('已复制到剪贴板')
  }).catch(() => {
    toast.error('复制失败')
  })
}

const regenerateCurrent = async () => {
  if (!selectedPage.value || !store.currentOutline) return
  
  const pageIndex = selectedPageIndex.value
  store.currentOutline.pages[pageIndex].description = currentEditingPrompt.value
  
  try {
    isGenerating.value = true
    generatingPages.value.add(selectedPage.value.page_number)
    
    const currentPrompt = currentEditingPrompt.value
    const processResult = await materialApi.processBatchPrompts([currentPrompt])
    
    let enhancedPrompt = currentPrompt
    let referenceImages: string[] = []
    
    if (processResult.success && processResult.enhanced_prompts && processResult.enhanced_prompts.length > 0) {
      enhancedPrompt = processResult.enhanced_prompts[0]
      referenceImages = processResult.reference_images || []
    }
    
    const singlePage = {
      ...store.currentOutline.pages[pageIndex],
      description: enhancedPrompt
    }
    
    const regenerateTaskId = `${store.currentOutline.task_id}_regen_${Date.now()}`
    
    const finalReferenceImage = referenceImages.length > 0
      ? referenceImages[0]
      : (store.referenceImage || undefined)
    
    const response = await generateImages({
      task_id: regenerateTaskId,
      pages: [singlePage],
      topic: store.currentOutline.topic,
      reference_image: finalReferenceImage,
      generator_type: selectedGenerator.value,
      image_model_config: store.imageModelConfig,
      image_generation_config: store.imageGenerationConfig,
      full_outline: buildFullOutline()
    })
    
    if (response.success) {
      subscribeToProgress(response.data.task_id)
    } else {
      throw new Error('启动生成任务失败')
    }
  } catch (err: any) {
    toast.error(err.message || '生成失败，请重试')
    isGenerating.value = false
    generatingPages.value.delete(selectedPage.value.page_number)
  }
}

const startGeneration = async () => {
  if (!store.currentOutline) {
    toast.error('没有可用的大纲')
    return
  }

  try {
    isGenerating.value = true
    store.currentOutline.pages.forEach(p => {
      if (!p.image_url) generatingPages.value.add(p.page_number)
    })
    
    const prompts = store.currentOutline.pages.map(p => p.description)
    const processResult = await materialApi.processBatchPrompts(prompts)
    
    let enhancedPages = store.currentOutline.pages
    let referenceImages: string[] = []
    
    if (processResult.success && processResult.enhanced_prompts) {
      enhancedPages = store.currentOutline.pages.map((page, index) => ({
        ...page,
        description: processResult.enhanced_prompts![index] || page.description
      }))
      referenceImages = processResult.reference_images || []
    }
    
    const generatorType = store.imageModelConfig.generatorType || selectedGenerator.value
    
    const finalReferenceImage = referenceImages.length > 0
      ? referenceImages[0]
      : (store.referenceImage || undefined)
    
    const response = await generateImages({
      task_id: store.currentOutline.task_id,
      pages: enhancedPages,
      topic: store.currentOutline.topic,
      reference_image: finalReferenceImage,
      generator_type: generatorType,
      image_model_config: store.imageModelConfig,
      image_generation_config: store.imageGenerationConfig,
      full_outline: buildFullOutline()
    })
    
    if (response.success) {
      subscribeToProgress(response.data.task_id)
    } else {
      throw new Error('启动生成任务失败')
    }
  } catch (err: any) {
    toast.error(err.message || '生成失败，请重试')
    isGenerating.value = false
    generatingPages.value.clear()
  }
}

const subscribeToProgress = (taskId: string) => {
  if (eventSource.value) {
    eventSource.value.close()
  }

  eventSource.value = subscribeProgress(
    taskId,
    (data: ProgressData) => {
      progressData.value = {
        ...progressData.value,
        ...data,
        images: data.images || progressData.value.images || [],
        failed_pages: data.failed_pages || progressData.value.failed_pages || []
      }
      
      if (data.images && data.images.length > 0) {
        data.images.forEach(img => {
          const page = store.currentOutline!.pages.find(p => p.page_number === img.page_number)
          if (page) {
            page.image_url = img.url
            generatingPages.value.delete(page.page_number)
          }
        })
      }
      
      if (data.failed_pages && data.failed_pages.length > 0) {
        data.failed_pages.forEach(fail => {
          generatingPages.value.delete(fail.page_number)
          toast.error(`第 ${fail.page_number} 页生成失败: ${fail.error}`, 5000)
        })
      }
    },
    (err: Error) => {
      toast.error(err.message || 'SSE连接错误')
      isGenerating.value = false
      generatingPages.value.clear()
    },
    async () => {
      isGenerating.value = false
      generatingPages.value.clear()
      
      if (store.currentOutline && progressData.value.images) {
        progressData.value.images.forEach(img => {
          const page = store.currentOutline!.pages.find(p => p.page_number === img.page_number)
          if (page) page.image_url = img.url
        })
        
        try {
          await saveHistory({
            task_id: store.currentOutline.task_id,
            topic: store.currentOutline.topic,
            pages: store.currentOutline.pages,
            reference_image: store.referenceImage || undefined,
            generator_type: selectedGenerator.value,
            status: 'completed'
          })
        } catch (err) {
          console.error('保存历史记录失败:', err)
        }
      }
    }
  )
}

const goHome = () => {
  router.push('/inspiration')
}

const downloadSingle = async () => {
  if (!selectedPage.value?.image_url) return
  try {
    const response = await fetch(selectedPage.value.image_url)
    const blob = await response.blob()
    const blobUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = `page_${selectedPage.value.page_number}.jpg`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(blobUrl)
  } catch (err) {
    console.error('下载图片失败:', err)
  }
}

const updateScale = () => {
  // 减去导航栏高度(约80px)和上下padding(40px)
  const availableHeight = window.innerHeight - 120
  const phoneHeight = 920 // 手机模型高度(852) + 阴影/边距
  const scale = Math.min(availableHeight / phoneHeight, 1)
  phoneScale.value = Math.max(scale, 0.5) // 最小缩放 0.5
}

onMounted(() => {
  updateScale()
  window.addEventListener('resize', updateScale)

  if (!store.currentOutline) {
    router.push('/inspiration')
    return
  }

  store.currentOutline.pages.forEach((page, index) => {
    initialPrompts.value[index] = page.description
    editingPrompts.value[index] = page.description
    editingCaptions.value[index] = page.xiaohongshu_content || ''
  })

  const hasAnyImages = store.currentOutline.pages.some(p => !!p.image_url)
  if (!hasAnyImages) {
    startGeneration()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', updateScale)
  if (eventSource.value) {
    eventSource.value.close()
  }
})
</script>

<style scoped>
/* --- 核心容器 --- */
.studio-container {
  width: 100%;
  height: calc(100vh - var(--nav-height, 0px));
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  background: transparent;
  padding: 0;
  box-sizing: border-box;
}

/* 背景装饰 */
.studio-bg-decor {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
  background: transparent;
}

/* 噪点纹理 - 增加质感 */
.studio-bg-decor::before {
  display: none;
}

.grid-pattern {
  display: none;
}

.floating-shapes .shape {
  position: absolute;
  opacity: 0.6;
  animation: float 10s infinite ease-in-out alternate;
}

.shape-circle {
  width: 120px;
  height: 120px;
  background: radial-gradient(circle at 30% 30%, var(--macaron-pink-light), var(--macaron-pink));
  border-radius: 50%;
  bottom: 10%;
  left: -5%;
  filter: blur(40px);
  opacity: 0.4;
}

.shape-triangle {
  width: 0;
  height: 0;
  border-left: 40px solid transparent;
  border-right: 40px solid transparent;
  border-bottom: 70px solid var(--macaron-mint-light);
  top: 60%;
  right: 10%;
  transform: rotate(15deg);
  filter: blur(15px);
  animation-delay: -2s;
}

.shape-wave {
  width: 200px;
  height: 200px;
  background: var(--macaron-purple);
  border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
  bottom: -5%;
  left: 20%;
  filter: blur(40px);
  opacity: 0.3;
  animation-delay: -5s;
}

.shape-donut {
  width: 80px;
  height: 80px;
  border: 15px solid var(--macaron-yellow);
  border-radius: 50%;
  top: 20%;
  right: 20%;
  filter: blur(10px);
  opacity: 0.5;
  animation-delay: -3s;
}

@keyframes float {
  0% { transform: translateY(0) rotate(0deg); }
  100% { transform: translateY(-20px) rotate(10deg); }
}

/* --- 悬浮返回按钮 --- */
.floating-back-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 100;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 30px;
  padding: 8px 20px;
  cursor: pointer;
  transition: all 0.3s var(--ease-spring);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.floating-back-btn:hover {
  background: #fff;
  transform: translateX(5px);
  box-shadow: 0 8px 20px rgba(255, 154, 162, 0.2);
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-secondary);
}

.floating-back-btn:hover .btn-content {
  color: var(--primary-color);
}

.btn-content svg { width: 18px; height: 18px; }

/* --- 主体布局 (Grid) --- */
.studio-layout {
  display: grid;
  grid-template-columns: 420px 1fr 360px;
  width: 100%;
  min-height: 100%;
  max-width: 1800px;
  margin: 0 auto;
  padding: 20px;
  gap: 24px;
  z-index: 1;
  overflow: visible;
  box-sizing: border-box;
}

/* 通用区域样式 */
.zone-preview,
.zone-detail,
.zone-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.zone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 0 8px;
}

.zone-header h3 {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.zone-header .subtitle {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* --- 左列：手机预览 --- */
.zone-preview {
  align-items: center;
  overflow: visible;
  padding: 24px 0;
}

.showcase-stage {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  /* transform: scale(0.9); */
  transform-origin: center center;
  height: 100%;
  /* overflow-y: auto; */
  /* padding-bottom: 40px; */
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: visible;
}

/* 手机模型 Real Style */
.phone-mockup-real {
  width: 393px;
  height: 852px;
  background: #000;
  border-radius: 55px;
  position: relative;
  /* 模拟金属边框 */
  box-shadow:
    0 0 0 2px #333,
    0 0 0 6px #d4d4d4, /* 银色边框 */
    0 0 0 7px #a0a0a0,
    0 20px 50px rgba(0,0,0,0.2);
  z-index: 10;
  padding: 12px; /* 边框厚度 */
  box-sizing: border-box;
  transform-style: preserve-3d;
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.phone-shadow {
  width: 330px;
  height: 20px;
  background: radial-gradient(ellipse at center, rgba(0,0,0,0.1) 0%, transparent 70%);
  margin-top: 40px;
  border-radius: 50%;
  filter: blur(5px);
  flex-shrink: 0;
}

/* 物理按键 */
.btn-volume-up, .btn-volume-down, .btn-power {
  position: absolute;
  background: #e0e0e0;
  border-radius: 4px;
  width: 4px;
}

.btn-volume-up { left: -12px; top: 120px; height: 40px; }
.btn-volume-down { left: -12px; top: 170px; height: 40px; }
.btn-power { right: -12px; top: 140px; height: 60px; }

/* 灵动岛 */
.dynamic-island {
  position: absolute;
  top: 22px; /* 调整位置 */
  left: 50%;
  transform: translateX(-50%);
  width: 126px;
  height: 37px;
  background: #000;
  border-radius: 20px;
  z-index: 100; /* 确保在最上层 */
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.camera-lens {
  width: 10px;
  height: 10px;
  background: #1a1a1a;
  border-radius: 50%;
  box-shadow: inset 0 0 3px rgba(255,255,255,0.3);
}

.sensor {
  width: 6px;
  height: 6px;
  background: #1a1a1a;
  border-radius: 50%;
}

/* 屏幕内容 */
.screen-content {
  width: 100%;
  height: 100%;
  border-radius: 44px; /* 稍微减小圆角以匹配内屏 */
  overflow: hidden;
  background: #fff;
  position: relative;
  display: flex;
  flex-direction: column;
  mask-image: radial-gradient(white, black);
  -webkit-mask-image: -webkit-radial-gradient(white, black);
}

.status-bar {
  height: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 24px 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  background: #fff;
  z-index: 20;
}

.status-icons {
  display: flex;
  gap: 6px;
}

.status-icons .icon { width: 16px; height: 16px; }

/* 滚动容器 */
.scroll-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  padding-bottom: 160px;
}

.scroll-container::-webkit-scrollbar { width: 0; }
/* Xiaohongshu 导航与内容 */
.note-wrapper {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #fff;
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.note-header-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(0,0,0,0.04);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  cursor: pointer;
}

.note-header-actions {
  display: flex;
  gap: 8px;
}

.header-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.05);
  cursor: pointer;
}

.note-media {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.note-media-main {
  position: relative;
  width: 100%;
  aspect-ratio: 4/5;
  border-radius: 22px;
  overflow: hidden;
  background: #f5f5f5;
  box-shadow: 0 12px 30px rgba(0,0,0,0.08);
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
  touch-action: pan-y pinch-zoom;
}

.note-media-main.is-dragging {
  cursor: grabbing;
}

/* 滑动容器 */
.note-media-slider {
  display: flex;
  width: 100%;
  height: 100%;
  will-change: transform;
}

.note-media-slide {
  flex-shrink: 0;
  width: 100%;
  height: 100%;
  position: relative;
}

.note-media-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  pointer-events: none;
}

.note-media-placeholder,
.note-media-empty {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #aaa;
  font-weight: 600;
}

.note-media-indicator {
  position: absolute;
  right: 12px;
  bottom: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(0,0,0,0.65);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}

.note-media-thumbs {
  display: flex;
  justify-content: center;
  gap: 6px;
}

.thumb-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(0,0,0,0.15);
  border: none;
  cursor: pointer;
  transition: transform 0.2s, background 0.2s;
}

.thumb-dot.active {
  transform: scale(1.2);
  background: var(--primary-color);
}

.note-author-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.author-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

.author-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.author-name {
  font-size: 14px;
  font-weight: 700;
  color: #333;
}

.author-desc {
  font-size: 12px;
  color: #a0a0a0;
}
.btn-follow {
  border: none;
  background: #ff2d55;
  color: #fff;
  padding: 6px 16px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 6px 12px rgba(255, 45, 85, 0.3);
}

.note-title {
  font-size: 18px;
  font-weight: 800;
  color: #333;
}

.note-text {
  font-size: 14px;
  line-height: 1.7;
  color: #444;
  white-space: pre-wrap;
}

.note-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.note-tags span {
  background: #fff5f5;
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  color: #ff2442;
  font-weight: 600;
}

.note-comment-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 16px;
  background: #fff8f8;
}

.comment-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #ffe1e7;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.comment-copy {
  flex: 1;
}

.comment-user {
  margin: 0;
  font-size: 12px;
  color: #999;
  font-weight: 600;
}

.comment-text {
  margin: 4px 0 0;
  font-size: 13px;
  color: #444;
}

.comment-like {
  font-size: 12px;
  color: #ff2442;
  font-weight: 600;
}

.note-bottom-bar {
  position: absolute;
  bottom: 20px;
  left: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  padding: 10px 16px;
  box-shadow: 0 15px 30px rgba(0,0,0,0.08);
  border: 1px solid rgba(0,0,0,0.05);
}

.note-input {
  flex: 1;
  background: #f5f5f5;
  border-radius: 16px;
  padding: 8px 12px;
  font-size: 12px;
  color: #999;
}

.note-bottom-actions {
  display: flex;
  gap: 8px;
}

.note-bottom-actions button {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: #fff;
  box-shadow: 0 4px 8px rgba(0,0,0,0.08);
  cursor: pointer;
}

.home-indicator {
  position: absolute;
  bottom: 6px;
  left: 50%;
  transform: translateX(-50%);
  width: 110px;
  height: 4px;
  background: rgba(0,0,0,0.2);
  border-radius: 999px;
  z-index: 5;
}

/* ========== 小红书风格样式 ========== */
/* 顶部导航栏 */
.xhs-nav-bar {
  height: 44px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 12px;
  background: #fff;
  z-index: 20;
  flex-shrink: 0;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-back-btn {
  width: 24px;
  height: 24px;
  background: none;
  border: none;
  padding: 0;
  color: #333;
  cursor: pointer;
}

.nav-back-btn svg {
  width: 24px;
  height: 24px;
}

.nav-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  background: #eee;
}

.nav-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.nav-author-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-follow-btn {
  padding: 4px 12px;
  border-radius: 14px;
  border: 1px solid #ff2442;
  background: transparent;
  color: #ff2442;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  line-height: 1.2;
}

.nav-share-btn {
  width: 24px;
  height: 24px;
  background: none;
  border: none;
  padding: 0;
  color: #333;
  cursor: pointer;
}

.nav-share-btn svg {
  width: 20px;
  height: 20px;
}

.xhs-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
  background: #fff;
  padding-bottom: 60px; /* 为底部栏留出空间 */
}

.xhs-content::-webkit-scrollbar {
  width: 0;
}

/* 图片滑动区域 */
.xhs-image-area {
  position: relative;
  width: 100%;
  aspect-ratio: 4/5;
  background: #f5f5f5;
  overflow: hidden;
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
  touch-action: pan-y pinch-zoom;
  flex-shrink: 0;
}

.xhs-image-area.is-dragging {
  cursor: grabbing;
}

.xhs-image-slider {
  display: flex;
  width: 100%;
  height: 100%;
  will-change: transform;
}

.xhs-image-slide {
  flex-shrink: 0;
  width: 100%;
  height: 100%;
  position: relative;
}

.xhs-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  pointer-events: none;
}

.xhs-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%);
}

.xhs-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #bbb;
  font-size: 13px;
  font-weight: 500;
}

.xhs-empty-state .icon {
  font-size: 32px;
}

/* 页码指示器 */
.xhs-page-indicator {
  position: absolute;
  right: 12px;
  top: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 12px;
  font-weight: 500;
}

/* 圆点指示器 */
.xhs-dots {
  display: flex;
  justify-content: center;
  gap: 6px;
  padding: 12px 0;
  flex-shrink: 0;
}

.xhs-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ddd;
  cursor: pointer;
  transition: all 0.2s ease;
}

.xhs-dot.active {
  width: 16px;
  border-radius: 3px;
  background: #ff2442;
}

/* 文案内容区 */
.xhs-text-area {
  padding: 12px 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 标题 */
.xhs-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
  margin-bottom: 4px;
}

/* 正文内容 */
.xhs-body {
  font-size: 14px;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 标签 */
.xhs-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.xhs-tag {
  font-size: 13px;
  color: #2e7cf6;
  font-weight: 500;
  cursor: pointer;
}

.xhs-tag:hover {
  text-decoration: underline;
}

/* 发布时间和地点 */
.xhs-meta {
  font-size: 12px;
  color: #999;
  padding-top: 4px;
}

/* 底部互动栏 */
.xhs-bottom-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px 24px;
  background: #fff;
  border-top: 1px solid #f5f5f5;
  z-index: 50;
}

.xhs-comment-input {
  flex: 1;
  height: 36px;
  background: #f5f5f5;
  border-radius: 18px;
  display: flex;
  align-items: center;
  padding: 0 12px;
  gap: 6px;
  font-size: 13px;
  color: #999;
}

.xhs-comment-input span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.icon-edit {
  width: 14px;
  height: 14px;
  color: #999;
  flex-shrink: 0;
}

.xhs-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.xhs-action-item {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: #333;
}

.xhs-action-icon {
  width: 24px;
  height: 24px;
  stroke-width: 1.5;
}

.xhs-action-count {
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

/* --- 中列：图文详情 (画廊) --- */
.zone-detail {
  background: rgba(255, 255, 255, 0.4); /* 更通透 */
  backdrop-filter: blur(40px) saturate(180%); /* 增强毛玻璃 */
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border-radius: 32px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  padding: 24px;
  box-shadow:
    0 12px 36px rgba(255, 183, 178, 0.1), /* 带颜色的阴影 */
    inset 0 0 0 1px rgba(255, 255, 255, 0.2);
}

.page-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.nav-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid #eee;
  background: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: all 0.2s;
}

.nav-btn:hover:not(:disabled) {
  background: var(--primary-color);
  color: #fff;
  border-color: var(--primary-color);
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.detail-gallery {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  padding-right: 4px;
  min-height: 0;
}

.main-image-container {
  width: 100%;
  height: min(420px, 60vh);
  background: #f8f8f8;
  border-radius: 20px;
  overflow: hidden;
  position: relative;
  box-shadow: inset 0 0 20px rgba(0,0,0,0.03);
  flex-shrink: 0;
}

.image-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.main-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  cursor: zoom-in;
}

.btn-zoom-large {
  position: absolute;
  bottom: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255,255,255,0.9);
  border: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
  transition: transform 0.2s;
}

.btn-zoom-large:hover {
  transform: scale(1.1);
}

.placeholder-large {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ccc;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  font-weight: 600;
}

.empty-state .icon { font-size: 48px; }

/* 缩略图条 */
.thumbnail-strip {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 4px;
  flex-shrink: 0;
}

.thumbnail-strip::-webkit-scrollbar { height: 6px; }
.thumbnail-strip::-webkit-scrollbar-thumb { background: #eee; border-radius: 3px; }

.thumbnail-item {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
  flex-shrink: 0;
}

.thumbnail-item.active {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 154, 162, 0.3);
}

.thumbnail-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  width: 100%;
  height: 100%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-weight: 700;
}

/* --- 右列：编辑工作台 --- */
.zone-editor {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border-radius: 32px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  padding: 24px;
  box-shadow:
    0 12px 36px rgba(255, 183, 178, 0.1),
    inset 0 0 0 1px rgba(255, 255, 255, 0.2);
}

.editor-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-right: 4px;
  min-height: 0;
}

.candy-card {
  background: rgba(255, 255, 255, 0.6); /* 卡片也半透明 */
  border-radius: 20px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.card-header-sm {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.card-header-sm .icon { font-size: 16px; }
.card-header-sm .dot {
  width: 8px;
  height: 8px;
  background: var(--primary-color);
  border-radius: 50%;
}

.candy-input {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #eee;
  background: #f9f9f9;
  font-family: inherit;
  font-size: 13px;
  color: var(--text-primary);
  resize: vertical;
  transition: all 0.2s;
}

.candy-input:focus {
  background: #fff;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(255, 154, 162, 0.1);
  outline: none;
}

.editor-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  min-height: 0;
}

.stretch {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.prompt-area {
  min-height: 0;
  flex: 1;
  resize: none;
}

.tags-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.style-chip {
  background: #f5f5f5;
  border: 1px solid transparent;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 600;
}

.style-chip:hover {
  background: var(--macaron-mint-light);
  color: var(--text-primary);
  border-color: var(--macaron-mint);
}

.action-area {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 20px;
}

.btn {
  padding: 12px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: var(--primary-color);
  color: #fff;
  box-shadow: 0 4px 12px rgba(255, 154, 162, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 154, 162, 0.5);
}

.btn-primary:disabled {
  background: #ccc;
  box-shadow: none;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: #f0f0f0;
  color: var(--text-secondary);
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.btn-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

/* 加载动画 */
.loading-pulse {
  width: 12px;
  height: 12px;
  background: var(--primary-color);
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.loading-spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-spinner-lg {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 154, 162, 0.3);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes pulse { 0% { transform: scale(0.8); opacity: 0.5; } 50% { transform: scale(1.2); opacity: 1; } 100% { transform: scale(0.8); opacity: 0.5; } }

/* 模态框 */
.preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-backdrop {
  position: absolute;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
}

.modal-content-wrapper {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  z-index: 1001;
}

.modal-image {
  max-width: 100%;
  max-height: 90vh;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(255, 154, 162, 0.3);
}

.modal-close {
  position: absolute;
  top: -50px;
  right: -20px;
  background: #fff;
  border: none;
  color: var(--text-primary);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: #fff;
  color: var(--text-primary);
  width: 56px;
  height: 56px;
  border-radius: 50%;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s var(--ease-spring);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  border: none;
}

.modal-nav:hover {
  transform: translateY(-50%) scale(1.1);
  background: var(--primary-color);
  color: #fff;
}

.modal-nav.prev { left: -80px; }
.modal-nav.next { right: -80px; }

/* 响应式 */
@media (max-width: 1280px) {
  .studio-layout {
    grid-template-columns: 320px 1fr 300px;
    gap: 16px;
  }
  
  .phone-mockup-candy {
    width: 320px;
    height: 650px;
  }
}

@media (max-width: 1024px) {
  .studio-layout {
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    height: auto;
  }
  
  .zone-preview, .zone-detail, .zone-editor {
    height: auto;
    overflow: visible;
  }
  
  .phone-mockup-candy {
    transform: none;
    margin: 0 auto;
  }
}
</style>
