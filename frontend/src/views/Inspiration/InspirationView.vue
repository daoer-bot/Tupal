<template>
  <div class="inspiration-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="title-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
        </svg>
        灵感与发现
      </h1>
      <p class="page-subtitle">探索热点，采集灵感</p>
    </div>

    <!-- Tab导航 -->
    <div class="tab-navigation">
      <router-link
        to="/inspiration/trending"
        class="tab-item"
        :class="{ active: $route.path === '/inspiration/trending' || $route.path === '/inspiration' }"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="tab-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z" />
        </svg>
        平台热榜
      </router-link>
      <router-link
        to="/inspiration/collector"
        class="tab-item"
        :class="{ active: $route.path === '/inspiration/collector' }"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="tab-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
        </svg>
        图文采集
      </router-link>
    </div>

    <!-- 内容区域 -->
    <div class="content-area">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style scoped>
.inspiration-view {
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  font-size: 2rem;
  font-weight: 800;
  margin: 0 0 0.5rem;
  color: var(--text-primary);
}

.title-icon {
  width: 32px;
  height: 32px;
  color: var(--primary-color);
}

.page-subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
  margin: 0;
}

/* Tab导航 */
.tab-navigation {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-lg, 12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-md, 8px);
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
}

.tab-item:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.tab-item.active {
  color: var(--primary-color);
  background: rgba(var(--primary-rgb, 99, 102, 241), 0.15);
}

.tab-icon {
  width: 20px;
  height: 20px;
}

/* 内容区域 */
.content-area {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .inspiration-view {
    padding: 1rem 0.75rem;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .title-icon {
    width: 24px;
    height: 24px;
  }

  .tab-navigation {
    gap: 0.5rem;
  }

  .tab-item {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }

  .tab-icon {
    width: 18px;
    height: 18px;
  }
}
</style>