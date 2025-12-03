<template>
  <div id="app" class="app-wrapper">
    <!-- 🌌 动态极光背景层 -->
    <div class="aurora-bg">
      <div class="aurora-orb orb-1"></div>
      <div class="aurora-orb orb-2"></div>
      <div class="aurora-orb orb-3"></div>
    </div>

    <!-- 🏗️ 顶部导航栏 -->
    <header class="top-navbar">
      <div class="navbar-container">
        <!-- Logo 区域 -->
        <div class="logo-area">
          <div class="logo-icon animate-pulse-slow">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l-.249 1.74" />
            </svg>
          </div>
          <h1 class="logo-text text-gradient">Tupal</h1>
        </div>
        
        <!-- 导航菜单 -->
        <nav class="nav-menu">
          <router-link to="/" class="nav-item" active-class="active">
            <span class="label">灵感工坊</span>
          </router-link>

          <router-link to="/materials" class="nav-item" active-class="active">
            <span class="label">素材中心</span>
          </router-link>

          <router-link to="/trending" class="nav-item" active-class="active">
            <span class="label">热点趋势</span>
          </router-link>

          <router-link to="/history" class="nav-item" active-class="active">
            <span class="label">作品档案</span>
          </router-link>
        </nav>

        <!-- 顶部操作区 -->
        <div class="header-actions">
          <button class="config-btn glass-btn" @click="showConfigModal = true" title="AI 模型配置">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.343 3.94c.09-.542.56-.94 1.11-.94h1.093c.55 0 1.02.398 1.11.94l.149.894c.07.424.384.764.78.93.398.164.855.142 1.205-.108l.737-.527a1.125 1.125 0 011.45.12l.773.774c.39.389.44 1.002.12 1.45l-.527.737c-.25.35-.272.806-.107 1.204.165.397.505.71.93.78l.893.15c.543.09.94.56.94 1.109v1.094c0 .55-.397 1.02-.94 1.11l-.893.149c-.425.07-.765.383-.93.78-.165.398-.143.854.107 1.204l.527.738c.32.447.269 1.06-.12 1.45l-.774.773a1.125 1.125 0 01-1.449.12l-.738-.527c-.35-.25-.806-.272-1.203-.107-.397.165-.71.505-.781.929l-.149.894c-.09.542-.56.94-1.11.94h-1.094c-.55 0-1.02-.398-1.11-.94l-.149-.894c-.07-.424-.384-.764-.78-.93-.398-.164-.855-.142-1.205.108l-.738.527c-.447.32-1.06.269-1.45-.12l-.773-.774a1.125 1.125 0 01-.12-1.45l.527-.737c.25-.35.273-.806.108-1.204-.165-.397-.506-.71-.93-.78l-.894-.15c-.542-.09-.94-.56-.94-1.109v-1.094c0-.55.398-1.02.94-1.11l.894-.149c.424-.07.765-.383.93-.78.165-.398.143-.854-.107-1.204l-.527-.738a1.125 1.125 0 01.12-1.45l.773-.773a1.125 1.125 0 011.45-.12l.737.527c.35.25.807.272 1.204.107.397-.165.71-.505.78-.929l.15-.894z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span class="label">模型配置</span>
          </button>
        </div>
      </div>
    </header>

    <!-- 🎨 主舞台 -->
    <main class="main-stage">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 配置模态框 -->
    <ModelConfigModal
      :show="showConfigModal"
      @close="showConfigModal = false"
      @save="handleSaveConfig"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useAppStore } from './store'
import ModelConfigModal from './components/ModelConfigModal.vue'

const store = useAppStore()
const showConfigModal = ref(false)

// 模型配置状态
const textModels = ref<any[]>([])
const imageModels = ref<any[]>([])
const selectedTextIndex = ref(0)
const selectedImageIndex = ref(0)

const loadConfig = () => {
  const savedTextModels = localStorage.getItem('textModels')
  const savedImageModels = localStorage.getItem('imageModels')
  const savedSelectedTextIndex = localStorage.getItem('selectedTextIndex')
  const savedSelectedImageIndex = localStorage.getItem('selectedImageIndex')
  
  if (savedTextModels) textModels.value = JSON.parse(savedTextModels)
  if (savedImageModels) imageModels.value = JSON.parse(savedImageModels)
  if (savedSelectedTextIndex) selectedTextIndex.value = parseInt(savedSelectedTextIndex)
  if (savedSelectedImageIndex) selectedImageIndex.value = parseInt(savedSelectedImageIndex)
  
  updateStoreConfig()
}

const updateStoreConfig = () => {
  if (textModels.value.length > 0 && textModels.value[selectedTextIndex.value]) {
    store.setTextModelConfig(textModels.value[selectedTextIndex.value])
  }
  if (imageModels.value.length > 0 && imageModels.value[selectedImageIndex.value]) {
    store.setImageModelConfig(imageModels.value[selectedImageIndex.value])
  }
}

const handleSaveConfig = (
  newTextModels: any[],
  newImageModels: any[],
  newSelectedTextIndex: number,
  newSelectedImageIndex: number
) => {
  textModels.value = newTextModels
  imageModels.value = newImageModels
  selectedTextIndex.value = newSelectedTextIndex
  selectedImageIndex.value = newSelectedImageIndex
  
  updateStoreConfig()
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.app-wrapper {
  display: flex;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

/* === 极光背景动画 === */
.aurora-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -1;
  background: var(--bg-color);
  overflow: hidden;
}

.aurora-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation: float-orb 20s infinite ease-in-out;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: var(--primary-color);
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: var(--secondary-color);
  bottom: 10%;
  right: 10%;
  animation-delay: -5s;
}

.orb-3 {
  width: 300px;
  height: 300px;
  background: var(--accent-color);
  top: 40%;
  left: 40%;
  animation-delay: -10s;
}

@keyframes float-orb {
  0% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0, 0) scale(1); }
}

/* === 顶部导航栏 === */
.top-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px; /* 稍微减小高度，更精致 */
  z-index: 100;
  display: flex;
  justify-content: center; /* 让内部容器居中 */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.7);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.navbar-container {
  width: 100%;
  max-width: 1400px; /* 限制最大宽度 */
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
}

.logo-icon svg {
  width: 18px;
  height: 18px;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 800;
  white-space: nowrap;
  letter-spacing: -0.02em;
}

/* 导航菜单 - 绝对居中 */
.nav-menu {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 4px;
  height: 100%;
}

.nav-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px 16px;
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  font-size: 0.95rem;
  font-weight: 500;
  height: 36px;
}

.nav-item:hover {
  color: var(--primary-color);
  background: rgba(0, 0, 0, 0.03);
}

.nav-item.active {
  color: var(--primary-color);
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  font-weight: 600;
}

/* 顶部操作区 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0; /* 防止被压缩 */
}

.glass-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 16px; /* 水平 padding */
  height: 36px; /* 固定高度 */
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 99px;
  background: white;
  color: var(--text-primary);
  transition: all 0.2s ease;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  white-space: nowrap; /* 强制不换行 */
  flex-shrink: 0; /* 强制不压缩 */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.glass-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
  transform: translateY(-1px);
}

/* === 主舞台 === */
.main-stage {
  flex: 1;
  margin-top: 72px; /* 留出顶部导航栏的高度 */
  padding: 24px;
  min-height: calc(100vh - 72px);
  position: relative;
  z-index: 10;
}

.animate-pulse-slow {
  animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .8; }
}
</style>