import { createApp } from 'vue'
import Toast from '../components/Toast.vue'

class ToastService {
  constructor() {
    this.toasts = []
  }

  show(message, type = 'info', options = {}) {
    const defaultOptions = {
      duration: 3000,
      closable: true
    }
    
    const toastOptions = { ...defaultOptions, ...options }
    
    const toastApp = createApp(Toast, {
      message,
      type,
      ...toastOptions,
      onClose: () => {
        this.remove(toastApp)
      }
    })
    
    const container = document.createElement('div')
    document.body.appendChild(container)
    toastApp.mount(container)
    
    toastApp._container = container
    this.toasts.push(toastApp)
    
    return toastApp
  }

  success(message, options = {}) {
    return this.show(message, 'success', options)
  }

  error(message, options = {}) {
    return this.show(message, 'error', options)
  }

  warning(message, options = {}) {
    return this.show(message, 'warning', options)
  }

  info(message, options = {}) {
    return this.show(message, 'info', options)
  }

  remove(toastApp) {
    const index = this.toasts.indexOf(toastApp)
    if (index > -1) {
      this.toasts.splice(index, 1)
    }
    
    // 延迟移除DOM元素，让动画完成
    setTimeout(() => {
      if (toastApp._container && toastApp._container.parentNode) {
        toastApp._container.parentNode.removeChild(toastApp._container)
      }
      toastApp.unmount()
    }, 300)
  }

  clear() {
    this.toasts.forEach(toast => {
      this.remove(toast)
    })
    this.toasts = []
  }
}

// 创建全局实例
const toast = new ToastService()

// 为了兼容现有的alert调用，提供一个全局函数
window.showToast = toast.show.bind(toast)
window.showSuccessToast = toast.success.bind(toast)
window.showErrorToast = toast.error.bind(toast)
window.showWarningToast = toast.warning.bind(toast)
window.showInfoToast = toast.info.bind(toast)

export default toast 