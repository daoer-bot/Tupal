<template>
  <div class="hero-section">
    <!-- 粒子背景 -->
    <ParticlesBackground class="particles-bg" />
    
    <!-- 装饰光晕 -->
    <div class="hero-decoration">
      <div class="decoration-orb orb-1 breathing-glow"></div>
      <div class="decoration-orb orb-2 breathing-glow"></div>
      <div class="decoration-orb orb-3 breathing-glow"></div>
    </div>

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
          <span>开始创作</span>
          <div class="btn-shine"></div>
        </button>
        <button class="btn-ghost secondary-action" @click="showDemo">
          <span class="btn-icon">▶</span>
          <span>观看演示</span>
        </button>
      </div>
      
      <!-- 特性标签 -->
      <div class="hero-features">
        <div class="feature-tag glass-card-premium" style="--delay: 0s">
          <div class="tag-icon">⚡</div>
          <span>3秒生成</span>
        </div>
        <div class="feature-tag glass-card-premium" style="--delay: 0.1s">
          <div class="tag-icon">🎨</div>
          <span>风格一致</span>
        </div>
        <div class="feature-tag glass-card-premium" style="--delay: 0.2s">
          <div class="tag-icon">🔥</div>
          <span>热点追踪</span>
        </div>
      </div>
    </div>
    
    <!-- 滚动指示器 -->
    <div class="scroll-indicator" @click="scrollToNext">
      <div class="scroll-arrow"></div>
      <span class="scroll-text">向下探索</span>
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
    rgba(99, 102, 241, 0.05) 0%,
    rgba(236, 72, 153, 0.05) 50%,
    rgba(139, 92, 246, 0.05) 100%
  );
}

.particles-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  opacity: 0.6;
}

.hero-content {
  position: relative;
  z-index: 10;
  text-align: center;
  max-width: 900px;
  padding: 0 2rem;
}

/* 徽章样式 */
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  margin-bottom: 2.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--primary-color);
  border-radius: 50px;
  background: var(--glass-surface-hover);
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.15);
}

.badge-icon {
  font-size: 1.2rem;
  animation: sparkle 2s infinite;
}

@keyframes sparkle {
  0%, 100% { transform: scale(1) rotate(0deg); }
  50% { transform: scale(1.2) rotate(180deg); }
}

.animate-float {
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 标题样式 */
.hero-title {
  font-size: 4.5rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  letter-spacing: -0.03em;
}

.text-gradient-animated {
  background: linear-gradient(
    135deg,
    var(--primary-color),
    var(--secondary-color),
    var(--accent-color),
    var(--primary-color)
  );
  background-size: 300% 300%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradient-shift 6s ease infinite;
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 副标题样式 */
.hero-subtitle {
  font-size: 1.25rem;
  color: var(--text-secondary);
  margin-bottom: 3.5rem;
  line-height: 1.6;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  font-weight: 500;
}

/* 按钮组样式 */
.hero-actions {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  margin-bottom: 4rem;
  flex-wrap: wrap;
}

.primary-action {
  padding: 1.125rem 2.5rem;
  font-size: 1.1rem;
  border-radius: 16px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.primary-action:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 12px 32px rgba(99, 102, 241, 0.4);
}

.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  transform: skewX(-20deg);
  animation: shine 4s infinite;
}

@keyframes shine {
  0%, 80% { left: -100%; }
  100% { left: 200%; }
}

.secondary-action {
  padding: 1.125rem 2.5rem;
  font-size: 1.1rem;
  border-radius: 16px;
  background: var(--glass-surface);
  border: 1px solid var(--glass-border);
  color: var(--text-primary);
  backdrop-filter: blur(8px);
}

.secondary-action:hover {
  background: var(--glass-surface-hover);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.btn-icon {
  margin-right: 0.5rem;
  font-size: 1.2rem;
}

/* 特性标签 */
.hero-features {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.feature-tag {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  border-radius: 16px;
  background: var(--glass-surface);
  animation: slideUpFade 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
  opacity: 0;
  animation-delay: var(--delay);
}

@keyframes slideUpFade {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.tag-icon {
  font-size: 1.2rem;
}

/* 装饰元素 */
.hero-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 2;
}

.decoration-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  mix-blend-mode: screen;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: var(--primary-color);
  top: -10%;
  left: -5%;
  animation: float-orb-1 20s infinite ease-in-out;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: var(--secondary-color);
  bottom: 10%;
  right: 5%;
  animation: float-orb-2 15s infinite ease-in-out;
}

.orb-3 {
  width: 200px;
  height: 200px;
  background: var(--accent-color);
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: float-orb-3 18s infinite ease-in-out;
  opacity: 0.3;
}

@keyframes float-orb-1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(50px, -30px) scale(1.1); }
  66% { transform: translate(-20px, 40px) scale(0.9); }
}

@keyframes float-orb-2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(-40px, -50px) scale(1.2); }
}

@keyframes float-orb-3 {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  25% { transform: translate(-40%, -60%) scale(0.8); }
  75% { transform: translate(-60%, -40%) scale(1.1); }
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
  opacity: 0.6;
  transition: all 0.3s ease;
  z-index: 20;
}

.scroll-indicator:hover {
  opacity: 1;
  transform: translateX(-50%) translateY(-5px);
}

.scroll-arrow {
  width: 20px;
  height: 20px;
  border-right: 2px solid var(--text-secondary);
  border-bottom: 2px solid var(--text-secondary);
  transform: rotate(45deg);
  animation: bounce-arrow 2s infinite;
}

.scroll-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
  letter-spacing: 0.05em;
}

@keyframes bounce-arrow {
  0%, 100% { transform: rotate(45deg) translateY(0); }
  50% { transform: rotate(45deg) translateY(6px); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.75rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
    margin-bottom: 2.5rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  
  .primary-action,
  .secondary-action {
    width: 100%;
    max-width: 320px;
  }
  
  .feature-tag {
    width: 100%;
    justify-content: center;
  }
  
  .decoration-orb {
    opacity: 0.2;
  }
}

/* 动画优化 */
@media (prefers-reduced-motion: reduce) {
  .particles-bg,
  .decoration-orb,
  .scroll-indicator,
  .animate-float,
  .text-gradient-animated,
  .btn-shine {
    animation: none;
  }
}
</style>