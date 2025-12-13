<template>
  <div id="app" class="app-wrapper">
    <!-- ☁️ 奶油云朵背景 -->
    <div class="macaron-bg">
      <div class="bg-blob blob-1"></div>
      <div class="bg-blob blob-2"></div>
      <div class="bg-blob blob-3"></div>
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
  /* margin-top 由 NavHeight 决定，这里使用 padding 来避免内容被遮挡 */
  padding-top: var(--nav-height);
  min-height: 100vh;
  position: relative;
  z-index: 10;
  overflow-x: hidden;
  /* 确保内容在背景之上 */
}

.animate-pulse-slow {
  animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .8; }
}
</style>