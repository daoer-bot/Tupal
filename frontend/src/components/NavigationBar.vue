<template>
  <header class="navigation-bar">
    <div class="nav-container">
      <!-- Logo 区域 -->
      <div class="logo-section">
        <div class="logo-wrapper">
          <div class="logo-icon breathing-glow">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l-.249 1.74" />
            </svg>
          </div>
          <div class="logo-text">
            <h1 class="brand-name text-gradient-animated">Tupal</h1>
            <p class="brand-tagline">AI创意引擎</p>
          </div>
        </div>
      </div>
      
      <!-- 导航菜单 -->
      <nav class="nav-menu">
        <div class="nav-items">
          <router-link 
            v-for="item in navItems" 
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ 'active': $route.meta.navKey === item.key }"
            @mouseenter="handleNavHover(item)"
            @mouseleave="handleNavLeave"
          >
            <div class="nav-icon">
              <component :is="item.icon" :size="18" />
            </div>
            <span class="nav-label">{{ item.label }}</span>
            <div class="nav-indicator"></div>
          </router-link>
        </div>
        
        <!-- 动态指示器背景 -->
        <div 
          class="nav-indicator-bg" 
          :style="indicatorStyle"
          :class="{ 'transition': isTransitioning }"
        ></div>
      </nav>
      
      <!-- 右侧操作区 -->
      <div class="nav-actions">
        <!-- 模型配置 -->
        <button
          class="action-btn config-btn glass-card-premium"
          @click="showConfigModal = true"
          title="AI模型配置"
        >
          <Settings :size="18" />
          <span class="btn-label">配置</span>
        </button>
        
        <!-- 用户菜单 -->
        <div class="user-menu">
          <button class="action-btn user-btn glass-card-premium" @click="toggleUserMenu">
            <User :size="18" />
          </button>
          
          <transition name="dropdown">
            <div v-if="showUserMenu" class="user-dropdown glass-card-premium">
              <div class="dropdown-header">
                <div class="user-avatar">
                  <User :size="24" />
                </div>
                <div class="user-info">
                  <div class="user-name">创作者</div>
                  <div class="user-status">在线</div>
                </div>
              </div>
              
              <div class="dropdown-divider"></div>
              
              <div class="dropdown-items">
                <button class="dropdown-item" @click="openSettings">
                  <Settings :size="16" />
                  <span>设置</span>
                </button>
              </div>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '../store'
import {
  Database,
  TrendingUp,
  History,
  Settings,
  User
} from 'lucide-vue-next'
import ModelConfigModal from './ModelConfigModal.vue'

const route = useRoute()
const store = useAppStore()
const showConfigModal = ref(false)
const showUserMenu = ref(false)
const isTransitioning = ref(false)

// 导航项
const navItems = [
  {
    key: 'inspiration',
    path: '/inspiration',
    label: '灵感与发现',
    icon: TrendingUp
  },
  {
    key: 'creation',
    path: '/creation',
    label: 'AI创作',
    icon: Database
  },
  {
    key: 'workspace',
    path: '/workspace',
    label: '资产与作品',
    icon: History
  }
]

// 当前激活的导航项索引
const activeNavIndex = computed(() => {
  const currentNavKey = route.meta.navKey
  return navItems.findIndex(item => item.key === currentNavKey)
})

// 指示器样式
const indicatorStyle = computed(() => {
  const index = activeNavIndex.value
  if (index === -1) return {}
  
  return {
    transform: `translateX(${index * 100}%)`,
    width: `${100 / navItems.length}%`
  }
})

// 处理导航悬停
const handleNavHover = (item: any) => {
  // 可以添加悬停效果
}

const handleNavLeave = () => {
  // 可以添加离开效果
}

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
  // 配置已保存，可以添加提示
}

// 点击外部关闭用户菜单
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.user-menu')) {
    showUserMenu.value = false
  }
}

// 监听路由变化
const handleRouteChange = () => {
  isTransitioning.value = true
  setTimeout(() => {
    isTransitioning.value = false
  }, 300)
}

onMounted(() => {
  // 监听点击外部
  document.addEventListener('click', handleClickOutside)
  
  // 监听路由变化
  handleRouteChange()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.navigation-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 72px;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.navigation-bar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg,
    transparent,
    rgba(99, 102, 241, 0.6) 20%,
    rgba(236, 72, 153, 0.6) 50%,
    rgba(139, 92, 246, 0.6) 80%,
    transparent
  );
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Logo 区域 */
.logo-section {
  flex-shrink: 0;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
  animation: breathing-glow 3s ease-in-out infinite;
}

@keyframes breathing-glow {
  0%, 100% {
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
  }
  50% {
    box-shadow: 0 4px 24px rgba(99, 102, 241, 0.6), 0 0 32px rgba(236, 72, 153, 0.3);
  }
}

.logo-icon svg {
  width: 22px;
  height: 22px;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.02em;
  text-shadow: 0 2px 12px rgba(99, 102, 241, 0.4);
}

.brand-tagline {
  font-size: 0.75rem;
  color: #475569;
  margin: 0;
  font-weight: 600;
}

/* 导航菜单 */
.nav-menu {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(241, 245, 249, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 14px;
  padding: 0.25rem;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.nav-items {
  display: flex;
  position: relative;
  z-index: 2;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border-radius: 10px;
  color: #334155;
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
  font-weight: 600;
  font-size: 0.95rem;
}

.nav-item:hover {
  color: #6366f1;
  background: rgba(99, 102, 241, 0.08);
}

.nav-item.active {
  color: #6366f1;
  font-weight: 700;
  background: rgba(99, 102, 241, 0.12);
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-label {
  white-space: nowrap;
}

.nav-indicator {
  position: absolute;
  bottom: -2px;
  left: 50%;
  width: 0;
  height: 2px;
  background: var(--primary-color);
  border-radius: 1px;
  transform: translateX(-50%);
  transition: width 0.3s ease;
}

.nav-item.active .nav-indicator {
  width: 24px;
}

.nav-indicator-bg {
  position: absolute;
  top: 0.25rem;
  bottom: 0.25rem;
  left: 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(236, 72, 153, 0.15));
  border-radius: 10px;
  z-index: 1;
  transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 2px 12px rgba(99, 102, 241, 0.15);
}

.nav-indicator-bg.transition {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* 右侧操作区 */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 12px;
  background: rgba(241, 245, 249, 0.8);
  backdrop-filter: blur(8px);
  color: #334155;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  font-size: 0.9rem;
  font-weight: 600;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.action-btn:hover {
  background: rgba(255, 255, 255, 1);
  color: #6366f1;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.4);
}

.config-btn {
  padding: 0.75rem 1.25rem;
}

.btn-label {
  font-size: 0.85rem;
}

/* 用户菜单 */
.user-menu {
  position: relative;
}

.user-btn {
  padding: 0.75rem;
  border-radius: 50%;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  min-width: 200px;
  padding: 0.75rem;
  z-index: 1000;
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 0.9rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.user-status {
  font-size: 0.75rem;
  color: #10b981;
  margin: 0;
}

.dropdown-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0.5rem 0;
}

.dropdown-items {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: none;
  border: none;
  color: #475569;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.3s ease;
  font-size: 0.85rem;
  font-weight: 500;
  width: 100%;
  text-align: left;
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--primary-color);
}

/* 动画 */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 下拉动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 暗色模式支持 */
[data-theme='dark'] .navigation-bar {
  background: rgba(15, 23, 42, 0.95);
  border-bottom-color: rgba(51, 65, 85, 0.8);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
}

[data-theme='dark'] .navigation-bar::before {
  background: linear-gradient(90deg,
    transparent,
    rgba(99, 102, 241, 0.7) 20%,
    rgba(236, 72, 153, 0.7) 50%,
    rgba(139, 92, 246, 0.7) 80%,
    transparent
  );
}

[data-theme='dark'] .brand-name {
  text-shadow: 0 2px 16px rgba(99, 102, 241, 0.6);
}

[data-theme='dark'] .brand-tagline {
  color: #94a3b8;
}

[data-theme='dark'] .nav-menu {
  background: rgba(30, 41, 59, 0.8);
  border-color: rgba(51, 65, 85, 0.8);
}

[data-theme='dark'] .nav-item {
  color: #e2e8f0;
}

[data-theme='dark'] .nav-item:hover {
  color: #a5b4fc;
  background: rgba(99, 102, 241, 0.15);
}

[data-theme='dark'] .nav-item.active {
  color: #a5b4fc;
  font-weight: 700;
  background: rgba(99, 102, 241, 0.2);
}

[data-theme='dark'] .nav-indicator-bg {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(236, 72, 153, 0.2));
  box-shadow: 0 2px 16px rgba(99, 102, 241, 0.3);
}

[data-theme='dark'] .action-btn {
  background: rgba(30, 41, 59, 0.8);
  border-color: rgba(51, 65, 85, 0.8);
  color: #e2e8f0;
}

[data-theme='dark'] .action-btn:hover {
  background: rgba(51, 65, 85, 1);
  border-color: rgba(99, 102, 241, 0.5);
  color: #a5b4fc;
}

[data-theme='dark'] .user-name {
  color: #f1f5f9;
}

[data-theme='dark'] .user-dropdown {
  background: rgba(15, 23, 42, 0.98);
  border-color: rgba(51, 65, 85, 0.8);
}

[data-theme='dark'] .dropdown-divider {
  background: rgba(51, 65, 85, 0.6);
}

[data-theme='dark'] .dropdown-item {
  color: #e2e8f0;
}

[data-theme='dark'] .dropdown-item:hover {
  background: rgba(99, 102, 241, 0.15);
  color: #a5b4fc;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-container {
    padding: 0 1rem;
  }
  
  .logo-text {
    display: none;
  }
  
  .nav-label {
    display: none;
  }
  
  .btn-label {
    display: none;
  }
  
  .nav-item {
    padding: 0.75rem;
  }
  
  .action-btn {
    padding: 0.75rem;
  }
}
</style>
