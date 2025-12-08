<template>
  <div class="workspace-view">
    <!-- 动态极光背景 -->
    <div class="aurora-bg-fixed">
      <div class="aurora-orb-3" style="top: 30%; left: 50%; filter: blur(120px); opacity: 0.4;"></div>
    </div>

    <!-- 头部概览区域 -->
    <div class="dashboard-header animate-fade-in">
      <div class="bento-grid">
        <!-- 欢迎卡片 -->
        <div class="col-span-6 glass-card welcome-card">
          <div class="card-body">
            <h1 class="welcome-title text-gradient">早安，创造者</h1>
            <p class="welcome-subtitle">今天想创作点什么惊艳的作品？</p>
          </div>
        </div>
        
        <!-- 数据概览卡片 -->
        <div class="col-span-3 glass-card stat-card">
          <div class="stat-icon-box purple">
            <FileText :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">12</span>
            <span class="stat-label">已发布作品</span>
          </div>
        </div>
        
        <div class="col-span-3 glass-card stat-card">
          <div class="stat-icon-box cyan">
            <Database :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">1.2GB</span>
            <span class="stat-label">资产库占用</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 悬浮胶囊导航 -->
    <div class="nav-container animate-slide-up" style="--delay: 0.1s">
      <div class="nav-capsule">
        <router-link 
          v-for="tab in tabs" 
          :key="tab.path"
          :to="tab.path"
          class="nav-item"
          :class="{ active: $route.path === tab.path }"
        >
          <component :is="tab.icon" :size="18" />
          <span>{{ tab.label }}</span>
        </router-link>
      </div>
    </div>
    
    <!-- 内容区域 -->
    <div class="content-area animate-slide-up" style="--delay: 0.2s">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FileText, Database } from 'lucide-vue-next'

const tabs = [
  { path: '/workspace/works', label: '作品库', icon: FileText },
  { path: '/workspace/assets', label: '资产库', icon: Database }
]
</script>

<style scoped>
.workspace-view {
  min-height: 100vh;
  padding-top: var(--nav-height);
  position: relative;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.welcome-card {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
}

.welcome-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.welcome-subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  gap: 1.5rem;
}

.stat-icon-box {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon-box.purple { background: rgba(139, 92, 246, 0.2); color: var(--neon-violet); }
.stat-icon-box.cyan { background: rgba(6, 182, 212, 0.2); color: var(--neon-cyan); }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.nav-container {
  position: sticky;
  top: calc(var(--nav-height) + 1rem);
  z-index: 100;
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
  pointer-events: none;
}

.nav-capsule {
  pointer-events: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.content-area {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem 4rem;
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .welcome-title { font-size: 1.5rem; }
  .stat-card { padding: 1rem; }
  .stat-value { font-size: 1.5rem; }
}
</style>