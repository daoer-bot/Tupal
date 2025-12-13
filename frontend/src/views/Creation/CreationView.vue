<template>
  <div class="creation-view">
    <!-- 内容区域 -->
    <div class="content-area">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
// 简化后的容器，移除 Spotlight 逻辑，依靠全局背景
</script>

<style scoped>
.creation-view {
  min-height: calc(100vh - var(--nav-height));
  width: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>