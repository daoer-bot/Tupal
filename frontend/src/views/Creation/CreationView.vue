<template>
  <div class="creation-view">
    <!-- 动态极光背景 -->
    <div class="aurora-bg-fixed">
      <div class="aurora-orb-1" style="top: -20%; left: 10%; filter: blur(100px); opacity: 0.6;"></div>
      <div class="aurora-orb-2" style="bottom: -20%; right: 10%; filter: blur(100px); opacity: 0.6;"></div>
    </div>

    <!-- 悬浮胶囊导航 -->
    <div class="nav-container animate-fade-in">
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
    <div class="content-area animate-slide-up">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Sparkles, FileText } from 'lucide-vue-next'

const tabs = [
  { path: '/creation/new', label: '全新创作', icon: Sparkles },
  { path: '/creation/template', label: '模板创作', icon: FileText }
]
</script>

<style scoped>
.creation-view {
  min-height: 100vh;
  padding-top: var(--nav-height);
  position: relative;
}

.nav-container {
  position: sticky;
  top: calc(var(--nav-height) + 1rem);
  z-index: 100;
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
  pointer-events: none; /* 让点击穿透容器 */
}

.nav-capsule {
  pointer-events: auto; /* 恢复导航点击 */
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
</style>