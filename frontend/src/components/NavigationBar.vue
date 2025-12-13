<template>
  <header class="macaron-nav-wrapper">
    <!-- 悬浮胶囊岛 -->
    <div class="nav-island glass-panel">
      <!-- Logo (Left) -->
      <div class="nav-left">
        <div class="brand-logo">
          <div class="logo-icon">🧁</div>
          <span class="brand-text">Tupal</span>
        </div>
      </div>
      
      <!-- Menu (Center) -->
      <nav class="nav-center">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-pill"
          :class="{ 'active': $route.meta.navKey === item.key }"
        >
          <component :is="item.icon" :size="18" class="nav-icon" />
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>
      
      <!-- Actions (Right) -->
      <div class="nav-right">
        <button
          class="action-bubble"
          @click="showConfigModal = true"
          title="Settings"
        >
          <Settings :size="18" />
        </button>
        
        <div class="user-menu-wrapper">
          <button class="action-bubble user-bubble" @click="toggleUserMenu">
            <div class="avatar-img">🐱</div>
          </button>
          
          <transition name="pop">
            <div v-if="showUserMenu" class="macaron-dropdown glass-panel">
              <div class="dropdown-header">
                <div class="user-info">
                  <span class="user-name">Sweet Creator</span>
                  <span class="user-role">Pro Member</span>
                </div>
              </div>
              <div class="divider"></div>
              <button class="dropdown-item" @click="openSettings">
                <Settings :size="14" />
                <span>Settings</span>
              </button>
              <button class="dropdown-item logout">
                <LogOut :size="14" />
                <span>Log out</span>
              </button>
            </div>
          </transition>
        </div>
      </div>
    </div>
    
    <!-- 配置模态框 -->
    <ModelConfigModal
      :show="showConfigModal"
      @close="showConfigModal = false"
      @save="handleSaveConfig"
    />
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '../store'
import {
  Sparkles,
  Palette,
  Layout,
  Settings,
  LogOut
} from 'lucide-vue-next'
import ModelConfigModal from './ModelConfigModal.vue'

const route = useRoute()
const store = useAppStore()
const showConfigModal = ref(false)
const showUserMenu = ref(false)

// 导航项 - 使用更可爱的图标和文案
const navItems = [
  { key: 'inspiration', path: '/inspiration', label: '灵感', icon: Sparkles },
  { key: 'creation', path: '/creation', label: '创作', icon: Palette },
  { key: 'workspace', path: '/workspace', label: '空间', icon: Layout }
]

// 切换用户菜单
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

// 打开设置
const openSettings = () => {
  showConfigModal.value = true
  showUserMenu.value = false
}

// 保存配置
const handleSaveConfig = () => {
  // 配置已保存
}

// 点击外部关闭用户菜单
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.user-menu-wrapper')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.macaron-nav-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: var(--nav-height);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none; /* 让两侧透过去，只有岛屿可交互 */
}

/* --- 🏝️ 悬浮胶囊岛 --- */
.nav-island {
  pointer-events: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.8rem;
  gap: 1rem;
  min-width: 600px;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 100px; /* 超大圆角 */
  box-shadow: 
    0 10px 30px -5px rgba(255, 183, 178, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.8);
  margin-top: 1rem;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.nav-island:hover {
  transform: translateY(2px);
  box-shadow: 
    0 15px 40px -5px rgba(255, 183, 178, 0.3),
    0 0 0 1px white;
}

/* --- 🧁 左侧 Logo --- */
.nav-left {
  padding-left: 0.5rem;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-icon {
  font-size: 1.5rem;
  animation: bounce 2s infinite;
}

.brand-text {
  font-family: 'Quicksand', sans-serif;
  font-weight: 700;
  font-size: 1.2rem;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

/* --- 💊 中间导航 --- */
.nav-center {
  display: flex;
  background: #F0F4F8; /* 浅灰底 */
  padding: 4px;
  border-radius: 100px;
  position: relative;
}

.nav-pill {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1.2rem;
  border-radius: 100px;
  text-decoration: none;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  z-index: 1;
}

.nav-pill:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.5);
}

.nav-pill.active {
  color: #fff;
  background: var(--macaron-pink-deep);
  box-shadow: 0 4px 12px rgba(255, 154, 162, 0.4);
}

.nav-pill.active .nav-icon {
  transform: scale(1.1);
}

/* --- 🫧 右侧按钮 --- */
.nav-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-right: 0.5rem;
}

.action-bubble {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: white;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.action-bubble:hover {
  transform: scale(1.1) rotate(10deg);
  color: var(--macaron-pink-deep);
  box-shadow: 0 5px 15px rgba(255, 154, 162, 0.2);
}

.user-bubble {
  padding: 2px;
  background: linear-gradient(135deg, var(--macaron-pink), var(--macaron-mint));
}

.avatar-img {
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

/* --- 📜 下拉菜单 --- */
.macaron-dropdown {
  position: absolute;
  top: 50px;
  right: 0;
  width: 200px;
  padding: 0.8rem;
  background: rgba(255, 255, 255, 0.95);
  z-index: 1100;
  transform-origin: top right;
}

.dropdown-header {
  padding: 0.5rem;
  margin-bottom: 0.5rem;
}

.user-name {
  display: block;
  font-weight: 700;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.user-role {
  display: block;
  font-size: 0.75rem;
  color: var(--macaron-pink-deep);
  font-weight: 600;
  margin-top: 2px;
}

.divider {
  height: 1px;
  background: #f0f0f0;
  margin: 0.5rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  width: 100%;
  padding: 0.6rem;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.dropdown-item:hover {
  background: var(--macaron-mint-light);
  color: #5d5656;
  transform: translateX(4px);
}

.dropdown-item.logout:hover {
  background: #fff0f0;
  color: #ff6b6b;
}

/* 动画 */
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.pop-enter-active,
.pop-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(-10px);
}
</style>
