import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Page {
  page_number: number
  title: string
  description: string
  image_url?: string
}

export interface Outline {
  task_id: string
  topic: string
  pages: Page[]
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
    setOutline,
    updateProgress,
    setGenerating,
    setReferenceImage,
    reset
  }
})