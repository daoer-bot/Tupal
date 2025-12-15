<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click="closeModal">
        <div class="glass-panel modal-container" @click.stop>
          <div class="modal-header">
            <div class="header-title">
              <h2>模型配置</h2>
              <p>管理你的 AI 模型参数</p>
            </div>
            <button class="close-btn" @click="closeModal">✕</button>
          </div>
          
          <div class="modal-body">
            <!-- 文本模型配置 -->
            <div class="config-section">
              <div class="section-header">
                <div class="section-info">
                  <span class="section-icon">📝</span>
                  <h3>文本模型</h3>
                  <span class="badge">生成大纲</span>
                </div>
                <button class="btn-sm btn-outline" @click="addTextModel">
                  + 添加模型
                </button>
              </div>
              
              <div v-if="textModels.length === 0" class="empty-config">
                暂无配置，点击上方按钮添加
              </div>
              
              <div v-else class="models-grid">
                <div
                  v-for="(model, index) in textModels"
                  :key="index"
                  class="model-card"
                  :class="{ active: selectedTextIndex === index }"
                  @click="selectedTextIndex = index"
                >
                  <div class="card-header">
                    <input
                      v-model="model.name"
                      placeholder="配置名称"
                      class="model-name-input"
                      @click.stop
                    />
                    <div class="card-actions">
                      <span v-if="selectedTextIndex === index" class="active-tag">当前使用</span>
                      <button class="delete-btn" @click.stop="deleteTextModel(index)">🗑️</button>
                    </div>
                  </div>
                  
                  <div class="card-body">
                    <div class="form-group">
                      <label>API URL</label>
                      <input v-model="model.url" placeholder="https://api.openai.com" class="glass-input" @click.stop />
                      <p class="field-hint">
                        <span class="endpoint-label">实际调用地址: </span>
                        <code class="endpoint-url">{{ getActualEndpoint(model) }}</code>
                      </p>
                    </div>
                    
                    <div class="form-group">
                      <label>API Key</label>
                      <input v-model="model.apiKey" type="password" placeholder="sk-..." class="glass-input" @click.stop />
                    </div>
                    
                    <div class="form-group">
                      <label>模型名称</label>
                      <input v-model="model.model" placeholder="gpt-4" class="glass-input" @click.stop />
                      <p class="field-hint">
                        文本模型使用 OpenAI 格式，支持: gpt-4, gpt-3.5-turbo, claude-3-opus 等
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 图片模型配置 -->
            <div class="config-section">
              <div class="section-header">
                <div class="section-info">
                  <span class="section-icon">🎨</span>
                  <h3>图片模型</h3>
                  <span class="badge">生成图片</span>
                </div>
                <button class="btn-sm btn-outline" @click="addImageModel">
                  + 添加模型
                </button>
              </div>
              
              <div v-if="imageModels.length === 0" class="empty-config">
                暂无配置，点击上方按钮添加
              </div>
              
              <div v-else class="models-grid">
                <div
                  v-for="(model, index) in imageModels"
                  :key="index"
                  class="model-card"
                  :class="{ active: selectedImageIndex === index }"
                  @click="selectedImageIndex = index"
                >
                  <div class="card-header">
                    <input
                      v-model="model.name"
                      placeholder="配置名称"
                      class="model-name-input"
                      @click.stop
                    />
                    <div class="card-actions">
                      <span v-if="selectedImageIndex === index" class="active-tag">当前使用</span>
                      <button class="delete-btn" @click.stop="deleteImageModel(index)">🗑️</button>
                    </div>
                  </div>
                  
                  <div class="card-body">
                    <div class="form-group">
                      <label>接口规则</label>
                      <select v-model="model.apiFormat" class="glass-input" @click.stop>
                        <option value="chat">OpenAI-Chat 格式（推荐）</option>
                        <option value="generations">OpenAI-DALL·E 格式</option>
                        <option value="official">Gemini 原生格式</option>
                      </select>
                      <p class="field-hint">
                        • OpenAI-Chat: /v1/chat/completions 端点<br>
                        • OpenAI-DALL·E 格式: /v1/images/generations 端点<br>
                        • Gemini 原生格式: 原生 generateContent 端点
                      </p>
                    </div>
                    
                    <div class="form-group">
                      <label>API URL</label>
                      <input v-model="model.url" placeholder="API 地址" class="glass-input" @click.stop />
                      <p class="field-hint">
                        <span class="endpoint-label">实际调用地址: </span>
                        <code class="endpoint-url">{{ getActualEndpoint(model) }}</code>
                      </p>
                    </div>
                    
                    <div class="form-group">
                      <label>API Key</label>
                      <input v-model="model.apiKey" type="password" placeholder="API Key" class="glass-input" @click.stop />
                    </div>
                    
                    <div class="form-group">
                      <label>模型名称</label>
                      <input v-model="model.model" placeholder="nano-banana" class="glass-input" @click.stop />
                      <p class="field-hint">
                        <span v-if="model.apiFormat === 'chat'">常用模型: gemini-2.0-flash-exp-image-generation, gpt-4, claude-3 等</span>
                        <span v-else-if="model.apiFormat === 'generations'">常用模型: dall-e-3, dall-e-2, flux-pro 等</span>
                        <span v-else>常用模型: gemini-2.0-flash-exp, gemini-pro-vision 等</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 小红书配置 -->
            <div class="config-section">
              <div class="section-header">
                <div class="section-info">
                  <span class="section-icon">📕</span>
                  <h3>小红书</h3>
                  <span class="badge xhs-badge">数据采集</span>
                </div>
                <div class="xhs-status" :class="xhsClientStatus">
                  <span v-if="xhsClientStatus === 'connected'" class="status-dot connected"></span>
                  <span v-else-if="xhsClientStatus === 'error'" class="status-dot error"></span>
                  <span v-else class="status-dot idle"></span>
                  <span class="status-text">{{ xhsStatusMessage || '未配置' }}</span>
                </div>
              </div>
              
              <div class="xhs-config-card">
                <div class="card-body">
                  <div class="form-group">
                    <label>Cookie <span class="required">*</span></label>
                    <div class="cookie-input-wrapper">
                      <textarea
                        v-model="xhsConfig.cookie"
                        placeholder="请输入小红书 Cookie（必填）&#10;获取方式：点击下方「扫码获取」按钮，或手动从浏览器复制"
                        class="glass-input cookie-input"
                        rows="3"
                      ></textarea>
                      <button
                        class="btn btn-qr-login"
                        @click="startQrLogin"
                        :disabled="qrLoginState.loading || qrLoginState.status === 'scanning'"
                      >
                        <span v-if="qrLoginState.loading">⏳</span>
                        <span v-else-if="qrLoginState.status === 'scanning'">📱</span>
                        <span v-else>📷</span>
                        {{ qrLoginButtonText }}
                      </button>
                    </div>
                    <p class="field-hint">
                      <span class="warning-text">⚠️ Cookie 包含敏感信息，请勿泄露给他人</span>
                    </p>
                  </div>
                  
                  <!-- 二维码登录区域 -->
                  <div v-if="qrLoginState.showQrCode" class="qr-login-section">
                    <div class="qr-code-container">
                      <div v-if="qrLoginState.qrCodeUrl" class="qr-code-wrapper">
                        <img :src="qrLoginState.qrCodeUrl" alt="小红书登录二维码" class="qr-code-image" />
                        <div v-if="qrLoginState.status === 'scanned'" class="qr-scanned-overlay">
                          <span class="scanned-icon">✓</span>
                          <span class="scanned-text">已扫码，请在手机上确认</span>
                        </div>
                        <div v-if="qrLoginState.status === 'expired'" class="qr-expired-overlay">
                          <span class="expired-icon">⏰</span>
                          <span class="expired-text">二维码已过期</span>
                          <button class="btn btn-sm btn-refresh" @click="startQrLogin">刷新</button>
                        </div>
                      </div>
                      <div v-else class="qr-loading">
                        <div class="loading-spinner"></div>
                        <span>正在生成二维码...</span>
                      </div>
                    </div>
                    <div class="qr-login-info">
                      <p class="qr-title">📱 使用小红书 App 扫码登录</p>
                      <p class="qr-steps">
                        1. 打开小红书 App<br>
                        2. 点击「我」→ 右上角设置图标<br>
                        3. 选择「扫一扫」扫描二维码<br>
                        4. 在手机上确认登录
                      </p>
                      <div class="qr-status" :class="qrLoginState.status">
                        <span class="status-icon">{{ qrStatusIcon }}</span>
                        <span class="status-message">{{ qrLoginState.message }}</span>
                      </div>
                      <button class="btn btn-sm btn-cancel" @click="cancelQrLogin">取消登录</button>
                    </div>
                  </div>
                  
                  <div class="form-row">
                    <div class="form-group flex-1">
                      <label>超时时间（秒）</label>
                      <input
                        v-model.number="xhsConfig.timeout"
                        type="number"
                        min="1"
                        max="60"
                        placeholder="10"
                        class="glass-input"
                      />
                    </div>
                    
                    <div class="form-group flex-2">
                      <label>代理地址（可选）</label>
                      <input
                        v-model="xhsConfig.proxy"
                        placeholder="http://127.0.0.1:7890"
                        class="glass-input"
                      />
                    </div>
                  </div>
                  
                  <div class="form-group">
                    <label>User-Agent（可选）</label>
                    <input
                      v-model="xhsConfig.userAgent"
                      placeholder="留空使用默认值"
                      class="glass-input"
                    />
                    <p class="field-hint">
                      自定义请求的 User-Agent，一般无需修改
                    </p>
                  </div>
                  
                  <div class="xhs-actions">
                    <button class="btn btn-outline" @click="testXhsConnection" :disabled="!xhsConfig.cookie">
                      🔗 测试连接
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeModal">取消</button>
            <button class="btn btn-primary" @click="saveConfig">保存配置</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

interface ModelConfig {
  name: string
  url: string
  apiKey: string
  model: string
  generatorType: string
  apiFormat?: string // 仅用于图片模型
}

interface XhsConfig {
  cookie: string
  userAgent: string
  timeout: number
  proxy: string
}

// 计算实际的接口地址（根据选择的格式动态变化）
const getActualEndpoint = (model: ModelConfig): string => {
  if (!model.url) {
    return '请先填写 API URL'
  }
  
  let baseUrl = model.url.trim().replace(/\/+$/, '') // 移除末尾的斜杠
  
  // 文本模型（OpenAI 格式）
  if (model.generatorType === 'openai') {
    // 如果 URL 不包含 /v1，自动添加
    if (!baseUrl.endsWith('/v1')) {
      baseUrl = `${baseUrl}/v1`
    }
    return `${baseUrl}/chat/completions`
  }
  
  // 图像模型
  if (model.apiFormat === 'chat') {
    // OpenAI-Chat 格式: /v1/chat/completions
    return `${baseUrl}/v1/chat/completions`
  } else if (model.apiFormat === 'generations') {
    // OpenAI-DALL·E 格式: /v1/images/generations
    return `${baseUrl}/v1/images/generations`
  } else if (model.apiFormat === 'official') {
    // Gemini 原生格式: /v1beta/models/{model}:generateContent
    const modelName = model.model || 'gemini-2.0-flash-exp'
    return `${baseUrl}/v1beta/models/${modelName}:generateContent`
  }
  
  return baseUrl
}

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
  save: [textModels: ModelConfig[], imageModels: ModelConfig[], selectedTextIndex: number, selectedImageIndex: number]
}>()

const textModels = ref<ModelConfig[]>([])
const imageModels = ref<ModelConfig[]>([])
const selectedTextIndex = ref(0)
const selectedImageIndex = ref(0)

// 小红书配置
const xhsConfig = ref<XhsConfig>({
  cookie: '',
  userAgent: '',
  timeout: 10,
  proxy: ''
})
const xhsClientStatus = ref<'idle' | 'connected' | 'error'>('idle')
const xhsStatusMessage = ref('')

// 二维码登录状态
interface QrLoginState {
  loading: boolean
  showQrCode: boolean
  qrCodeUrl: string
  sessionId: string
  status: 'idle' | 'waiting' | 'scanning' | 'scanned' | 'success' | 'expired' | 'failed' | 'cancelled'
  message: string
  pollingTimer: number | null
}

const qrLoginState = ref<QrLoginState>({
  loading: false,
  showQrCode: false,
  qrCodeUrl: '',
  sessionId: '',
  status: 'idle',
  message: '',
  pollingTimer: null
})

// 计算属性：二维码登录按钮文字
const qrLoginButtonText = computed(() => {
  if (qrLoginState.value.loading) return '准备中...'
  if (qrLoginState.value.status === 'scanning' || qrLoginState.value.status === 'scanned') return '扫码中'
  return '扫码获取'
})

// 计算属性：二维码状态图标
const qrStatusIcon = computed(() => {
  switch (qrLoginState.value.status) {
    case 'waiting': return '⏳'
    case 'scanning': return '📱'
    case 'scanned': return '✓'
    case 'success': return '🎉'
    case 'expired': return '⏰'
    case 'failed': return '❌'
    case 'cancelled': return '🚫'
    default: return '📷'
  }
})

// 开始二维码登录
const startQrLogin = async () => {
  // 先检查 Playwright 是否已安装
  qrLoginState.value.loading = true
  qrLoginState.value.message = '正在检查环境...'
  
  try {
    const checkResponse = await fetch('/api/xiaohongshu/login/check')
    const checkData = await checkResponse.json()
    
    if (!checkData.success || !checkData.data.available) {
      qrLoginState.value.loading = false
      qrLoginState.value.message = '请先安装 Playwright：pip install playwright && playwright install chromium'
      alert('扫码登录需要 Playwright 支持，请在后端执行：\npip install playwright\nplaywright install chromium')
      return
    }
    
    // 启动登录会话
    qrLoginState.value.message = '正在启动浏览器...'
    const startResponse = await fetch('/api/xiaohongshu/login/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ headless: true, timeout: 180 })
    })
    
    const startData = await startResponse.json()
    
    if (!startData.success) {
      qrLoginState.value.loading = false
      qrLoginState.value.message = startData.error || '启动登录失败'
      return
    }
    
    // 保存会话 ID 并显示二维码
    qrLoginState.value.sessionId = startData.data.session_id
    qrLoginState.value.qrCodeUrl = startData.data.qr_code_url
    qrLoginState.value.showQrCode = true
    qrLoginState.value.loading = false
    qrLoginState.value.status = 'waiting'
    qrLoginState.value.message = '请使用小红书 App 扫描二维码'
    
    // 开始轮询状态
    startPollingLoginStatus()
    
  } catch (error) {
    qrLoginState.value.loading = false
    qrLoginState.value.message = '网络错误，请重试'
    console.error('QR login error:', error)
  }
}

// 轮询登录状态
const startPollingLoginStatus = () => {
  // 清除之前的定时器
  if (qrLoginState.value.pollingTimer) {
    clearInterval(qrLoginState.value.pollingTimer)
  }
  
  qrLoginState.value.pollingTimer = window.setInterval(async () => {
    if (!qrLoginState.value.sessionId) {
      stopPolling()
      return
    }
    
    try {
      const response = await fetch(`/api/xiaohongshu/login/status/${qrLoginState.value.sessionId}`)
      const data = await response.json()
      
      if (!data.success) {
        qrLoginState.value.message = data.error || '获取状态失败'
        return
      }
      
      const status = data.data.status
      
      switch (status) {
        case 'waiting_scan':
          qrLoginState.value.status = 'waiting'
          qrLoginState.value.message = '等待扫码...'
          break
        case 'scanned':
          qrLoginState.value.status = 'scanned'
          qrLoginState.value.message = '已扫码，请在手机上确认登录'
          break
        case 'success':
          qrLoginState.value.status = 'success'
          qrLoginState.value.message = '登录成功！'
          // 获取 Cookie 并填充
          if (data.data.cookie) {
            xhsConfig.value.cookie = data.data.cookie
            // 自动测试连接
            setTimeout(() => {
              testXhsConnection()
            }, 500)
          }
          // 停止轮询并清理
          stopPolling()
          setTimeout(() => {
            qrLoginState.value.showQrCode = false
            resetQrLoginState()
          }, 2000)
          break
        case 'failed':
          qrLoginState.value.status = 'failed'
          qrLoginState.value.message = data.data.error || '登录失败'
          stopPolling()
          break
        case 'timeout':
          qrLoginState.value.status = 'expired'
          qrLoginState.value.message = '二维码已过期，请刷新'
          stopPolling()
          break
        case 'cancelled':
          qrLoginState.value.status = 'cancelled'
          qrLoginState.value.message = '登录已取消'
          stopPolling()
          break
      }
    } catch (error) {
      console.error('Polling error:', error)
    }
  }, 2000) // 每 2 秒轮询一次
}

// 停止轮询
const stopPolling = () => {
  if (qrLoginState.value.pollingTimer) {
    clearInterval(qrLoginState.value.pollingTimer)
    qrLoginState.value.pollingTimer = null
  }
}

// 取消二维码登录
const cancelQrLogin = async () => {
  if (qrLoginState.value.sessionId) {
    try {
      await fetch(`/api/xiaohongshu/login/cancel/${qrLoginState.value.sessionId}`, {
        method: 'POST'
      })
    } catch (error) {
      console.error('Cancel login error:', error)
    }
  }
  
  stopPolling()
  qrLoginState.value.showQrCode = false
  resetQrLoginState()
}

// 重置二维码登录状态
const resetQrLoginState = () => {
  qrLoginState.value = {
    loading: false,
    showQrCode: false,
    qrCodeUrl: '',
    sessionId: '',
    status: 'idle',
    message: '',
    pollingTimer: null
  }
}

// 加载配置
const loadConfig = () => {
  const savedTextModels = localStorage.getItem('textModels')
  const savedImageModels = localStorage.getItem('imageModels')
  const savedSelectedTextIndex = localStorage.getItem('selectedTextIndex')
  const savedSelectedImageIndex = localStorage.getItem('selectedImageIndex')
  const savedXhsConfig = localStorage.getItem('xhsConfig')
  
  if (savedTextModels) {
    textModels.value = JSON.parse(savedTextModels)
  }
  if (savedImageModels) {
    imageModels.value = JSON.parse(savedImageModels)
  }
  if (savedSelectedTextIndex) {
    selectedTextIndex.value = parseInt(savedSelectedTextIndex)
  }
  if (savedSelectedImageIndex) {
    selectedImageIndex.value = parseInt(savedSelectedImageIndex)
  }
  if (savedXhsConfig) {
    xhsConfig.value = JSON.parse(savedXhsConfig)
    // 检查小红书连接状态
    if (xhsConfig.value.cookie) {
      checkXhsStatus()
    }
  }
}

// 检查小红书连接状态
const checkXhsStatus = async () => {
  if (!xhsConfig.value.cookie) {
    xhsClientStatus.value = 'idle'
    xhsStatusMessage.value = ''
    return
  }
  
  try {
    const response = await fetch('/api/xiaohongshu/client', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cookie: xhsConfig.value.cookie,
        user_agent: xhsConfig.value.userAgent || undefined,
        timeout: xhsConfig.value.timeout || 10,
        proxies: xhsConfig.value.proxy || undefined
      })
    })
    
    const data = await response.json()
    if (data.success) {
      xhsClientStatus.value = 'connected'
      xhsStatusMessage.value = `已连接 (ID: ${data.data.client_id.substring(0, 8)}...)`
    } else {
      xhsClientStatus.value = 'error'
      xhsStatusMessage.value = data.error || '连接失败'
    }
  } catch (error) {
    xhsClientStatus.value = 'error'
    xhsStatusMessage.value = '网络错误'
  }
}

// 测试小红书连接
const testXhsConnection = async () => {
  xhsClientStatus.value = 'idle'
  xhsStatusMessage.value = '正在测试连接...'
  await checkXhsStatus()
}

// 监听 show 变化，打开时加载配置
watch(() => props.show, (newVal) => {
  if (newVal) {
    loadConfig()
  }
})

const addTextModel = () => {
  textModels.value.push({
    name: `文本模型 ${textModels.value.length + 1}`,
    url: 'https://api.openai.com',
    apiKey: '',
    model: 'gpt-4',
    generatorType: 'openai'
  })
}

const addImageModel = () => {
  imageModels.value.push({
    name: `图片模型 ${imageModels.value.length + 1}`,
    url: '',
    apiKey: '',
    model: 'nano-banana',
    generatorType: 'image_api',  // 明确设置为 image_api
    apiFormat: 'chat'  // 默认使用 chat 格式
  })
}

// 监听 apiFormat 变化，自动更新对应的默认模型
watch(() => imageModels.value.map(m => m.apiFormat), (newFormats, oldFormats) => {
  imageModels.value.forEach((model, index) => {
    // 只有当格式发生变化时才更新模型
    if (newFormats[index] !== oldFormats[index]) {
      if (model.apiFormat === 'official') {
        // Gemini 原生格式
        model.model = 'gemini-3-pro-image-preview'
      } else if (model.apiFormat === 'chat') {
        // OpenAI-Chat 格式
        model.model = 'nano-banana'
      } else if (model.apiFormat === 'generations') {
        // OpenAI-DALL·E 格式
        model.model = 'nano-banana'
      }
    }
  })
}, { deep: true })

const deleteTextModel = (index: number) => {
  if (confirm('确定要删除这个配置吗？')) {
    textModels.value.splice(index, 1)
    if (selectedTextIndex.value >= textModels.value.length) {
      selectedTextIndex.value = Math.max(0, textModels.value.length - 1)
    }
  }
}

const deleteImageModel = (index: number) => {
  if (confirm('确定要删除这个配置吗？')) {
    imageModels.value.splice(index, 1)
    if (selectedImageIndex.value >= imageModels.value.length) {
      selectedImageIndex.value = Math.max(0, imageModels.value.length - 1)
    }
  }
}

const closeModal = () => {
  emit('close')
}

const saveConfig = () => {
  // 保存到 localStorage
  localStorage.setItem('textModels', JSON.stringify(textModels.value))
  localStorage.setItem('imageModels', JSON.stringify(imageModels.value))
  localStorage.setItem('selectedTextIndex', selectedTextIndex.value.toString())
  localStorage.setItem('selectedImageIndex', selectedImageIndex.value.toString())
  localStorage.setItem('xhsConfig', JSON.stringify(xhsConfig.value))
  
  // 触发保存事件
  emit('save', textModels.value, imageModels.value, selectedTextIndex.value, selectedImageIndex.value)
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  border-radius: 24px;
  width: 100%;
  max-width: 900px;
  height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.9);
}

.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: transparent;
}

.header-title h2 {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
  color: var(--text-primary);
  font-weight: 700;
}

.header-title p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.2rem;
  color: var(--text-tertiary);
  cursor: pointer;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--text-primary);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  background: transparent;
}

.config-section {
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  padding-bottom: 1rem;
}

.section-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-icon {
  font-size: 1.5rem;
  filter: none;
}

.section-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
  font-weight: 700;
}

.badge {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  border: none;
}

.btn-outline {
  background: white;
  border: 1px solid rgba(0,0,0,0.1);
  color: var(--text-secondary);
  border-radius: 8px;
  font-size: 0.85rem;
  padding: 0.4rem 1rem;
  transition: all 0.2s;
  cursor: pointer;
}

.btn-outline:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.model-card {
  background: white;
  border: 1px solid rgba(0,0,0,0.05);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.model-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.05);
}

.model-card.active {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-color);
}

.card-header {
  padding: 1rem;
  border-bottom: 1px solid rgba(0,0,0,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
}

.model-name-input {
  border: none;
  background: transparent;
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-primary);
  width: 100%;
  padding: 0.25rem 0;
  border-bottom: 1px solid transparent;
}

.model-name-input:focus {
  outline: none;
  border-bottom-color: var(--primary-color);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.active-tag {
  font-size: 0.7rem;
  color: white;
  font-weight: 600;
  background: var(--primary-color);
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
}

.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.3;
  transition: opacity 0.2s;
  padding: 0.25rem;
  filter: none;
}

.delete-btn:hover {
  opacity: 1;
}

.card-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.glass-input {
  padding: 0.75rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  color: var(--text-primary);
  width: 100%;
}

.glass-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.modal-footer {
  padding: 1.5rem 2rem;
  border-top: 1px solid rgba(0,0,0,0.05);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  background: transparent;
}

.btn {
  padding: 0.6rem 1.5rem;
  font-size: 0.9rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 600;
}

.btn-secondary {
  background: transparent;
  border: 1px solid rgba(0,0,0,0.1);
  color: var(--text-secondary);
}

.btn-secondary:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.btn-primary {
  background: var(--primary-color);
  border: 1px solid var(--primary-color);
  color: white;
}

.btn-primary:hover {
  filter: brightness(1.1);
}

.empty-config {
  text-align: center;
  padding: 4rem;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  color: var(--text-tertiary);
}

.field-hint {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-tertiary);
  line-height: 1.5;
}

.endpoint-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.endpoint-url {
  background: #f1f5f9;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: var(--text-secondary);
  word-break: break-all;
  display: inline-block;
  margin-top: 0.25rem;
  border: 1px solid rgba(0,0,0,0.05);
}

.warning-text {
  color: #d97706;
  font-weight: 500;
}

.info-text {
  color: #2563eb;
  font-weight: 500;
}

/* 小红书配置样式 */
.xhs-badge {
  background: rgba(255, 45, 85, 0.1);
  color: #ff2d55;
}

.xhs-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.connected {
  background: #10b981;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.5);
}

.status-dot.error {
  background: #ef4444;
  box-shadow: 0 0 6px rgba(239, 68, 68, 0.5);
}

.status-dot.idle {
  background: #9ca3af;
}

.status-text {
  color: var(--text-secondary);
}

.xhs-status.connected .status-text {
  color: #10b981;
}

.xhs-status.error .status-text {
  color: #ef4444;
}

.xhs-config-card {
  background: white;
  border: 1px solid rgba(0,0,0,0.05);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.cookie-input {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  resize: vertical;
  min-height: 80px;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.flex-1 {
  flex: 1;
}

.flex-2 {
  flex: 2;
}

.required {
  color: #ef4444;
}

.xhs-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(0,0,0,0.05);
  margin-top: 0.5rem;
}

.btn-outline:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Cookie 输入区域样式 */
.cookie-input-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.cookie-input-wrapper .cookie-input {
  flex: 1;
}

.btn-qr-login {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #ff2d55 0%, #ff6b8a 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  min-width: 80px;
}

.btn-qr-login:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 45, 85, 0.3);
}

.btn-qr-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-qr-login span:first-child {
  font-size: 1.25rem;
}

/* 二维码登录区域样式 */
.qr-login-section {
  display: flex;
  gap: 1.5rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #fff5f7 0%, #fff 100%);
  border: 1px solid rgba(255, 45, 85, 0.1);
  border-radius: 12px;
  margin-top: 1rem;
}

.qr-code-container {
  flex-shrink: 0;
}

.qr-code-wrapper {
  position: relative;
  width: 180px;
  height: 180px;
  background: white;
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.qr-code-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.qr-scanned-overlay,
.qr-expired-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  gap: 0.5rem;
}

.scanned-icon {
  font-size: 2.5rem;
  color: #10b981;
}

.scanned-text {
  font-size: 0.8rem;
  color: #10b981;
  font-weight: 600;
  text-align: center;
  padding: 0 0.5rem;
}

.expired-icon {
  font-size: 2rem;
  color: #f59e0b;
}

.expired-text {
  font-size: 0.8rem;
  color: #f59e0b;
  font-weight: 600;
}

.btn-refresh {
  margin-top: 0.5rem;
  padding: 0.4rem 1rem;
  background: #ff2d55;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.75rem;
  cursor: pointer;
}

.btn-refresh:hover {
  background: #e6294d;
}

.qr-loading {
  width: 180px;
  height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #ff2d55;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.qr-loading span {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.qr-login-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.qr-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.qr-steps {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.8;
  margin: 0;
  padding-left: 0.5rem;
}

.qr-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-radius: 8px;
  margin-top: auto;
}

.qr-status .status-icon {
  font-size: 1.25rem;
}

.qr-status .status-message {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.qr-status.waiting {
  background: #fef3c7;
}

.qr-status.waiting .status-message {
  color: #d97706;
}

.qr-status.scanned {
  background: #d1fae5;
}

.qr-status.scanned .status-message {
  color: #059669;
}

.qr-status.success {
  background: #d1fae5;
}

.qr-status.success .status-message {
  color: #059669;
}

.qr-status.expired,
.qr-status.failed {
  background: #fee2e2;
}

.qr-status.expired .status-message,
.qr-status.failed .status-message {
  color: #dc2626;
}

.btn-cancel {
  align-self: flex-start;
  padding: 0.4rem 1rem;
  background: transparent;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  font-size: 0.75rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  border-color: #ef4444;
  color: #ef4444;
}

.btn-sm {
  padding: 0.35rem 0.75rem;
  font-size: 0.75rem;
}

/* 动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95) translateY(10px);
}
</style>