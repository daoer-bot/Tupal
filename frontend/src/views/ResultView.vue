<template>
  <div class="result-view">
    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="retry" class="btn btn-secondary">重试</button>
    </div>

    <!-- 主体布局 -->
    <div v-if="store.currentOutline" class="split-layout">
      
      <!-- 左侧：小红书移动端预览区 -->
      <div class="preview-section">
        <div class="phone-mockup">
          <!-- 刘海 -->
          <div class="notch">
            <div class="camera"></div>
            <div class="speaker"></div>
          </div>
          
          <!-- 侧边按钮 -->
          <div class="side-btn volume-up"></div>
          <div class="side-btn volume-down"></div>
          <div class="side-btn power"></div>

          <!-- 顶部状态栏模拟 - 固定在顶部 -->
          <div class="status-bar-fixed">
            <span class="time">9:41</span>
            <div class="status-icons">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor"><path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33C7 21.4 7.6 22 8.33 22h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4z"/></svg>
            </div>
          </div>

          <!-- 可滚动内容容器 -->
          <div class="phone-content-scroll">
            <!-- 返回按钮 (仅单张模式显示) -->
            <transition name="fade">
              <button v-if="viewMode === 'single'" class="nav-back-btn" @click="exitSingleView">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
                </svg>
              </button>
            </transition>

            <!-- 图片和文案整体容器 -->
            <div class="content-wrapper">
              <!-- 图片区域 -->
              <div class="preview-images-container" :class="{ 'is-single': viewMode === 'single' }">
                <!-- 默认模式：3x3 网格 -->
                <transition name="fade-scale" mode="out-in">
                  <div v-if="viewMode === 'grid'" key="grid" class="grid-view">
                    <div
                      v-for="(page, index) in store.currentOutline.pages"
                      :key="page.page_number"
                      class="grid-item"
                      @click="enterSingleView(index)"
                    >
                      <div class="image-wrapper">
                        <img
                          v-if="page.image_url"
                          :src="page.image_url"
                          :alt="`Page ${page.page_number}`"
                          class="grid-image"
                        />
                        <div v-else class="grid-placeholder">
                          <span v-if="isGenerating && isPageGenerating(page.page_number)" class="loading-dot"></span>
                          <span v-else>P{{ page.page_number }}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 放大模式：单张大图 -->
                  <div v-else key="single" class="single-view" @click="exitSingleView">
                    <div class="single-image-wrapper" @click.stop>
                      <img
                        v-if="selectedPage?.image_url"
                        :src="selectedPage.image_url"
                        :alt="`Page ${selectedPage.page_number}`"
                        class="single-image"
                        @click="openPreview(selectedPage.image_url)"
                      />
                      <div v-else class="single-placeholder" @click="exitSingleView">
                        <div v-if="isGenerating && isPageGenerating(selectedPage?.page_number)" class="generating-state">
                          <div class="skeleton-pulse"></div>
                          <div class="loading-dots">
                            <span></span><span></span><span></span>
                          </div>
                        </div>
                        <span v-else>暂无图片</span>
                      </div>
                      
                      <!-- 放大提示 -->
                      <div class="zoom-hint" v-if="selectedPage?.image_url">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607zM10.5 7.5v6m3-3h-6" />
                        </svg>
                      </div>
                    </div>
                  </div>
                </transition>
              </div>

              <!-- 底部文案区域 - 在图片容器外部 -->
              <div class="preview-caption-container">
                <div class="caption-content">
                  <h3 class="caption-title">{{ store.currentOutline.topic }}</h3>
                  <p class="caption-text">
                    {{ store.currentOutline.pages[0]?.xiaohongshu_content || '暂无文案内容' }}
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 互动栏 - 固定在底部 -->
          <div class="interaction-bar-fixed">
            <div class="interaction-input">说点什么...</div>
            <div class="interaction-icons">
              <div class="icon-item">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                </svg>
                <span>1.2w</span>
              </div>
              <div class="icon-item">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                </svg>
                <span>520</span>
              </div>
              <div class="icon-item">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
                </svg>
                <span>88</span>
              </div>
            </div>
          </div>
          <!-- 结束可滚动内容容器 -->
          
          <!-- 底部 Home 条 (固定在手机外壳底部) -->
          <div class="home-indicator"></div>
        </div>
      </div>

      <!-- 右侧：操作区 -->
      <div class="editor-section">
        <!-- 上方：提示词编辑区（根据选择显示/隐藏） -->
        <div class="prompt-editor-container">
          <transition name="fade" mode="out-in">
            <!-- 默认提示 -->
            <div v-if="viewMode === 'grid'" key="hint" class="editor-hint">
              <div class="hint-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.042 21.672L13.684 16.6m0 0l-2.51 2.225.569-9.47 5.227 7.917-3.286-.672zM12 2.25V4.5m5.834.166l-1.591 1.591M20.25 10.5H18M7.757 14.743l-1.59 1.59M6 10.5H3.75m4.007-4.243l-1.59-1.59" />
                </svg>
              </div>
              <p>点击左侧任意图片<br>查看并编辑对应提示词</p>
              
              <div class="global-actions">
                <button @click="downloadAll" class="btn btn-outline-primary" :disabled="!hasImages">
                  下载全部图片
                </button>
                <button @click="goHome" class="btn btn-text">
                  返回首页
                </button>
              </div>
            </div>

            <!-- 提示词编辑模块 -->
            <div v-else key="editor" class="editor-module">
            <div class="editor-header">
              <h3 class="editor-title">当前图片提示词 (P{{ selectedPage?.page_number }})</h3>
              <button class="close-editor-btn" @click="exitSingleView">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div class="editor-content">
              <textarea
                v-model="currentEditingPrompt"
                class="prompt-input"
                placeholder="修改提示词（例：小红书风格、奶茶探店、暖色调、胶片感、高清细节）"
                :disabled="isGenerating"
              ></textarea>

              <!-- 热门标签 -->
              <div class="tags-container">
                <span class="tags-label">推荐风格：</span>
                <div class="tags-list">
                  <button 
                    v-for="tag in styleTags" 
                    :key="tag" 
                    class="style-tag"
                    @click="appendTag(tag)"
                    :disabled="isGenerating"
                  >
                    {{ tag }}
                  </button>
                </div>
              </div>

              <!-- 功能按钮 -->
              <div class="editor-actions">
                <button 
                  class="btn btn-regenerate" 
                  @click="regenerateCurrent"
                  :disabled="isGenerating"
                >
                  <span v-if="isGenerating && isPageGenerating(selectedPage?.page_number)" class="loading-spinner"></span>
                  <span v-else>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="btn-icon">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
                    </svg>
                    重新生成图片
                  </span>
                </button>
                
                <button 
                  class="btn btn-restore" 
                  @click="restoreDefaultPrompt"
                  :disabled="isGenerating"
                >
                  恢复默认提示词
                </button>
              </div>
              
              <div class="single-image-actions">
                <button
                  v-if="selectedPage?.image_url"
                  @click="downloadSingle"
                  class="btn btn-download-single"
                >
                  下载此图
                </button>
              </div>
            </div>
            </div>
          </transition>
        </div>

        <!-- 下方：小红书文案编辑区（始终显示） -->
        <div class="caption-editor-section">
          <h3 class="editor-subtitle">小红书文案</h3>
          <textarea
            v-model="globalCaption"
            class="caption-input"
            placeholder="编辑小红书文案..."
            :disabled="isGenerating"
          ></textarea>
          <button
            class="btn btn-save-caption"
            @click="saveGlobalCaption"
            :disabled="isGenerating"
          >
            保存文案
          </button>
        </div>
      </div>
    </div>
    
    <!-- 无大纲提示 -->
    <div v-if="!store.currentOutline && !isGenerating" class="empty-state">
      <p>暂无生成结果</p>
      <button @click="goHome" class="btn btn-primary">返回首页</button>
    </div>

    <!-- 图片预览模态框 -->
    <div v-if="previewUrl" class="image-modal" @click="closePreview">
      <div class="modal-content">
        <img :src="previewUrl" alt="预览图片" />
        <button class="close-btn" @click="closePreview">×</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../store'
import { generateImages, subscribeProgress, saveHistory, type ProgressData } from '../services/api'

const router = useRouter()
const store = useAppStore()

// 视图状态
const viewMode = ref<'grid' | 'single'>('grid')
const selectedPageIndex = ref<number>(0)
const editingPrompts = ref<Record<number, string>>({})
const initialPrompts = ref<Record<number, string>>({})
const editingCaptions = ref<Record<number, string>>({})
const previewUrl = ref('')

// 风格标签
const styleTags = ['#胶片感', '#ins风', '#韩系穿搭', '#美食特写', '#暖光滤镜', '#极简主义', '#高饱和度']

// 状态
const isGenerating = ref(false)
const generatingPages = ref<Set<number>>(new Set()) // 记录正在生成的页面
const error = ref('')
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

const selectedPage = computed(() => {
  if (!store.currentOutline) return null
  return store.currentOutline.pages[selectedPageIndex.value]
})

const currentEditingPrompt = computed({
  get: () => {
    if (!selectedPage.value) return ''
    // 优先显示编辑中的，否则显示 store 中的
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
    // 优先显示编辑中的，否则显示 store 中的
    return editingCaptions.value[selectedPageIndex.value] ?? selectedPage.value.xiaohongshu_content
  },
  set: (val: string) => {
    if (selectedPage.value) {
      editingCaptions.value[selectedPageIndex.value] = val
    }
  }
})

const globalCaption = computed({
  get: () => {
    if (!store.currentOutline) return ''
    // 使用第一页的文案作为全局文案
    return store.currentOutline.pages[0]?.xiaohongshu_content || ''
  },
  set: (val: string) => {
    if (store.currentOutline && store.currentOutline.pages[0]) {
      store.currentOutline.pages[0].xiaohongshu_content = val
    }
  }
})

// 方法
const enterSingleView = (index: number) => {
  selectedPageIndex.value = index
  viewMode.value = 'single'
  // 初始化编辑提示词
  if (editingPrompts.value[index] === undefined && store.currentOutline) {
    editingPrompts.value[index] = store.currentOutline.pages[index].description
  }
}

const exitSingleView = () => {
  viewMode.value = 'grid'
}

const openPreview = (url: string) => {
  previewUrl.value = url
}

const closePreview = () => {
  previewUrl.value = ''
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

// 重新生成当前图片
const regenerateCurrent = async () => {
  if (!selectedPage.value || !store.currentOutline) return
  
  // 更新 store 中的描述为当前编辑的描述
  const pageIndex = selectedPageIndex.value
  store.currentOutline.pages[pageIndex].description = currentEditingPrompt.value
  
  try {
    isGenerating.value = true
    generatingPages.value.add(selectedPage.value.page_number)
    error.value = ''
    
    // 构造只包含当前页面的请求
    const singlePage = store.currentOutline.pages[pageIndex]
    
    const response = await generateImages({
      task_id: store.currentOutline.task_id, // 复用 task_id 或后端生成新的
      pages: [singlePage],
      topic: store.currentOutline.topic,
      reference_image: store.referenceImage || undefined,
      generator_type: selectedGenerator.value,
      image_model_config: store.imageModelConfig,
      image_generation_config: store.imageGenerationConfig  // 新增：图片配置
    })
    
    if (response.success) {
      subscribeToProgress(response.task_id)
    } else {
      throw new Error('启动生成任务失败')
    }
  } catch (err: any) {
    error.value = err.message || '生成失败，请重试'
    isGenerating.value = false
    generatingPages.value.delete(selectedPage.value.page_number)
  }
}

// 批量生成（初始加载时）
const startGeneration = async () => {
  if (!store.currentOutline) {
    error.value = '没有可用的大纲'
    return
  }
  
  try {
    isGenerating.value = true
    // 标记所有没有图片的页面为生成中
    store.currentOutline.pages.forEach(p => {
      if (!p.image_url) generatingPages.value.add(p.page_number)
    })
    
    error.value = ''
    
    const generatorType = store.imageModelConfig.generatorType || selectedGenerator.value
    
    const response = await generateImages({
      task_id: store.currentOutline.task_id,
      pages: store.currentOutline.pages,
      topic: store.currentOutline.topic,
      reference_image: store.referenceImage || undefined,
      generator_type: generatorType,
      image_model_config: store.imageModelConfig,
      image_generation_config: store.imageGenerationConfig  // 新增：图片配置
    })
    
    if (response.success) {
      subscribeToProgress(response.task_id)
    } else {
      throw new Error('启动生成任务失败')
    }
  } catch (err: any) {
    error.value = err.message || '生成失败，请重试'
    isGenerating.value = false
    generatingPages.value.clear()
    console.error('Generation error:', err)
  }
}

const subscribeToProgress = (taskId: string) => {
  if (eventSource.value) {
    eventSource.value.close()
  }

  eventSource.value = subscribeProgress(
    taskId,
    (data: ProgressData) => {
      console.log('收到进度更新:', data)
      
      if (!data.done) {
        progressData.value = {
          ...progressData.value,
          ...data,
          images: data.images || progressData.value.images || [],
          failed_pages: data.failed_pages || progressData.value.failed_pages || []
        }
        
        // 实时更新图片
        if (data.images && data.images.length > 0) {
          data.images.forEach(img => {
            const page = store.currentOutline!.pages.find(p => p.page_number === img.page_number)
            if (page) {
              page.image_url = img.url
              generatingPages.value.delete(page.page_number)
            }
          })
        }
        
        // 处理失败
        if (data.failed_pages && data.failed_pages.length > 0) {
           data.failed_pages.forEach(fail => {
             generatingPages.value.delete(fail.page_number)
           })
        }
      }
    },
    (err: Error) => {
      error.value = err.message
      isGenerating.value = false
      generatingPages.value.clear()
    },
    async () => {
      isGenerating.value = false
      generatingPages.value.clear()
      
      // 最终同步
      if (store.currentOutline && progressData.value.images) {
        progressData.value.images.forEach(img => {
          const page = store.currentOutline!.pages.find(p => p.page_number === img.page_number)
          if (page) page.image_url = img.url
        })
        
        // 保存历史
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

const retry = () => {
  error.value = ''
  startGeneration()
}

const goHome = () => {
  router.push('/')
}

const downloadSingle = async () => {
  if (!selectedPage.value?.image_url) return
  
  try {
    // 使用 fetch 获取图片数据
    const response = await fetch(selectedPage.value.image_url)
    const blob = await response.blob()
    
    // 创建 blob URL
    const blobUrl = URL.createObjectURL(blob)
    
    // 创建下载链接
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = `page_${selectedPage.value.page_number}.jpg`
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    URL.revokeObjectURL(blobUrl)
  } catch (err) {
    console.error('下载图片失败:', err)
  }
}

const downloadAll = async () => {
  if (!store.currentOutline) return
  
  for (const page of store.currentOutline.pages) {
    if (page.image_url) {
      try {
        // 使用 fetch 获取图片数据
        const response = await fetch(page.image_url)
        const blob = await response.blob()
        
        // 创建 blob URL
        const blobUrl = URL.createObjectURL(blob)
        
        // 创建下载链接
        const link = document.createElement('a')
        link.href = blobUrl
        link.download = `page_${page.page_number}.jpg`
        document.body.appendChild(link)
        link.click()
        
        // 清理
        document.body.removeChild(link)
        URL.revokeObjectURL(blobUrl)
        
        // 添加延迟避免浏览器阻止多个下载
        await new Promise(resolve => setTimeout(resolve, 100))
      } catch (err) {
        console.error(`下载图片 ${page.page_number} 失败:`, err)
      }
    }
  }
}

const saveCaption = () => {
  if (!selectedPage.value || !store.currentOutline) return
  
  // 更新 store 中的文案
  const pageIndex = selectedPageIndex.value
  store.currentOutline.pages[pageIndex].xiaohongshu_content = currentEditingCaption.value
  
  // 可以添加保存成功提示
  console.log('文案已保存')
}

const saveGlobalCaption = () => {
  if (!store.currentOutline) return
  
  // 更新第一页的文案（显示在预览区）
  if (store.currentOutline.pages[0]) {
    store.currentOutline.pages[0].xiaohongshu_content = globalCaption.value
  }
  
  console.log('全局文案已保存')
}

// 生命周期
onMounted(() => {
  if (!store.currentOutline) {
    router.push('/')
    return
  }

  // 备份初始提示词和文案
  store.currentOutline.pages.forEach((page, index) => {
    initialPrompts.value[index] = page.description
    editingPrompts.value[index] = page.description
    editingCaptions.value[index] = page.xiaohongshu_content || ''
  })

  // 检查是否需要自动生成
  const hasAnyImages = store.currentOutline.pages.some(p => !!p.image_url)
  if (!hasAnyImages) {
    startGeneration()
  }
})

onUnmounted(() => {
  if (eventSource.value) {
    eventSource.value.close()
  }
})
</script>

<style scoped>
.result-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 布局容器 */
.split-layout {
  display: flex;
  gap: 40px;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 0 20px;
  overflow: hidden;
}

/* 左侧预览区 */
.preview-section {
  flex-shrink: 0;
  position: relative;
}

.phone-mockup {
  width: 375px;
  height: 812px; /* iPhone X 尺寸 */
  background: #fff;
  border-radius: 50px;
  box-shadow:
    0 0 0 12px #1a1a1a,
    0 0 0 14px #333,
    0 20px 50px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  position: relative;
  z-index: 1;
}

/* 手机内部可滚动容器 */
.phone-content-scroll {
  position: absolute;
  top: 54px; /* 状态栏高度 */
  bottom: 80px; /* 互动栏高度 */
  left: 0;
  right: 0;
  overflow-y: auto;
  overflow-x: hidden;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch; /* iOS平滑滚动 */
  pointer-events: auto; /* 确保可以滚动 */
}

/* 内容包装器 - 包含图片和文案 */
.content-wrapper {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  pointer-events: auto; /* 确保可以滚动 */
}

/* 自定义滚动条样式 */
.phone-content-scroll::-webkit-scrollbar {
  width: 4px;
}

.phone-content-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.phone-content-scroll::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 2px;
}

.phone-content-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* 刘海 */
.notch {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 160px;
  height: 30px;
  background: #1a1a1a;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
  z-index: 20;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.notch .camera {
  width: 10px;
  height: 10px;
  background: #0d0d0d;
  border-radius: 50%;
  box-shadow: inset 0 0 2px rgba(255,255,255,0.1);
}

.notch .speaker {
  width: 40px;
  height: 4px;
  background: #2a2a2a;
  border-radius: 2px;
}

/* 侧边按钮 */
.side-btn {
  position: absolute;
  background: #1a1a1a;
  border-radius: 2px;
}

.side-btn.volume-up {
  left: -14px;
  top: 120px;
  width: 3px;
  height: 40px;
}

.side-btn.volume-down {
  left: -14px;
  top: 170px;
  width: 3px;
  height: 40px;
}

.side-btn.power {
  right: -14px;
  top: 140px;
  width: 3px;
  height: 60px;
}

/* 底部 Home 条 */
.home-indicator {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 120px;
  height: 5px;
  background: #000;
  border-radius: 3px;
  z-index: 20;
  opacity: 0.3;
}

/* 固定状态栏 */
.status-bar-fixed {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 54px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 24px 0;
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

.status-icons .icon {
  width: 16px;
  height: 16px;
}

/* 导航返回按钮 - 更明显的样式 */
.nav-back-btn {
  position: absolute; /* 改回absolute，相对于内容定位 */
  top: 8px; /* 紧贴图片顶部 */
  left: 12px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.75); /* 更深的背景 */
  border: 2px solid rgba(255, 255, 255, 0.9); /* 更明显的边框 */
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 25; /* 提高层级确保可见 */
  backdrop-filter: blur(8px);
  transition: all 0.2s;
  pointer-events: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3); /* 添加阴影增加可见度 */
}

.nav-back-btn:hover {
  background: rgba(255, 255, 255, 0.95);
  color: #000;
  transform: scale(1.1);
  border-color: #fff;
}

.nav-back-btn:active {
  transform: scale(0.95);
}

.nav-back-btn svg {
  width: 22px;
  height: 22px;
  margin-right: 2px; /* 视觉修正 */
}

/* 图片容器 - 正方形9宫格 */
.preview-images-container {
  flex-shrink: 0;
  width: 100%;
  aspect-ratio: 1 / 1; /* 保持9宫格为正方形 */
  background: #000;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  pointer-events: auto; /* 确保可以接收触摸事件 */
}

.preview-images-container.is-single {
  aspect-ratio: 1 / 1;
}

/* 网格视图 - 9宫格正方形 */
.grid-view {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 2px;
  width: 100%;
  height: 100%;
  padding: 0;
  background: #fff;
}

.grid-item {
  position: relative;
  cursor: pointer;
  overflow: hidden;
  background: #f5f5f5;
  transition: transform 0.2s ease;
  aspect-ratio: 1 / 1; /* 确保每个格子是正方形 */
}

.grid-item:hover {
  z-index: 1;
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.image-wrapper {
  width: 100%;
  height: 100%;
}

.grid-image {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 填充满每个格子 */
}

.grid-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
  font-weight: 500;
}

/* 单张视图 */
.single-view {
  width: 100%;
  height: 100%;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: zoom-out;
  pointer-events: auto; /* 确保可以点击退出 */
}

.single-image-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 8px;
  pointer-events: none; /* 图片包装器不拦截点击 */
}

.single-image {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 保持比例 */
  cursor: zoom-in;
  pointer-events: auto; /* 图片本身可以点击放大预览 */
}

.zoom-hint {
  position: absolute;
  bottom: 16px;
  right: 16px;
  background: rgba(0,0,0,0.5);
  color: white;
  padding: 8px;
  border-radius: 50%;
  pointer-events: none; /* 提示图标不拦截点击 */
  opacity: 0;
  transition: opacity 0.3s;
}

.single-image-wrapper:hover .zoom-hint {
  opacity: 1;
}

.zoom-hint svg {
  width: 20px;
  height: 20px;
}

.single-placeholder {
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  pointer-events: auto; /* 占位符可以点击退出 */
}

/* 底部文案 */
.preview-caption-container {
  flex-shrink: 0;
  background: #fff;
  padding: 20px 16px;
  min-height: 200px; /* 至少200px高度 */
}

.caption-content {
  margin-bottom: 12px;
}

.caption-title {
  font-size: 17px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: #333;
  letter-spacing: -0.3px;
}

.caption-text {
  font-size: 14px;
  line-height: 1.8;
  color: #555;
  white-space: pre-wrap;
  margin: 0;
  word-break: break-word;
}

/* 固定互动栏 */
.interaction-bar-fixed {
  position: absolute;
  bottom: 13px; /* 留出Home条的空间 */
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
  z-index: 20;
}

.interaction-input {
  flex: 1;
  background: #f5f5f5;
  border-radius: 16px;
  padding: 8px 12px;
  font-size: 12px;
  color: #999;
}

.interaction-icons {
  display: flex;
  gap: 16px;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  color: #333;
}

.icon-item svg {
  width: 20px;
  height: 20px;
}

.icon-item span {
  font-size: 10px;
  color: #666;
}

/* 右侧操作区 */
.editor-section {
  flex: 1;
  min-width: 500px;
  max-width: 650px;
  background: #fff;
  border-radius: 32px; /* 与手机圆角呼应 */
  padding: 32px;
  height: 812px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow: 0 10px 40px rgba(0,0,0,0.05); /* 柔和阴影 */
  border: 1px solid rgba(0,0,0,0.02);
}

/* 默认提示 */
.editor-hint {
  text-align: center;
  color: #999;
}

.hint-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  color: #ddd;
}

.hint-icon svg {
  width: 100%;
  height: 100%;
}

.global-actions {
  margin-top: 32px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}

/* 编辑模块 */
.editor-module {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.editor-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.editor-title {
  font-size: 16px;
  color: #ff2442;
  margin: 0;
  font-weight: 600;
}

.close-editor-btn {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: background 0.2s;
}

.close-editor-btn:hover {
  background: #f5f5f5;
  color: #666;
}

.close-editor-btn svg {
  width: 20px;
  height: 20px;
}

.prompt-input {
  width: 100%;
  height: 150px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 8px;
  resize: vertical;
  font-family: Consolas, monospace;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
  margin-bottom: 16px;
  transition: border-color 0.2s;
}

.prompt-input:focus {
  outline: none;
  border-color: #ff2442;
}

/* 标签 */
.tags-container {
  margin-bottom: 24px;
}

.tags-label {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
  display: block;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.style-tag {
  background: #f5f5f5;
  border: none;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.style-tag:hover {
  background: #e6e6e6;
  color: #333;
}

/* 按钮 */
.editor-actions {
  display: flex;
  gap: 12px;
  margin-top: auto;
}

.btn {
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-regenerate {
  background: linear-gradient(to right, #ff2442, #ff6b81);
  color: white;
  padding: 10px 24px;
  border-radius: 24px;
  flex: 1;
}

.btn-regenerate:hover:not(:disabled) {
  transform: scale(1.03);
  box-shadow: 0 4px 12px rgba(255, 36, 66, 0.3);
}

.btn-regenerate:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-restore {
  background: white;
  border: 1px solid #ddd;
  color: #666;
  padding: 10px 24px;
  border-radius: 24px;
}

.btn-restore:hover:not(:disabled) {
  border-color: #999;
  color: #333;
}

.btn-icon {
  width: 18px;
  height: 18px;
  margin-right: 6px;
}

.btn-download-single {
  margin-top: 12px;
  width: 100%;
  text-align: center;
  color: #ff2442;
  font-size: 13px;
  text-decoration: none;
  padding: 8px;
  display: block;
}

.btn-download-single:hover {
  text-decoration: underline;
}

/* 小红书文案编辑区 */
.caption-editor-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

.editor-subtitle {
  font-size: 16px;
  color: #ff2442;
  margin: 0 0 12px 0;
  font-weight: 600;
}

.caption-input {
  width: 100%;
  min-height: 180px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 8px;
  resize: vertical;
  font-size: 14px;
  line-height: 1.8;
  color: #333;
  margin-bottom: 12px;
  transition: border-color 0.2s;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.caption-input:focus {
  outline: none;
  border-color: #ff2442;
}

.btn-save-caption {
  width: 100%;
  background: linear-gradient(to right, #ff2442, #ff6b81);
  color: white;
  padding: 10px 24px;
  border-radius: 24px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-save-caption:hover:not(:disabled) {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(255, 36, 66, 0.3);
}

.btn-save-caption:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 加载动画 */
.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-dots span {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #ff2442;
  border-radius: 50%;
  margin: 0 4px;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.3s ease;
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* 响应式适配 */
@media (max-width: 900px) {
  .split-layout {
    flex-direction: column;
    align-items: center;
  }

  .preview-section {
    width: 100%;
    display: flex;
    justify-content: center;
  }

  .editor-section {
    width: 100%;
    min-width: auto;
    max-width: 100%; /* 移动端全宽 */
    margin-top: 24px;
  }
}

/* 模态框样式 */
.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  cursor: zoom-out;
}

.modal-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.modal-content img {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 4px;
}

.close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: none;
  border: none;
  color: white;
  font-size: 2rem;
  cursor: pointer;
}
</style>
