<template>
  <div id="app" class="app-wrapper">
    <!-- 🌌 全局极光背景 -->
    <div class="aurora-bg-fixed">
      <div class="aurora-orb-1"></div>
      <div class="aurora-orb-2"></div>
      <div class="aurora-orb-3"></div>
    </div>

    <!-- �️ 顶部导航栏 - 使用新的高级导航组件 -->
    <NavigationBar @config="showConfigModal = true" />

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
  store.initTheme()
})
</script>

<style scoped>
.app-wrapper {
  display: flex;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
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