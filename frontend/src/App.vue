<template>
  <div id="app" class="app-wrapper">
    <!-- 🌌 动态极光背景层 -->
    <div class="aurora-bg">
      <div class="aurora-orb orb-1"></div>
      <div class="aurora-orb orb-2"></div>
      <div class="aurora-orb orb-3"></div>
    </div>

    <!-- 🏗️ 顶部导航栏 - 使用新的高级导航组件 -->
    <NavigationBar @config="showConfigModal = true" @toggle-theme="toggleTheme" />

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
import { ref, onMounted } from 'vue'
import { useAppStore } from './store'
import ModelConfigModal from './components/ModelConfigModal.vue'
import NavigationBar from './components/NavigationBar.vue'

const store = useAppStore()
const showConfigModal = ref(false)

// 主题切换逻辑
const initTheme = () => {
  const savedTheme = localStorage.getItem('theme') || 'light'
  document.documentElement.setAttribute('data-theme', savedTheme)
}

const toggleTheme = () => {
  const currentTheme = document.documentElement.getAttribute('data-theme') || 'light'
  const newTheme = currentTheme === 'light' ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', newTheme)
  localStorage.setItem('theme', newTheme)
}

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
  initTheme()
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