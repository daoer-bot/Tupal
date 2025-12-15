<template>
  <div class="inspiration-view">
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
import { ref, computed, onMounted } from 'vue'
import TrendingCard from '../../components/TrendingCard.vue'
import { getTrendingSources, getAllTrending, type TrendingSource, type TrendingResponse } from '../../services/trendingApi'

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
  { label: '精选案例', value: curatedSpots.value.length || '—' },
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
})
</script>

<style scoped>
.inspiration-view {
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.hero {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  padding: 2.5rem;
  border-radius: 28px;
}

.hero-copy h1 {
  margin: 0 0 0.75rem;
  font-size: 2.5rem;
  color: var(--text-primary);
}

.eyebrow {
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-tertiary);
  margin-bottom: 0.5rem;
}

.hero-desc {
  margin: 0 0 1.5rem;
  color: var(--text-secondary);
  line-height: 1.7;
}

.hero-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(100px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 1rem;
  text-align: center;
}

.metric-value {
  display: block;
  font-size: 2rem;
  font-weight: 800;
  color: var(--primary-color);
}

.metric-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.update-hint {
  font-size: 0.85rem;
  color: var(--text-secondary);
  align-self: center;
}

.ghost-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.6);
  color: var(--text-primary);
  border-radius: 999px;
  padding: 0.8rem 1.5rem;
  font-weight: 600;
}

.ghost-btn:disabled {
  opacity: 0.5;
}

.hero-visual {
  position: relative;
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bubble {
  position: absolute;
  border-radius: 24px;
  padding: 1.2rem 1.5rem;
  color: white;
  font-weight: 600;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
}

.bubble span {
  display: block;
  font-size: 0.85rem;
  font-weight: 400;
  opacity: 0.85;
}

.bubble-large { background: linear-gradient(135deg, #ff9aa2, #ffb17a); top: 10%; left: 10%; }
.bubble-medium { background: linear-gradient(135deg, #b5ead7, #8fe1c2); bottom: 15%; right: 15%; }
.bubble-small { background: linear-gradient(135deg, #c7ceea, #b197fc); top: 45%; right: 5%; }

.hero-placeholder {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.section-eyebrow {
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  color: var(--text-tertiary);
  margin: 0 0 0.4rem;
}

.section-header h2 {
  margin: 0;
  font-size: 1.8rem;
  color: var(--text-primary);
}

.section-desc {
  margin: 0;
  max-width: 360px;
  color: var(--text-secondary);
}

.signals-grid {
  margin-top: 1.5rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.signal-card {
  padding: 1.5rem;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.signal-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.signal-badge {
  font-weight: 700;
  color: var(--primary-color);
}

.signal-card h3 {
  margin: 0;
  font-size: 1.2rem;
}

.signal-card p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.signal-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: auto;
}

.signal-tags span {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 999px;
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.signals-placeholder {
  padding: 1.5rem;
  border-radius: 20px;
}

.placeholder-row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.placeholder-bar {
  height: 12px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 999px;
}

.placeholder-bar.short {
  width: 40%;
}

.placeholder-tags {
  height: 10px;
  width: 60%;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 999px;
}

.state-card {
  padding: 1.5rem;
  text-align: center;
  border-radius: 20px;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.retry-btn.ghost {
  background: transparent;
  border: 1px dashed var(--primary-color);
  color: var(--primary-color);
}

.spotlight-grid {
  margin-top: 1.5rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.spotlight-card {
  padding: 1.75rem;
  border-radius: 24px;
}

.spotlight-card.skeleton-card {
  min-height: 220px;
  background: rgba(0, 0, 0, 0.03);
}

.spotlight-type {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--secondary-color);
  margin-bottom: 0.5rem;
}

.spotlight-card h3 {
  margin: 0 0 0.5rem;
  font-size: 1.35rem;
  color: var(--text-primary);
}

.spotlight-summary,
.spotlight-insight {
  margin: 0 0 0.5rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.spotlight-insight {
  font-weight: 600;
  color: var(--text-primary);
}

.spotlight-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 600;
  margin-top: 1rem;
}

.workflow-section {
  padding: 2rem;
  border-radius: 28px;
}

.workflow-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.workflow-step {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 20px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.step-icon {
  font-size: 1.8rem;
}

.step-label {
  font-size: 0.8rem;
  letter-spacing: 0.1em;
  color: var(--text-tertiary);
  margin: 0;
}

.workflow-step h3 {
  margin: 0;
  font-size: 1.2rem;
}

.workflow-step p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.section-trending .loading-container,
.section-trending .error-container {
  min-height: 200px;
  border-radius: 24px;
  text-align: center;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
}

.loading-spinner.large {
  width: 48px;
  height: 48px;
  border: 3px solid rgba(255, 154, 162, 0.2);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.retry-btn {
  padding: 0.6rem 1.4rem;
  border-radius: 999px;
  border: none;
  background: var(--primary-color);
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.trending-grid {
  margin-top: 1.5rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .inspiration-view {
    padding: 1.5rem 1rem 2rem;
  }

  .hero {
    padding: 1.5rem;
  }

  .hero-copy h1 {
    font-size: 2rem;
  }

  .hero-metrics {
    grid-template-columns: repeat(2, 1fr);
  }

  .hero-actions {
    flex-direction: column;
  }

  .section-header {
    flex-direction: column;
  }

  .spotlight-footer {
    flex-direction: column;
    gap: 0.3rem;
  }
}
</style>
