<template>
  <div class="creation-view">
    <div class="sub-nav">
      <div class="sub-nav-container">
        <router-link 
          v-for="tab in tabs" 
          :key="tab.path"
          :to="tab.path"
          class="sub-nav-item"
          :class="{ active: $route.path === tab.path }"
        >
          <component :is="tab.icon" :size="18" />
          <span>{{ tab.label }}</span>
        </router-link>
      </div>
    </div>
    
    <div class="content-area">
      <router-view />
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
  padding-top: 72px;
}

.sub-nav {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  position: sticky;
  top: 72px;
  z-index: 100;
}

.sub-nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  gap: 0.5rem;
}

.sub-nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  color: var(--text-secondary);
  text-decoration: none;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.95rem;
}

.sub-nav-item:hover {
  color: var(--primary-color);
  background: rgba(255, 255, 255, 0.1);
}

.sub-nav-item.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.content-area {
  padding: 2rem 0;
}
</style>