<template>
  <div class="workspace-view">
    <!-- Aurora 背景 -->
    <div class="aurora-bg-fixed">
      <div class="aurora-orb-1"></div>
      <div class="aurora-orb-2"></div>
      <div class="aurora-orb-3"></div>
    </div>

    <div class="workspace-container">
      <!-- 顶部Tab导航 -->
      <div class="tab-navigation glass-panel-heavy">
        <router-link
          v-for="tab in tabs"
          :key="tab.path"
          :to="tab.path"
          class="tab-item"
          :class="{ active: $route.path === tab.path }"
        >
          <component :is="tab.icon" :size="20" />
          <span>{{ tab.label }}</span>
        </router-link>
      </div>
      
      <!-- 内容区域 -->
      <div class="content-area">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FileText, Database, Bookmark } from 'lucide-vue-next'

const tabs = [
  { path: '/workspace/works', label: '作品', icon: FileText },
  { path: '/workspace/knowledge', label: '知识', icon: Database },
  { path: '/workspace/cases', label: '案例', icon: Bookmark }
]
</script>

<style scoped>
.workspace-view {
  min-height: 100vh;
  padding-top: var(--nav-height);
  position: relative;
}

.workspace-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  position: relative;
  z-index: 1;
}

/* 顶部Tab导航 */
.tab-navigation {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  margin-bottom: 2rem;
  border-radius: 16px;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  border-radius: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
}

.tab-item:hover {
  color: var(--text-primary);
  background: rgba(99, 102, 241, 0.1);
}

.tab-item.active {
  color: white;
  background: linear-gradient(135deg, #6366f1, #ec4899);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.content-area {
  animation: fadeIn 0.5s ease-in-out;
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

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .workspace-container {
    padding: 1rem;
  }
  
  .tab-item {
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
  }
  
  .tab-item span {
    display: none;
  }
}
</style>