/**
 * Toast 通知服务
 * 用于全局显示轻量级消息提示
 */

import { createApp, h } from 'vue'
import Toast, { type ToastProps } from '@/components/Toast.vue'

interface ToastInstance {
  container: HTMLDivElement
  close: () => void
}

const instances: ToastInstance[] = []
const MAX_TOASTS = 3

/**
 * 显示toast通知
 */
export function showToast(options: ToastProps): ToastInstance {
  // 如果超过最大数量,移除最旧的toast
  if (instances.length >= MAX_TOASTS) {
    const oldest = instances.shift()
    if (oldest) oldest.close()
  }

  const container = document.createElement('div')
  document.body.appendChild(container)

  const app = createApp({
    render() {
      return h(Toast, {
        ...options,
        onClose: () => {
          app.unmount()
          document.body.removeChild(container)
          const index = instances.findIndex(i => i.container === container)
          if (index > -1) instances.splice(index, 1)
        }
      })
    }
  })

  app.mount(container)

  const instance: ToastInstance = {
    container,
    close: () => {
      app.unmount()
      document.body.removeChild(container)
      const index = instances.findIndex(i => i.container === container)
      if (index > -1) instances.splice(index, 1)
    }
  }

  instances.push(instance)
  return instance
}

/**
 * 便捷方法
 */
export const toast = {
  success(message: string, duration = 3000) {
    return showToast({ message, type: 'success', duration })
  },

  error(message: string, duration = 4000) {
    return showToast({ message, type: 'error', duration })
  },

  warning(message: string, duration = 3500) {
    return showToast({ message, type: 'warning', duration })
  },

  info(message: string, duration = 3000) {
    return showToast({ message, type: 'info', duration })
  }
}

export default toast
