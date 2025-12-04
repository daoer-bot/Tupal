<template>
  <div class="hero-section">
    <!-- 粒子背景 -->
    <ParticlesBackground class="particles-bg" />
    
    <!-- 主要内容 -->
    <div class="hero-content">
      <!-- 徽章 -->
      <div class="hero-badge glass-card-premium animate-float">
        <div class="badge-icon">✨</div>
        <span>AI 驱动的创意引擎</span>
      </div>
      
      <!-- 主标题 -->
      <h1 class="hero-title">
        释放无限
        <span class="text-gradient-animated">图文创作灵感</span>
      </h1>
      
      <!-- 副标题 -->
      <p class="hero-subtitle">
        输入一个想法，自动生成完整的小红书图文。
        <br>
        让 AI 成为你的专属设计总监，创作从未如此自由。
      </p>
      
      <!-- CTA 按钮组 -->
      <div class="hero-actions">
        <button class="btn-3d primary-action" @click="scrollToCreation">
          <span class="btn-icon">🚀</span>
          开始创作
        </button>
        <button class="btn-ghost secondary-action" @click="showDemo">
          <span class="btn-icon">▶</span>
          观看演示
        </button>
      </div>
      
      <!-- 特性标签 -->
      <div class="hero-features">
        <div class="feature-tag glass-card-premium">
          <div class="tag-icon">⚡</div>
          <span>3秒生成</span>
        </div>
        <div class="feature-tag glass-card-premium">
          <div class="tag-icon">🎨</div>
          <span>风格一致</span>
        </div>
        <div class="feature-tag glass-card-premium">
          <div class="tag-icon">🔥</div>
          <span>热点追踪</span>
        </div>
      </div>
    </div>
    
    <!-- 装饰元素 -->
    <div class="hero-decoration">
      <div class="decoration-orb orb-1 breathing-glow"></div>
      <div class="decoration-orb orb-2 breathing-glow"></div>
      <div class="decoration-orb orb-3 breathing-glow"></div>
    </div>
    
    <!-- 滚动指示器 -->
    <div class="scroll-indicator" @click="scrollToNext">
      <div class="scroll-arrow"></div>
      <span class="scroll-text">向下滚动</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import ParticlesBackground from './ParticlesBackground.vue'

const emit = defineEmits<{
  scrollToCreation: []
  showDemo: []
}>()

const scrollToCreation = () => {
  emit('scrollToCreation')
}

const showDemo = () => {
  emit('showDemo')
}

const scrollToNext = () => {
  window.scrollTo({
    top: window.innerHeight,
    behavior: 'smooth'
  })
}
</script>

<style scoped>
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: linear-gradient(
    135deg,
    rgba(99, 102, 241, 0.1) 0%,
    rgba(236, 72, 153, 0.1) 50%,
    rgba(139, 92, 246, 0.1) 100%
  );
}

.particles-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.hero-content {
  position: relative;
  z-index: 2;
  text-align: center;
  max-width: 800px;
  padding: 0 2rem;
}

/* 徽章样式 */
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  margin-bottom: 2rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--primary-color);
}

.badge-icon {
  font-size: 1.2rem;
  animation: sparkle 2s infinite;
}

@keyframes sparkle {
  0%, 100% { transform: scale(1) rotate(0deg); }
  50% { transform: scale(1.2) rotate(180deg); }
}

/* 标题样式 */
.hero-title {
  font-size: 4rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

/* 副标题样式 */
.hero-subtitle {
  font-size: 1.25rem;
  color: var(--text-secondary);
  margin-bottom: 3rem;
  line-height: 1.6;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

/* 按钮组样式 */
.hero-actions {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  margin-bottom: 3rem;
  flex-wrap: wrap;
}

.primary-action {
  font-size: 1.1rem;
  padding: 1.125rem 2.25rem;
}

.secondary-action {
  font-size: 1.1rem;
  padding: 1.125rem 2.25rem;
}

.btn-icon {
  margin-right: 0.5rem;
  font-size: 1.2rem;
}

/* 特性标签 */
.hero-features {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.feature-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
}

.tag-icon {
  font-size: 1.1rem;
}

/* 装饰元素 */
.hero-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.decoration-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.4;
}

.orb-1 {
  width: 300px;
  height: 300px;
  background: var(--primary-color);
  top: 20%;
  left: 10%;
  animation: float-orb-1 15s infinite ease-in-out;
}

.orb-2 {
  width: 200px;
  height: 200px;
  background: var(--secondary-color);
  top: 60%;
  right: 15%;
  animation: float-orb-2 12s infinite ease-in-out;
}

.orb-3 {
  width: 150px;
  height: 150px;
  background: var(--accent-color);
  bottom: 20%;
  left: 60%;
  animation: float-orb-3 18s infinite ease-in-out;
}

@keyframes float-orb-1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

@keyframes float-orb-2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(-40px, -20px) scale(1.2); }
}

@keyframes float-orb-3 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(20px, -40px) scale(0.8); }
  75% { transform: translate(-30px, 10px) scale(1.1); }
}

/* 滚动指示器 */
.scroll-indicator {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.3s ease;
}

.scroll-indicator:hover {
  opacity: 1;
}

.scroll-arrow {
  width: 24px;
  height: 24px;
  border-right: 2px solid var(--text-secondary);
  border-bottom: 2px solid var(--text-secondary);
  transform: rotate(45deg);
  animation: bounce-arrow 2s infinite;
}

.scroll-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

@keyframes bounce-arrow {
  0%, 100% { transform: rotate(45deg) translateY(0); }
  50% { transform: rotate(45deg) translateY(5px); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .primary-action,
  .secondary-action {
    width: 100%;
    max-width: 300px;
  }
  
  .hero-features {
    flex-direction: column;
    align-items: center;
  }
  
  .feature-tag {
    width: 100%;
    max-width: 200px;
    justify-content: center;
  }
  
  .decoration-orb {
    display: none;
  }
}

/* 动画优化 */
@media (prefers-reduced-motion: reduce) {
  .particles-bg,
  .decoration-orb,
  .scroll-indicator {
    animation: none;
  }
}
</style>