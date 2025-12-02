import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Page {
  page_number: number
  title: string
  description: string
  image_url?: string
  xiaohongshu_content?: string
}

export interface Outline {
  task_id: string
  topic: string
  pages: Page[]
}

export interface ModelConfig {
  url: string
  apiKey: string
  model: string
  generatorType?: string  // 新增：生成器类型
  apiFormat?: string  // 新增：图片模型的接口规则（chat/generations/official）
}

// 图片生成配置
export interface ImageGenerationConfig {
  quality: '1k' | '2k' | '4k'  // 清晰度
  aspectRatio: '4:3' | '3:4' | '16:9' | '9:16' | '2:3' | '3:2' | '1:1' | '4:5' | '5:4' | '21:9'  // 宽高比
}

export const useAppStore = defineStore('app', () => {
  // 当前大纲
  const currentOutline = ref<Outline | null>(null)
  
  // 生成进度
  const progress = ref(0)
  const isGenerating = ref(false)
  const progressMessage = ref('')
  
  // 参考图片
  const referenceImage = ref<string | null>(null)
  
  // 模型配置
  const textModelConfig = ref<ModelConfig>({
    url: '',
    apiKey: '',
    model: '',
    generatorType: 'openai'  // 默认使用 openai
  })
  
  const imageModelConfig = ref<ModelConfig>({
    url: '',
    apiKey: '',
    model: '',
    generatorType: 'image_api'  // 默认使用 image_api
  })
  
  // 图片生成配置
  const imageGenerationConfig = ref<ImageGenerationConfig>({
    quality: '2k',  // 默认 2K
    aspectRatio: '3:4'  // 默认 3:4（小红书常用竖版）
  })
  
  // 设置大纲
  const setOutline = (outline: Outline) => {
    currentOutline.value = outline
  }
  
  // 更新进度
  const updateProgress = (value: number, message: string = '') => {
    progress.value = value
    progressMessage.value = message
  }
  
  // 设置生成状态
  const setGenerating = (status: boolean) => {
    isGenerating.value = status
  }
  
  // 设置参考图片
  const setReferenceImage = (url: string | null) => {
    referenceImage.value = url
  }
  
  // 设置语言模型配置
  const setTextModelConfig = (config: ModelConfig) => {
    textModelConfig.value = config
  }
  
  // 设置图片模型配置
  const setImageModelConfig = (config: ModelConfig) => {
    imageModelConfig.value = config
  }
  
  // 设置图片生成配置
  const setImageGenerationConfig = (config: ImageGenerationConfig) => {
    imageGenerationConfig.value = config
  }
  
  // 重置状态
  const reset = () => {
    currentOutline.value = null
    progress.value = 0
    isGenerating.value = false
    progressMessage.value = ''
  }
  
  return {
    currentOutline,
    progress,
    isGenerating,
    progressMessage,
    referenceImage,
    textModelConfig,
    imageModelConfig,
    imageGenerationConfig,
    setOutline,
    updateProgress,
    setGenerating,
    setReferenceImage,
    setTextModelConfig,
    setImageModelConfig,
    setImageGenerationConfig,
    reset
  }
})