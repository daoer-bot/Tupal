<template>
  <div class="creation-home">
    <!-- 全新创作区域 -->
    <section class="new-creation-section glass-panel-heavy">
      <div class="section-header">
        <div class="header-content">
          <h2 class="section-title">
            <Sparkles :size="24" class="title-icon" />
            开始创作
          </h2>
          <p class="section-subtitle">描述你的创意想法，AI 将为你生成精美的小红书图文</p>
        </div>
      </div>
      
      <div class="creation-form">
        <!-- 主题输入 -->
        <div class="form-group">
          <label class="form-label">创作主题</label>
          <MentionInput
            v-model="topic"
            placeholder="描述你的创作主题和想法...（输入 @ 可引用素材）"
            :multiline="true"
            :rows="4"
            input-class="topic-input"
          />
        </div>
        
        <!-- 风格选择 -->
        <div class="form-group">
          <label class="form-label">内容风格</label>
          <div class="style-options">
            <button
              v-for="style in styleOptions"
              :key="style.value"
              class="style-btn"
              :class="{ active: selectedStyle === style.value }"
              @click="selectedStyle = style.value"
            >
              <span class="style-icon">{{ style.icon }}</span>
              <span class="style-name">{{ style.label }}</span>
            </button>
          </div>
        </div>
        
        <!-- 图片配置 -->
        <div class="form-row">
          <div class="form-group flex-1">
            <label class="form-label">图片清晰度</label>
            <div class="config-buttons">
              <button
                v-for="q in qualityOptions"
                :key="q.value"
                @click="selectQuality(q.value)"
                class="config-btn"
                :class="{ active: imageConfig.quality === q.value }"
              >
                {{ q.label }}
              </button>
            </div>
          </div>
          
          <div class="form-group flex-1">
            <label class="form-label">图片比例</label>
            <div class="config-buttons">
              <button
                v-for="ratio in ratioOptions"
                :key="ratio.value"
                @click="selectRatio(ratio.value)"
                class="config-btn"
                :class="{ active: imageConfig.aspectRatio === ratio.value }"
              >
                {{ ratio.label }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- 开始创作按钮 -->
        <div class="form-actions">
          <button 
            class="btn-create"
            :disabled="!canCreate || isCreating"
            @click="startCreation"
          >
            <span v-if="isCreating" class="loading-spinner"></span>
            <Sparkles v-else :size="20" />
            <span>{{ isCreating ? '准备中...' : '开始创作' }}</span>
          </button>
        </div>
      </div>
    </section>
    
    <!-- 模板区域 -->
    <section class="templates-section">
      <div class="section-header">
        <div class="header-content">
          <h2 class="section-title">
            <FileText :size="24" class="title-icon" />
            创作模板
          </h2>
          <p class="section-subtitle">选择模板快速开始，或从你的案例库中使用个人模板</p>
        </div>
        
        <!-- Tab 切换 -->
        <div class="template-tabs">
          <button
            v-for="tab in templateTabs"
            :key="tab.value"
            class="tab-btn"
            :class="{ active: activeTab === tab.value }"
            @click="activeTab = tab.value"
          >
            <component :is="tab.icon" :size="18" />
            <span>{{ tab.label }}</span>
            <span v-if="tab.count !== undefined" class="tab-count">{{ tab.count }}</span>
          </button>
        </div>
      </div>
      
      <!-- 模板网格 -->
      <div class="templates-content">
        <!-- 加载状态 -->
        <div v-if="loadingTemplates" class="loading-state">
          <div class="loading-spinner-large"></div>
          <p>加载模板中...</p>
        </div>
        
        <!-- 空状态 -->
        <div v-else-if="currentTemplates.length === 0" class="empty-state">
          <div class="empty-icon">
            <component :is="activeTab === 'official' ? Crown : Bookmark" :size="48" />
          </div>
          <h3>{{ activeTab === 'official' ? '暂无官方模板' : '暂无个人模板' }}</h3>
          <p v-if="activeTab === 'personal'">
            你可以在「资产与作品」的案例库中将优秀案例设为模板
          </p>
        </div>
        
        <!-- 模板网格 -->
        <div v-else class="templates-grid">
          <TemplateCard
            v-for="template in currentTemplates"
            :key="template.id"
            :template="template"
            @use="handleUseTemplate"
            @click="handleTemplateClick"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Sparkles, FileText, Crown, Bookmark } from 'lucide-vue-next'
import { useAppStore } from '../../store'
import MentionInput from '../../components/MentionInput.vue'
import TemplateCard from '../../components/TemplateCard.vue'
import templateApi, { type Template } from '../../services/templateApi'
import { generateOutline } from '../../services/api'

const router = useRouter()
const store = useAppStore()

// 创作表单状态
const topic = ref('')
const selectedStyle = ref('xiaohongshu')
const isCreating = ref(false)

// 图片配置
const imageConfig = ref({
  quality: store.imageGenerationConfig.quality,
  aspectRatio: store.imageGenerationConfig.aspectRatio
})

// 模板状态
const activeTab = ref<'official' | 'personal'>('official')
const loadingTemplates = ref(false)
const officialTemplates = ref<Template[]>([])
const personalTemplates = ref<Template[]>([])

// 风格选项
const styleOptions = [
  { value: 'xiaohongshu', label: '小红书风', icon: '📕' },
  { value: 'professional', label: '专业风', icon: '💼' },
  { value: 'casual', label: '轻松风', icon: '😊' },
  { value: 'creative', label: '创意风', icon: '🎨' }
]

// 图片配置选项
const qualityOptions = [
  { label: '1K', value: '1k' as const },
  { label: '2K', value: '2k' as const },
  { label: '4K', value: '4k' as const }
]

const ratioOptions = [
  { label: '3:4', value: '3:4' as const },
  { label: '4:3', value: '4:3' as const },
  { label: '1:1', value: '1:1' as const },
  { label: '9:16', value: '9:16' as const },
  { label: '16:9', value: '16:9' as const }
]

// Tab 配置
const templateTabs = computed(() => [
  { 
    value: 'official' as const, 
    label: '官方模板', 
    icon: Crown,
    count: officialTemplates.value.length 
  },
  { 
    value: 'personal' as const, 
    label: '我的模板', 
    icon: Bookmark,
    count: personalTemplates.value.length 
  }
])

// 当前显示的模板
const currentTemplates = computed(() => {
  return activeTab.value === 'official' ? officialTemplates.value : personalTemplates.value
})

// 是否可以创作
const canCreate = computed(() => {
  return topic.value.trim().length > 0
})

// 选择清晰度
const selectQuality = (quality: '1k' | '2k' | '4k') => {
  imageConfig.value.quality = quality
  store.setImageGenerationConfig({
    ...store.imageGenerationConfig,
    quality
  })
}

// 选择比例
const selectRatio = (aspectRatio: '4:3' | '3:4' | '16:9' | '9:16' | '2:3' | '3:2' | '1:1' | '4:5' | '5:4' | '21:9') => {
  imageConfig.value.aspectRatio = aspectRatio
  store.setImageGenerationConfig({
    ...store.imageGenerationConfig,
    aspectRatio
  })
}

// 开始创作
const startCreation = async () => {
  if (!canCreate.value || isCreating.value) return
  
  isCreating.value = true
  
  try {
    // 生成大纲
    const response = await generateOutline({
      topic: topic.value,
      generator_type: store.textModelConfig.generatorType,
      text_model_config: store.textModelConfig
    })
    
    if (response.success && response.data) {
      store.setOutline(response.data)
      // 跳转到编辑器页面
      router.push('/creation/editor')
    }
  } catch (error) {
    console.error('创建失败:', error)
  } finally {
    isCreating.value = false
  }
}

// 使用模板
const handleUseTemplate = async (template: Template) => {
  isCreating.value = true
  
  try {
    const response = await templateApi.useTemplate(template.id, topic.value || template.name)
    
    if (response.success && response.data) {
      store.setOutline(response.data)
      router.push('/creation/editor')
    }
  } catch (error) {
    console.error('使用模板失败:', error)
  } finally {
    isCreating.value = false
  }
}

// 点击模板查看详情
const handleTemplateClick = (template: Template) => {
  // 可以实现模板预览功能
  console.log('查看模板:', template)
}

// 加载模板
const loadTemplates = async () => {
  loadingTemplates.value = true
  
  try {
    // 并行加载官方模板和个人模板
    const [officialRes, personalRes] = await Promise.all([
      templateApi.getOfficialTemplates({ page_size: 20 }),
      templateApi.getPersonalTemplates({ page_size: 20 })
    ])
    
    if (officialRes.success && officialRes.data) {
      officialTemplates.value = officialRes.data.items
    }
    
    if (personalRes.success && personalRes.data) {
      personalTemplates.value = personalRes.data.items
    }
  } catch (error) {
    console.error('加载模板失败:', error)
    // 使用模拟数据作为后备
    officialTemplates.value = getMockOfficialTemplates()
    personalTemplates.value = []
  } finally {
    loadingTemplates.value = false
  }
}

// 模拟官方模板数据（后备）
const getMockOfficialTemplates = (): Template[] => [
  {
    id: 'tpl-1',
    name: '穿搭分享',
    description: '时尚穿搭推荐模板，适合服装搭配、OOTD分享',
    type: 'official',
    tags: ['穿搭', '时尚', 'OOTD'],
    created_at: new Date().toISOString()
  },
  {
    id: 'tpl-2',
    name: '美食探店',
    description: '餐厅美食推荐模板，适合探店打卡、美食分享',
    type: 'official',
    tags: ['美食', '探店', '打卡'],
    created_at: new Date().toISOString()
  },
  {
    id: 'tpl-3',
    name: '旅行攻略',
    description: '旅游景点介绍模板，适合旅行记录、攻略分享',
    type: 'official',
    tags: ['旅行', '攻略', '景点'],
    created_at: new Date().toISOString()
  },
  {
    id: 'tpl-4',
    name: '好物推荐',
    description: '产品种草模板，适合好物分享、测评推荐',
    type: 'official',
    tags: ['好物', '种草', '测评'],
    created_at: new Date().toISOString()
  },
  {
    id: 'tpl-5',
    name: '护肤心得',
    description: '护肤美妆分享模板，适合护肤技巧、产品推荐',
    type: 'official',
    tags: ['护肤', '美妆', '技巧'],
    created_at: new Date().toISOString()
  },
  {
    id: 'tpl-6',
    name: '健身打卡',
    description: '健身运动记录模板，适合健身打卡、运动分享',
    type: 'official',
    tags: ['健身', '运动', '打卡'],
    created_at: new Date().toISOString()
  }
]

// 监听 Tab 切换
watch(activeTab, () => {
  // 可以在这里添加切换动画或其他逻辑
})

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.creation-home {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  padding: 1rem 0;
}

/* 通用区域样式 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-content {
  flex: 1;
  min-width: 200px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

.title-icon {
  color: #6366f1;
}

.section-subtitle {
  margin: 0;
  font-size: 0.9375rem;
  color: #64748b;
}

/* 全新创作区域 */
.new-creation-section {
  padding: 2rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
  border-radius: 24px;
}

.creation-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group.flex-1 {
  flex: 1;
}

.form-row {
  display: flex;
  gap: 2rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 主题输入 */
.topic-input {
  min-height: 100px !important;
  border: 2px solid rgba(99, 102, 241, 0.2) !important;
  border-radius: 12px !important;
  background: rgba(255, 255, 255, 0.6) !important;
  font-size: 15px !important;
  transition: all 0.3s !important;
}

.topic-input:focus {
  border-color: #6366f1 !important;
  background: rgba(255, 255, 255, 0.9) !important;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1) !important;
}

/* 风格选择 */
.style-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.style-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: rgba(255, 255, 255, 0.6);
  border: 2px solid rgba(99, 102, 241, 0.15);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.style-btn:hover {
  border-color: rgba(99, 102, 241, 0.4);
  background: rgba(255, 255, 255, 0.9);
}

.style-btn.active {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
  border-color: #6366f1;
}

.style-icon {
  font-size: 1.25rem;
}

.style-name {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #1e293b;
}

/* 配置按钮 */
.config-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
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
}

.config-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
}

.config-btn.active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* 创作按钮 */
.form-actions {
  display: flex;
  justify-content: center;
  padding-top: 0.5rem;
}

.btn-create {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem 3rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
}

.btn-create:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
}

.btn-create:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 模板区域 */
.templates-section {
  display: flex;
  flex-direction: column;
}

/* Tab 切换 */
.template-tabs {
  display: flex;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.5);
  padding: 0.375rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #64748b;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.6);
  color: #1e293b;
}

.tab-btn.active {
  background: white;
  color: #6366f1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.tab-count {
  padding: 2px 8px;
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
  font-size: 12px;
  font-weight: 600;
  border-radius: 10px;
}

.tab-btn.active .tab-count {
  background: rgba(99, 102, 241, 0.15);
}

/* 模板内容区 */
.templates-content {
  min-height: 300px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #64748b;
}

.loading-spinner,
.loading-spinner-large {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(99, 102, 241, 0.2);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-spinner-large {
  width: 40px;
  height: 40px;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
  border-radius: 20px;
  margin-bottom: 1.5rem;
  color: #6366f1;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

.empty-state p {
  margin: 0;
  font-size: 0.9375rem;
  color: #64748b;
  max-width: 300px;
}

/* 模板网格 */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

/* 响应式 */
@media (max-width: 768px) {
  .new-creation-section {
    padding: 1.5rem;
  }
  
  .form-row {
    flex-direction: column;
    gap: 1rem;
  }
  
  .section-header {
    flex-direction: column;
  }
  
  .template-tabs {
    width: 100%;
    justify-content: center;
  }
  
  .templates-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
  
  .btn-create {
    width: 100%;
    padding: 1rem 2rem;
  }
}

@media (max-width: 480px) {
  .style-options {
    flex-direction: column;
  }
  
  .style-btn {
    width: 100%;
    justify-content: center;
  }
  
  .templates-grid {
    grid-template-columns: 1fr;
  }
}
</style>