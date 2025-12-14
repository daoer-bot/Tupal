<template>
  <div class="home-container">
    <div class="bento-grid">
      <!-- 智能创作 - 核心大卡片 -->
      <div class="glass-panel bento-hero hero-card animate-entry" style="--delay: 0s">
        <div class="card-bg-glow"></div>
        <div class="card-content">
          <div class="hero-header">
            <div class="badge-pill">AI Powered</div>
            <h2 class="hero-title text-gradient">智能创作引擎</h2>
            <p class="hero-subtitle">释放无限灵感，一键生成爆款图文</p>
          </div>
          
          <div class="hero-visual">
            <div class="floating-icon icon-1">✨</div>
            <div class="floating-icon icon-2">🎨</div>
            <div class="floating-icon icon-3">🚀</div>
          </div>

          <div class="hero-actions">
            <button class="btn btn-primary primary-action" @click="$router.push('/creation/new')">
              <span class="btn-icon">✨</span>
              <span>开始全新创作</span>
            </button>
            <button class="btn btn-secondary secondary-action" @click="$router.push('/creation/template')">
              <span class="btn-icon">📝</span>
              <span>使用模板</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 灵感集市 -->
      <div class="glass-panel bento-sidebar feature-card animate-entry" style="--delay: 0.1s">
        <div class="card-content">
          <div class="card-header">
            <h3 class="card-title">灵感发现</h3>
            <span class="card-tag">每日更新</span>
          </div>
          
          <div class="feature-links">
            <router-link to="/inspiration/trending" class="feature-link-item">
              <div class="link-icon-wrapper hot">
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                </svg>
              </div>
              <div class="link-info">
                <span class="link-title">全网热榜</span>
                <span class="link-desc">实时追踪流量趋势</span>
              </div>
              <div class="link-arrow">→</div>
            </router-link>
            
            <router-link to="/inspiration/collector" class="feature-link-item">
              <div class="link-icon-wrapper collect">
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
              </div>
              <div class="link-info">
                <span class="link-title">素材采集</span>
                <span class="link-desc">一键提取优质内容</span>
              </div>
              <div class="link-arrow">→</div>
            </router-link>
          </div>
        </div>
      </div>

      <!-- 模板广场 -->
      <router-link to="/inspiration/templates" class="glass-panel bento-small quick-card animate-entry" style="--delay: 0.2s">
        <div class="card-bg-decoration template-bg"></div>
        <div class="card-content center-content">
          <div class="quick-icon-wrapper template">
            <svg width="28" height="28" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z"/>
            </svg>
          </div>
          <h3 class="quick-title">模板广场</h3>
          <p class="quick-desc">海量爆款模板</p>
        </div>
      </router-link>

      <!-- 我的作品 -->
      <router-link to="/workspace/works" class="glass-panel bento-small quick-card animate-entry" style="--delay: 0.3s">
        <div class="card-bg-decoration works-bg"></div>
        <div class="card-content center-content">
          <div class="quick-icon-wrapper works">
            <svg width="28" height="28" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
          <h3 class="quick-title">我的作品</h3>
          <p class="quick-desc">管理创作历史</p>
        </div>
      </router-link>

      <!-- 我的资产 -->
      <router-link to="/workspace/assets" class="glass-panel bento-small quick-card animate-entry" style="--delay: 0.4s">
        <div class="card-bg-decoration assets-bg"></div>
        <div class="card-content center-content">
          <div class="quick-icon-wrapper assets">
            <svg width="28" height="28" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/>
            </svg>
          </div>
          <h3 class="quick-title">我的资产</h3>
          <p class="quick-desc">素材资源库</p>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
// 逻辑保持简洁，主要依靠 CSS 动画
</script>

<style scoped>
.home-container {
  height: 100%; /* 占满父容器剩余空间 */
  overflow-y: auto; /* 允许内部滚动 */
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(2, 240px);
  gap: 1.5rem;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

/* 卡片通用样式已由 glass-panel 接管 */

/* 布局定义 */
.bento-hero {
  grid-column: span 2;
  grid-row: span 2;
}

.bento-sidebar {
  grid-column: span 2;
  grid-row: span 1;
}

.bento-small {
  grid-column: span 1; /* 修正为 span 1，因为总列数改为 4 */
  grid-row: span 1;
}

/* 修正布局：让 sidebar 占右侧上方两格，下面三个小卡片占右侧下方 */
.bento-sidebar {
  grid-column: 3 / 5;
  grid-row: 1 / 2;
}

.bento-small:nth-of-type(3) { /* 模板广场 */
  grid-column: 3 / 4;
  grid-row: 2 / 3;
}

.bento-small:nth-of-type(4) { /* 我的作品 */
  grid-column: 4 / 5;
  grid-row: 2 / 3;
}

.bento-small:nth-of-type(5) { /* 我的资产 - 放到哪里？ */
  /* 重新调整布局策略 */
  /* 方案：
     Hero: 2x2 (左侧)
     Sidebar: 2x1 (右侧上)
     Small 1: 1x1 (右侧下左)
     Small 2: 1x1 (右侧下右)
     Small 3: ... 哎呀，格子不够了。
     
     调整方案：
     Grid 4列 x 2行
     Hero: 2列 x 2行 (左半边)
     Sidebar: 2列 x 1行 (右半边上)
     Small 1: 1列 (右下1)
     Small 2: 1列 (右下2)
     Small 3: ... 还是不够。
     
     最终方案：
     Grid 3列 x 2行 (保持原比例，但优化内部)
     Hero: 2列 x 2行
     Sidebar: 1列 x 1行 (右上)
     Small 1: 1列 x 1行 (右中) -> 不对，这样高度不对。
     
     让我们用更灵活的 Grid：
     Grid 3列
     Hero: 2列 x 2行
     Sidebar: 1列 x 1.2行 (稍微高一点)
     Small Cards: 放在 Sidebar 下面？
     
     为了视觉平衡，我们把 Small Cards 做成一行三个放在最下面？
     或者：
     Hero (2x2) | Sidebar (1x2)
     Small | Small | Small
     
     这样布局更稳重。
  */
}

/* 重新定义 Grid 布局 */
.bento-grid {
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: 360px 180px; /* 上层高，下层矮 */
}

.bento-hero {
  grid-column: 1 / 3;
  grid-row: 1 / 2;
}

.bento-sidebar {
  grid-column: 3 / 4;
  grid-row: 1 / 2;
}

.bento-small {
  grid-column: span 1;
  grid-row: 2 / 3;
}

/* Hero Card 内容 */
.card-content {
  height: 100%;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 2;
}

.hero-header {
  margin-bottom: auto;
}

.badge-pill {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: white;
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 20px;
  color: var(--primary-color);
  font-size: 0.75rem;
  font-weight: 700;
  margin-bottom: 1rem;
  box-shadow: 0 2px 5px rgba(99, 102, 241, 0.1);
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  margin: 0 0 1rem 0;
  line-height: 1.1;
  color: var(--text-primary);
}

.hero-subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
  margin: 0;
  max-width: 80%;
}

.hero-visual {
  position: absolute;
  top: 2rem;
  right: 2rem;
  width: 200px;
  height: 200px;
  pointer-events: none;
}

.floating-icon {
  position: absolute;
  font-size: 3rem;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.1));
  animation: float 6s ease-in-out infinite;
}

.icon-1 { top: 0; right: 20%; animation-delay: 0s; font-size: 4rem; }
.icon-2 { bottom: 20%; left: 0; animation-delay: -2s; font-size: 2.5rem; }
.icon-3 { top: 40%; right: 0; animation-delay: -4s; font-size: 3rem; }

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(10deg); }
}

.hero-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.primary-action {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  border-radius: var(--radius-md);
}

.secondary-action {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  border-radius: var(--radius-md);
}

/* Sidebar Card */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.card-tag {
  font-size: 0.75rem;
  color: var(--text-secondary);
  background: rgba(0, 0, 0, 0.05);
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-weight: 600;
}

.feature-links {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feature-link-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  text-decoration: none;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.feature-link-item:hover {
  background: white;
  border-color: var(--primary-color);
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.link-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.link-icon-wrapper.hot { background: linear-gradient(135deg, #f43f5e, #fb7185); box-shadow: 0 4px 10px rgba(244, 63, 94, 0.3); }
.link-icon-wrapper.collect { background: linear-gradient(135deg, #8b5cf6, #a78bfa); box-shadow: 0 4px 10px rgba(139, 92, 246, 0.3); }

.link-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.link-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 1rem;
}

.link-desc {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.link-arrow {
  color: var(--text-tertiary);
  font-weight: bold;
  transition: transform 0.3s ease;
}

.feature-link-item:hover .link-arrow {
  transform: translateX(4px);
  color: var(--primary-color);
}

/* Small Cards */
.center-content {
  align-items: center;
  justify-content: center;
  text-align: center;
}

.quick-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  transition: transform 0.3s ease;
}

.quick-icon-wrapper.template { background: #fdf2f8; color: #db2777; border: 1px solid #fbcfe8; }
.quick-icon-wrapper.works { background: #eef2ff; color: #4f46e5; border: 1px solid #c7d2fe; }
.quick-icon-wrapper.assets { background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }

.quick-card:hover .quick-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.quick-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
}

.quick-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0;
}

/* 入场动画 */
.animate-entry {
  opacity: 0;
  animation: slideUpFade 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
  animation-delay: var(--delay);
}

@keyframes slideUpFade {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式 */
@media (max-width: 1024px) {
  .bento-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: auto;
  }
  
  .bento-hero { grid-column: span 2; }
  .bento-sidebar { grid-column: span 2; }
  .bento-small { grid-column: span 1; }
}

@media (max-width: 768px) {
  .bento-grid {
    grid-template-columns: 1fr;
  }
  
  .bento-hero, .bento-sidebar, .bento-small {
    grid-column: span 1;
  }
  
  .hero-title { font-size: 2rem; }
  .hero-visual { display: none; }
}
</style>