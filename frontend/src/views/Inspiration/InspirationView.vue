
<template>
  <div class="inspiration-view">
    <!-- Hero 区域 -->
    <section class="hero glass-panel animate-fade-in">
      <div class="hero-copy">
        <p class="eyebrow">Inspiration Hub · 灵感工作室</p>
        <h1>每天十分钟，刷新创作雷达</h1>
        <p class="hero-desc">
          我们从社交舆情、消费热点与视觉趋势中精选最具潜力的灵感线索，帮你快速建立今日创作方向。
        </p>

        <div class="hero-metrics">
          <div v-for="metric in heroMetricCards" :key="metric.label" class="metric">
            <span class="metric-value">{{ metric.value }}</span>
            <span class="metric-label">{{ metric.label }}</span>
          </div>
        </div>

        <div class="hero-actions">
          <router-link to="/workspace/cases" class="btn btn-primary">前往灵感收藏</router-link>
          <button class="btn ghost-btn" @click="handleRefreshAll" :disabled="insightLoading">
            {{ insightLoading ? '刷新中...' : '刷新灵感' }}
          </button>
          <span v-if="lastUpdatedText" class="update-hint">更新于 {{ lastUpdatedText }}</span>
        </div>
      </div>
      <div class="hero-visual">
        <template v-if="heroHighlights.length">
          <div
            v-for="(highlight, index) in heroHighlights"
            :key="highlight.id"
            :class="getBubbleClass(index)"
          >
            <strong>{{ highlight.title }}</strong>
            <span>{{ highlight.metric }}</span>
          </div>
        </template>
        <div v-else class="hero-placeholder">数据加载中...</div>
      </div>
    </section>

    <!-- 小红书灵感区域 -->
    <section class="xhs-section animate-fade-in">
      <div class="section-header">
        <div>
          <p class="section-eyebrow">小红书灵感</p>
          <h2>热门内容 · 创作参考</h2>
        </div>
        <div class="section-actions">
          <div :class="['xhs-status-indicator', xhsConnected ? 'connected' : '']">
            <span class="status-dot"></span>
            <span>{{ xhsConnected ? '已连接' : '未连接' }}</span>
          </div>
        </div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="xhs-controls glass-panel" v-if="xhsConnected">
        <div class="search-box">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
          </svg>
          <input 
            v-model="xhsSearchKeyword"
            type="text"
            placeholder="搜索小红书内容..."
            @keyup.enter="handleXhsSearch"
          />
          <button 
            v-if="xhsSearchKeyword"
            class="clear-btn"
            @click="xhsSearchKeyword = ''"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="filter-tabs">
          <button 
            v-for="tab in xhsFeedTabs" 
            :key="tab.value"
            :class="['filter-tab', { active: xhsActiveTab === tab.value }]"
            @click="handleTabChange(tab.value)"
          >
            {{ tab.label }}
          </button>
        </div>

        <div class="sort-options" v-if="xhsActiveTab === 'search' && xhsSearchKeyword">
          <select v-model="xhsSearchSort" @change="handleXhsSearch">
            <option value="general">综合排序</option>
            <option value="popularity_descending">最热优先</option>
            <option value="time_descending">最新优先</option>
          </select>
          <select v-model="xhsSearchNoteType" @change="handleXhsSearch">
            <option value="0">全部类型</option>
            <option value="1">仅视频</option>
            <option value="2">仅图文</option>
          </select>
        </div>
      </div>

      <!-- 未连接提示 -->
      <div v-if="!xhsConnected" class="xhs-placeholder glass-panel">
        <div class="placeholder-icon">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
          </svg>
        </div>
        <h3>连接小红书获取更多灵感</h3>
        <p>配置小红书 Cookie 后，即可搜索热门笔记、浏览推荐内容。</p>
        <button class="btn btn-primary" @click="openConfigModal">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="btn-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          立即配置
        </button>
        <p class="hint-text">点击上方按钮打开配置，找到「小红书」区域进行设置</p>
      </div>

      <!-- 加载状态 -->
      <div v-else-if="xhsLoading" class="xhs-loading">
        <div class="loading-spinner large"></div>
        <p>正在加载小红书内容...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="xhsError" class="xhs-error glass-panel">
        <p>{{ xhsError }}</p>
        <button class="btn btn-secondary" @click="loadXhsContent">重试</button>
      </div>

      <!-- 笔记列表 -->
      <div v-else-if="xhsNotes.length > 0" class="xhs-notes-grid">
        <XhsNoteCard 
          v-for="note in xhsNotes" 
          :key="note.note_id"
          :note="note"
          @click="handleNoteClick"
          @collect="handleNoteCollect"
        />
      </div>

      <!-- 空状态 -->
      <div v-else class="xhs-empty glass-panel">
        <p>暂无内容，请尝试搜索或切换分类</p>
      </div>

      <!-- 加载更多 -->
      <div v-if="xhsConnected && xhsNotes.length > 0 && xhsHasMore" class="load-more">
        <button 
          class="btn btn-secondary"
          @click="loadMoreXhsContent"
          :disabled="xhsLoadingMore"
        >
          {{ xhsLoadingMore ? '加载中...' : '加载更多' }}
        </button>
      </div>
    </section>

    <!-- 实时信号区域 -->
    <section class="signals-section animate-fade-in">
      <div class="section-header">
        <div>
          <p class="section-eyebrow">今日灵感雷达</p>
          <h2>实时信号 · 连接灵感与数据</h2>
        </div>
        <p class="section-desc">每条信号都附带洞察提示，帮助你判断是否值得延伸为创作选题。</p>
      </div>

      <div v-if="insightLoading" class="signals-placeholder glass-panel">
        <div class="placeholder-row" v-for="i in 3" :key="i">
          <div class="placeholder-bar short"></div>
          <div class="placeholder-bar"></div>
          <div class="placeholder-tags"></div>
        </div>
      </div>
      <div v-else-if="insightError" class="state-card glass-panel">
        <p>{{ insightError }}</p>
        <button class="retry-btn" @click="handleRefreshAll">重试</button>
      </div>
      <div v-else-if="liveSignals.length === 0" class="state-card glass-panel">
        <p>暂无实时信号，稍后再试或刷新热榜。</p>
        <button class="retry-btn ghost" @click="handleRefreshAll">刷新</button>
      </div>
      <div v-else class="signals-grid">
        <article v-for="signal in liveSignals" :key="signal.id" class="signal-card glass-panel">
          <div class="signal-header">
            <span class="signal-badge">{{ signal.channel }}</span>
            <span class="signal-metric">{{ signal.metric }}</span>
          </div>
          <h3>{{ signal.title }}</h3>
          <p>{{ signal.description }}</p>
          <div class="signal-tags">
            <span v-for="tag in signal.tags" :key="`tag-${signal.id}-${tag}`">{{ tag }}</span>
          </div>
        </article>
      </div>
    </section>

    <!-- 精选案例区域 -->
    <section class="spotlight-section animate-fade-in">
      <div class="section-header">
        <div>
          <p class="section-eyebrow">灵感提案</p>
          <h2>编辑精选 · 案例拆解</h2>
        </div>
        <p class="section-desc">挑选值得跟进的内容方向，并附上潜在执行策略。</p>
      </div>

      <div v-if="insightLoading" class="spotlight-grid">
        <article v-for="i in 3" :key="`spot-skeleton-${i}`" class="spotlight-card glass-panel skeleton-card"></article>
      </div>
      <div v-else-if="curatedSpots.length === 0" class="state-card glass-panel">
        <p>正在整理精选案例，稍后自动更新。</p>
      </div>
      <div v-else class="spotlight-grid">
        <article v-for="spot in curatedSpots" :key="spot.title" class="spotlight-card glass-panel">
          <div class="spotlight-type">{{ spot.type }}</div>
          <h3>{{ spot.title }}</h3>
          <p class="spotlight-summary">{{ spot.summary }}</p>
          <p class="spotlight-insight">{{ spot.insight }}</p>
          <div class="spotlight-footer">
            <span>{{ spot.stat }}</span>
            <span>{{ spot.callout }}</span>
          </div>
        </article>
      </div>
    </section>

    <!-- 工作流区域 -->
    <section class="workflow-section glass-panel animate-fade-in">
      <div class="section-header compact">
        <div>
          <p class="section-eyebrow">灵感工作流</p>
          <h2>把灵感变成可执行计划</h2>
        </div>
        <p class="section-desc">跟随 4 个阶段将零散想法沉淀成可复用的创作资产。</p>
      </div>

      <div class="workflow-steps">
        <div v-for="step in workflowSteps" :key="step.title" class="workflow-step">
          <div class="step-icon">{{ step.icon }}</div>
          <div class="step-content">
            <p class="step-label">{{ step.label }}</p>
            <h3>{{ step.title }}</h3>
            <p>{{ step.detail }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 热榜区域 -->
    <section class="section-trending animate-fade-in">
      <div class="section-header">
        <div>
          <p class="section-eyebrow">热度雷达</p>
          <h2>平台热榜 · 实时更新</h2>
        </div>
        <p class="section-desc">追踪关键平台上的关注度变化，随时捕捉下一波热点。</p>
      </div>

      <div v-if="trendingLoading && sources.length === 0" class="loading-container glass-panel">
        <div class="loading-spinner large"></div>
        <p>正在加载热榜数据...</p>
      </div>

      <div v-else-if="trendingError" class="error-container glass-panel">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="error-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
        </svg>
        <p class="error-message">{{ trendingError }}</p>
        <button class="retry-btn" @click="loadSources">重试</button>
      </div>

      <div v-else class="trending-grid">
        <TrendingCard 
          v-for="source in sources" 
          :key="source.id" 
          :source="source"
        />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, inject } from 'vue'
import TrendingCard from '../../components/TrendingCard.vue'
import XhsNoteCard from '../../components/XhsNoteCard.vue'
import { getTrendingSources, getAllTrending, type TrendingSource, type TrendingResponse } from '../../services/trendingApi'
import { 
  createClient,
  searchNotes, 
  getHomeFeed,
  type XhsNote,
  type FeedType,
  type SearchSortType
} from '../../services/xhsApi'

interface LiveSignal {
  id: string
  channel: string
  metric: string
  title: string
  description: string
  tags: string[]
}

interface Spotlight {
  type: string
  title: string
  summary: string
  insight: string
  stat: string
  callout: string
}

interface XhsConfig {
  cookie: string
  userAgent: string
  timeout: number
  proxy: string
}

// 注入打开配置弹窗的方法（来自 App.vue）
const injectedOpenConfigModal = inject<() => void>('openConfigModal')

// 打开配置弹窗的方法
const openConfigModal = () => {
  if (injectedOpenConfigModal) {
    injectedOpenConfigModal()
  } else {
    window.dispatchEvent(new CustomEvent('open-config-modal'))
  }
}

// 小红书相关状态
const xhsClientId = ref<string | null>(null)
const xhsConnected = computed(() => !!xhsClientId.value)
const xhsLoading = ref(false)
const xhsLoadingMore = ref(false)
const xhsError = ref('')
const xhsNotes = ref<XhsNote[]>([])
const xhsHasMore = ref(false)
const xhsSearchKeyword = ref('')
const xhsActiveTab = ref<string>('recommend')
const xhsSearchSort = ref<SearchSortType>('general')
const xhsSearchNoteType = ref<string>('0')
const xhsPage = ref(1)

const xhsFeedTabs = [
  { label: '推荐', value: 'recommend' },
  { label: '穿搭', value: 'homefeed.fashion_v3' },
  { label: '美食', value: 'homefeed.food_v3' },
  { label: '美妆', value: 'homefeed.cosmetics_v3' },
  { label: '旅行', value: 'homefeed.travel_v3' },
  { label: '家居', value: 'homefeed.household_product_v3' },
  { label: '搜索', value: 'search' }
]

// 热榜相关状态
const liveSignals = ref<LiveSignal[]>([])
const curatedSpots = ref<Spotlight[]>([])
const workflowSteps = [
  { label: '01 LISTEN', title: '捕捉信号', detail: '实时收集全网热度、关键词与人群场景，形成灵感收件箱。', icon: '👂' },
  { label: '02 CLUSTER', title: '聚合主题', detail: '把相似线索聚成主题卡片，评估可行性与投入优先级。', icon: '🧩' },
  { label: '03 DESIGN', title: '生成提案', detail: '结合模板与案例拆解，输出脚本、视觉要求与素材清单。', icon: '🧠' },
  { label: '04 DEPLOY', title: '发布复盘', detail: '同步到灵感收藏与作品库，追踪表现并沉淀为可复用资产。', icon: '🚀' }
]

const sources = ref<TrendingSource[]>([])
const trendingLoading = ref(false)
const trendingError = ref('')
const insightLoading = ref(false)
const insightError = ref('')
const lastUpdatedAt = ref<Date | null>(null)

const sourceMap = computed(() => {
  const map: Record<string, TrendingSource> = {}
  sources.value.forEach(src => {
    map[src.id] = src
  })
  return map
})

const heroMetricCards = computed(() => [
  { label: '实时信号', value: liveSignals.value.length || '—' },
  { label: '小红书笔记', value: xhsNotes.value.length || '—' },
  { label: '活跃数据源', value: sources.value.length || '—' }
])

const heroHighlights = computed(() => liveSignals.value.slice(0, 3))
const lastUpdatedText = computed(() => lastUpdatedAt.value ? lastUpdatedAt.value.toLocaleTimeString() : '')
const bubbleClassList = ['bubble bubble-large', 'bubble bubble-medium', 'bubble bubble-small']
const getBubbleClass = (index: number) => bubbleClassList[index] || 'bubble bubble-medium'

const formatHotValue = (value?: string | number): string => {
  if (!value) return '热度飙升'
  const num = typeof value === 'string' ? parseInt(value) : value
  if (isNaN(num)) return String(value)
  if (num >= 100000000) return (num / 100000000).toFixed(1) + '亿热度'
  if (num >= 10000) return (num / 10000).toFixed(1) + '万热度'
  return `${num}热度`
}

const buildTags = (item: any): string[] => {
  const tags: string[] = []
  if (item.extra?.label) tags.push(item.extra.label)
  if (item.extra?.desc) {
    const words = item.extra.desc.split(/[#，、,]/).map((w: string) => w.trim()).filter(Boolean)
    tags.push(...words.slice(0, 2))
  }
  if (tags.length === 0) tags.push('热门话题')
  return [...new Set(tags)].slice(0, 3)
}

const itemStatText = (rankCount: number, hot?: string | number) => {
  const heat = formatHotValue(hot)
  return `${heat} · 覆盖 ${rankCount} 条趋势`
}

const generateInsights = (data: Record<string, TrendingResponse>) => {
  const signals: LiveSignal[] = []
  const spots: Spotlight[] = []

  Object.entries(data).forEach(([sourceId, response]) => {
    const sourceInfo = sourceMap.value[sourceId]
    const channelName = sourceInfo ? sourceInfo.name : `数据源 ${sourceId}`

    response.data.slice(0, 3).forEach((item, index) => {
      signals.push({
        id: `${sourceId}-${item.id}-${index}`,
        channel: `${channelName} · TOP${index + 1}`,
        metric: item.hot_value ? formatHotValue(item.hot_value) : `热度上升`,
        title: item.title,
        description: item.extra?.desc || '该话题热度持续攀升，适合快速跟进内容创作。',
        tags: buildTags(item)
      })
    })

    if (response.data.length > 0) {
      const topItem = response.data[0]
      spots.push({
        type: channelName,
        title: topItem.title,
        summary: topItem.extra?.desc || '该主题在目标人群中保持高互动，可延展为深度内容或活动玩法。',
        insight: topItem.extra?.label ? `关联标签：${topItem.extra.label}` : '建议结合品牌场景或节日节点延展。',
        stat: itemStatText(response.data.length, topItem.hot_value),
        callout: response.update_time ? `更新于 ${new Date(response.update_time).toLocaleTimeString()}` : '实时监控中'
      })
    }
  })

  liveSignals.value = signals.slice(0, 6)
  curatedSpots.value = spots.slice(0, 3)
}

// 从 localStorage 获取小红书配置
const getXhsConfig = (): XhsConfig | null => {
  const stored = localStorage.getItem('xhsConfig')
  if (!stored) return null
  
  try {
    const config = JSON.parse(stored)
    if (!config.cookie) return null
    return config
  } catch {
    return null
  }
}

// 初始化小红书客户端
const initXhsClient = async () => {
  const config = getXhsConfig()
  if (!config) {
    console.log('未配置小红书 Cookie，请在右上角配置中设置')
    return
  }
  
  try {
    const result = await createClient({
      cookie: config.cookie,
      user_agent: config.userAgent || undefined,
      timeout: config.timeout || 10,
      proxies: config.proxy || undefined
    })
    
    if (result.success && result.data) {
      xhsClientId.value = result.data.client_id
      loadXhsContent()
    }
  } catch (e) {
    console.log('创建小红书客户端失败:', e)
  }
}

// 监听 localStorage 变化（当用户在配置中保存后）
const handleStorageChange = (e: StorageEvent) => {
  if (e.key === 'xhsConfig') {
    xhsClientId.value = null
    xhsNotes.value = []
    initXhsClient()
  }
}

const loadXhsContent = async () => {
  if (!xhsClientId.value) return
  
  xhsLoading.value = true
  xhsError.value = ''
  xhsPage.value = 1
  
  try {
    if (xhsActiveTab.value === 'search' && xhsSearchKeyword.value) {
      await performSearch()
    } else {
      await loadFeed()
    }
  } catch (e: any) {
    xhsError.value = e.message || '加载失败'
    console.error('加载小红书内容失败:', e)
  } finally {
    xhsLoading.value = false
  }
}

const loadFeed = async () => {
  if (!xhsClientId.value) return
  
  const feedType = xhsActiveTab.value === 'recommend' 
    ? 'homefeed_recommend' 
    : xhsActiveTab.value as FeedType
  
  const result = await getHomeFeed(xhsClientId.value, feedType)
  
  if (result.success && result.data) {
    xhsNotes.value = result.data.items || []
    xhsHasMore.value = !!result.data.cursor
  } else {
    throw new Error(result.error || '加载推荐内容失败')
  }
}

const performSearch = async () => {
  if (!xhsClientId.value || !xhsSearchKeyword.value) return
  
  const result = await searchNotes(xhsClientId.value, xhsSearchKeyword.value, {
    page: xhsPage.value,
    page_size: 20,
    sort: xhsSearchSort.value,
    note_type: xhsSearchNoteType.value as any
  })
  
  if (result.success && result.data) {
    if (xhsPage.value === 1) {
      xhsNotes.value = result.data.items || []
    } else {
      xhsNotes.value = [...xhsNotes.value, ...(result.data.items || [])]
    }
    xhsHasMore.value = result.data.has_more
  } else {
    throw new Error(result.error || '搜索失败')
  }
}

const loadMoreXhsContent = async () => {
  if (!xhsClientId.value || xhsLoadingMore.value) return
  
  xhsLoadingMore.value = true
  xhsPage.value++
  
  try {
    if (xhsActiveTab.value === 'search' && xhsSearchKeyword.value) {
      await performSearch()
    } else {
      await loadFeed()
    }
  } catch (e: any) {
    console.error('加载更多失败:', e)
    xhsPage.value--
  } finally {
    xhsLoadingMore.value = false
  }
}

const handleTabChange = (tab: string) => {
  xhsActiveTab.value = tab
  if (tab !== 'search') {
    loadXhsContent()
  } else if (xhsSearchKeyword.value) {
    loadXhsContent()
  }
}

const handleXhsSearch = () => {
  if (!xhsSearchKeyword.value.trim()) return
  xhsActiveTab.value = 'search'
  loadXhsContent()
}

const handleNoteClick = (note: XhsNote) => {
  const url = `https://www.xiaohongshu.com/explore/${note.note_id}`
  window.open(url, '_blank')
}

const handleNoteCollect = (note: XhsNote) => {
  console.log('收藏笔记:', note)
  alert('功能开发中：将笔记收藏为创作素材')
}

// 热榜相关方法
const loadSources = async () => {
  trendingLoading.value = true
  trendingError.value = ''
  
  try {
    sources.value = await getTrendingSources()
  } catch (e: any) {
    trendingError.value = e.message || '加载数据源失败'
    console.error('加载数据源失败:', e)
  } finally {
    trendingLoading.value = false
  }
}

const refreshInsights = async (force = false) => {
  insightLoading.value = true
  insightError.value = ''
  try {
    const responses = await getAllTrending(force)
    generateInsights(responses)
    lastUpdatedAt.value = new Date()
  } catch (e: any) {
    insightError.value = e.message || '获取趋势洞察失败'
    console.error('获取趋势洞察失败:', e)
  } finally {
    insightLoading.value = false
  }
}

const handleRefreshAll = () => {
  refreshInsights(true)
}

onMounted(() => {
  loadSources()
  refreshInsights()
  initXhsClient()
  
  // 监听 storage 变化
  window.addEventListener('storage', handleStorageChange)
})

onUnmounted(() => {
  window.removeEventListener('storage', handleStorageChange)
})
</script>

<style scoped>
@import './inspiration-styles.css';

.xhs-status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 999px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.xhs-status-indicator .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
}

.xhs-status-indicator.connected .status-dot {
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
}

.xhs-status-indicator.connected {
  color: #22c55e;
}

.hint-text {
  font-size: 0.85rem;
  color: var(--text-tertiary);
  margin-top: 0.5rem;
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.5rem;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>
