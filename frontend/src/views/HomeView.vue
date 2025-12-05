<template>
  <div class="home-container">
    <div class="bento-grid">
      <!-- 智能创作 - 核心大卡片 -->
      <div class="bento-card glass-panel bento-hero hero-card">
        <div class="card-content">
          <div class="hero-header">
            <h2 class="hero-title text-gradient">智能创作</h2>
            <p class="hero-subtitle">AI 驱动的内容创作引擎</p>
          </div>
          <div class="hero-actions">
            <button class="hero-btn primary" @click="$router.push('/creation/new')">
              <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              <span>全新创作</span>
            </button>
            <button class="hero-btn secondary" @click="$router.push('/creation/template')">
              <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5z"/>
              </svg>
              <span>模板创作</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 灵感集市 -->
      <div class="bento-card glass-panel bento-sidebar feature-card">
        <div class="card-content">
          <h3 class="card-title">灵感与发现</h3>
          <div class="feature-links">
            <router-link to="/inspiration/trending" class="feature-link">
              <svg class="link-icon" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
              </svg>
              <span class="link-text">热榜观测</span>
              <svg class="link-arrow" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
            </router-link>
            <router-link to="/inspiration/collector" class="feature-link">
              <svg class="link-icon" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              <span class="link-text">图文采集</span>
              <svg class="link-arrow" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
            </router-link>
          </div>
        </div>
      </div>

      <!-- 模板广场 -->
      <router-link to="/inspiration/templates" class="bento-card glass-panel bento-small quick-card">
        <div class="card-content">
          <svg class="quick-icon" width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z"/>
          </svg>
          <h3 class="quick-title">模板广场</h3>
          <p class="quick-desc">探索热门模板</p>
        </div>
      </router-link>

      <!-- 我的作品 -->
      <router-link to="/workspace/works" class="bento-card glass-panel bento-small quick-card">
        <div class="card-content">
          <svg class="quick-icon" width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <h3 class="quick-title">我的作品</h3>
          <p class="quick-desc">查看创作历史</p>
        </div>
      </router-link>

      <!-- 我的资产 -->
      <router-link to="/workspace/assets" class="bento-card glass-panel bento-small quick-card">
        <div class="card-content">
          <svg class="quick-icon" width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/>
          </svg>
          <h3 class="quick-title">我的资产</h3>
          <p class="quick-desc">管理素材资源</p>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.home-container {
  min-height: calc(100vh - 96px);
  padding: 2rem 0;
}

.bento-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, minmax(180px, auto));
  gap: 1.5rem;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.bento-hero {
  grid-column: 1 / 3;
  grid-row: 1 / 3;
}

.bento-sidebar {
  grid-column: 3 / 4;
  grid-row: 1 / 3;
}

.bento-small {
  grid-column: span 1;
  grid-row: span 1;
}

.card-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Hero Card 样式 */
.hero-card {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.08));
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.hero-header {
  margin-bottom: auto;
}

.hero-title {
  font-size: 2.75rem;
  font-weight: 800;
  margin: 0 0 0.75rem 0;
  letter-spacing: -0.03em;
  line-height: 1.1;
}

.hero-subtitle {
  color: var(--text-secondary);
  font-size: 1.125rem;
  margin: 0;
  font-weight: 500;
  line-height: 1.5;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 2.5rem;
}

.hero-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  border: none;
  border-radius: 16px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  overflow: hidden;
}

.hero-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.5s;
}

.hero-btn:hover::before {
  left: 100%;
}

.hero-btn.primary {
  background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
  color: white;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
}

.hero-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(99, 102, 241, 0.5);
}

.hero-btn.secondary {
  background: rgba(255, 255, 255, 0.2);
  color: var(--text-primary);
  border: 2px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}

.hero-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateY(-2px);
}

/* Feature Card 样式 */
.feature-card {
  display: flex;
  flex-direction: column;
}

.feature-card .card-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0 0 2rem 0;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.feature-links {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.feature-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.feature-link:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateX(6px);
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.link-icon {
  flex-shrink: 0;
  color: var(--primary-color);
}

.link-text {
  flex: 1;
  font-weight: 600;
  font-size: 1.05rem;
  letter-spacing: -0.01em;
}

.link-arrow {
  flex-shrink: 0;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.feature-link:hover .link-arrow {
  opacity: 1;
  transform: translateX(4px);
}

/* Quick Card 样式 */
.quick-card {
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.quick-card:hover {
  transform: translateY(-6px) scale(1.02);
}

.quick-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 1.25rem;
  color: var(--primary-color);
  stroke-width: 1.5;
}

.quick-title {
  font-size: 1.375rem;
  font-weight: 700;
  margin: 0 0 0.625rem 0;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.quick-desc {
  color: var(--text-secondary);
  font-size: 0.9375rem;
  margin: 0;
  font-weight: 500;
}

/* 暗色模式适配 */
[data-theme='dark'] .hero-btn.secondary {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
}

[data-theme='dark'] .feature-link {
  background: rgba(255, 255, 255, 0.05);
}

[data-theme='dark'] .feature-link:hover {
  background: rgba(255, 255, 255, 0.08);
}
</style>