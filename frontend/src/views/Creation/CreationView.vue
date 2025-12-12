<template>
  <div class="creation-view">
    <!-- 动态极光背景 -->
    <div class="aurora-bg-fixed">
      <div class="aurora-orb-1" style="top: -20%; left: 10%; filter: blur(100px); opacity: 0.6;"></div>
      <div class="aurora-orb-2" style="bottom: -20%; right: 10%; filter: blur(100px); opacity: 0.6;"></div>
    </div>

    <!-- 页面标题区域 -->
    <div class="page-header animate-fade-in">
      <h1 class="page-title">
        <Sparkles :size="28" class="title-icon" />
        AI创作
      </h1>
      <p class="page-subtitle">智能内容生成，让创作更简单</p>
    </div>
    
    <!-- 内容区域 -->
    <!-- 移除 animate-slide-up 类和内部 transition，避免与 App.vue 的 transition 冲突导致UI消失 -->
    <div class="content-area">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Sparkles } from 'lucide-vue-next'
</script>

<style scoped>
.creation-view {
  min-height: 100vh;
  padding-top: var(--nav-height);
  position: relative;
}

.page-header {
  text-align: center;
  padding: 2rem 2rem 1rem;
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin: 0 0 0.75rem 0;
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-icon {
  color: #6366f1;
  -webkit-text-fill-color: initial;
}

.page-subtitle {
  margin: 0;
  font-size: 1.0625rem;
  color: #64748b;
}

.content-area {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem 4rem;
}

/* 动画类 - 简化版，避免与全局 transition 冲突 */
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>