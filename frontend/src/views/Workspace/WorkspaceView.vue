<template>
  <div class="workspace-view">
    <div class="workspace-container">
      
      <!-- 🍬 简约糖果 Tab 导航 -->
      <div class="tabs-wrapper animate-fade-in">
        <div class="simple-tabs">
          <router-link
            v-for="tab in tabs"
            :key="tab.path"
            :to="tab.path"
            class="tab-item"
            :class="{ active: $route.path === tab.path }"
          >
            <component :is="tab.icon" :size="16" class="tab-icon" />
            <span>{{ tab.label }}</span>
          </router-link>
        </div>
      </div>
      
      <!-- 📦 内容展示柜 -->
      <div class="content-display-case">
        <router-view v-slot="{ Component }">
          <transition name="pop" mode="out-in">
            <KeepAlive>
              <component :is="Component" />
            </KeepAlive>
          </transition>
        </router-view>
      </div>
      
    </div>
  </div>
</template>

<script setup lang="ts">
import { FileText, Database, Bookmark } from 'lucide-vue-next'

const tabs = [
  { path: '/workspace/works', label: '我的作品', icon: FileText },
  { path: '/workspace/knowledge', label: '知识库', icon: Database },
  { path: '/workspace/cases', label: '灵感收藏', icon: Bookmark }
]
</script>

<style scoped>
.workspace-view {
  min-height: 100vh;
  /* padding-top 由 App.vue 的全局 padding 处理 */
  position: relative;
}

.workspace-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* --- 🍬 Tabs --- */
.tabs-wrapper {
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
  width: 100%;
}

.simple-tabs {
  display: flex;
  padding: 4px;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.tab-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.5rem;
  border-radius: 12px;
  text-decoration: none;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.tab-item:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.5);
}

.tab-item.active {
  color: white;
  background: var(--macaron-pink);
  box-shadow: 0 4px 12px rgba(255, 154, 162, 0.3);
}

/* --- 📦 内容区域 --- */
.content-display-case {
  width: 100%;
  min-height: 400px;
}

/* 路由动画 */
.pop-enter-active,
.pop-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}

/* 响应式 */
@media (max-width: 768px) {
  .workspace-container {
    padding: 1rem;
  }
  
  .simple-tabs {
    width: 100%;
    overflow-x: auto;
    justify-content: flex-start;
  }
  
  .tab-item {
    flex: 1;
    justify-content: center;
    padding: 0.6rem 1rem;
    white-space: nowrap;
  }
}
</style>
