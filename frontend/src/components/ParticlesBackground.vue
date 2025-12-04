<template>
  <div class="particles-container" ref="particlesContainer">
    <div 
      v-for="(particle, index) in particles" 
      :key="index"
      class="particle"
      :style="{
        left: particle.x + '%',
        top: particle.y + '%',
        width: particle.size + 'px',
        height: particle.size + 'px',
        background: particle.color,
        animationDelay: particle.delay + 's',
        animationDuration: particle.duration + 's'
      }"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Particle {
  x: number
  y: number
  size: number
  color: string
  delay: number
  duration: number
  speed: number
}

const particlesContainer = ref<HTMLElement>()
const particles = ref<Particle[]>([])
let animationFrame: number | null = null

// 生成随机粒子
const generateParticles = (count: number = 50) => {
  const colors = [
    'rgba(99, 102, 241, 0.6)',   // 靛蓝
    'rgba(236, 72, 153, 0.6)',   // 霓虹粉
    'rgba(139, 92, 246, 0.6)',   // 梦幻紫
    'rgba(16, 185, 129, 0.6)',   // 翡翠绿
    'rgba(245, 158, 11, 0.6)',   // 琥珀黄
  ]

  const newParticles: Particle[] = []
  
  for (let i = 0; i < count; i++) {
    newParticles.push({
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 6 + 2,
      color: colors[Math.floor(Math.random() * colors.length)],
      delay: Math.random() * 5,
      duration: Math.random() * 10 + 10,
      speed: Math.random() * 0.5 + 0.2
    })
  }
  
  particles.value = newParticles
}

// 粒子动画
const animateParticles = () => {
  particles.value.forEach(particle => {
    // 缓慢移动粒子
    particle.x += (Math.random() - 0.5) * 0.1
    particle.y += particle.speed * 0.1
    
    // 边界检测
    if (particle.x > 100) particle.x = 0
    if (particle.x < 0) particle.x = 100
    if (particle.y > 100) particle.y = 0
    if (particle.y < 0) particle.y = 100
  })
  
  animationFrame = requestAnimationFrame(animateParticles)
}

// 鼠标交互效果
const handleMouseMove = (event: MouseEvent) => {
  if (!particlesContainer.value) return
  
  const rect = particlesContainer.value.getBoundingClientRect()
  const mouseX = ((event.clientX - rect.left) / rect.width) * 100
  const mouseY = ((event.clientY - rect.top) / rect.height) * 100
  
  // 让附近的粒子向鼠标位置轻微移动
  particles.value.forEach(particle => {
    const distance = Math.sqrt(
      Math.pow(particle.x - mouseX, 2) + Math.pow(particle.y - mouseY, 2)
    )
    
    if (distance < 20) {
      const force = (20 - distance) / 20
      const angle = Math.atan2(particle.y - mouseY, particle.x - mouseX)
      particle.x += Math.cos(angle) * force * 0.5
      particle.y += Math.sin(angle) * force * 0.5
    }
  })
}

// 点击创建新粒子
const handleClick = (event: MouseEvent) => {
  if (!particlesContainer.value) return
  
  const rect = particlesContainer.value.getBoundingClientRect()
  const clickX = ((event.clientX - rect.left) / rect.width) * 100
  const clickY = ((event.clientY - rect.top) / rect.height) * 100
  
  // 在点击位置创建新粒子
  const colors = [
    'rgba(99, 102, 241, 0.8)',
    'rgba(236, 72, 153, 0.8)',
    'rgba(139, 92, 246, 0.8)',
  ]
  
  for (let i = 0; i < 5; i++) {
    particles.value.push({
      x: clickX + (Math.random() - 0.5) * 10,
      y: clickY + (Math.random() - 0.5) * 10,
      size: Math.random() * 8 + 4,
      color: colors[Math.floor(Math.random() * colors.length)],
      delay: 0,
      duration: Math.random() * 3 + 2,
      speed: Math.random() * 2 + 1
    })
  }
  
  // 限制粒子数量
  if (particles.value.length > 100) {
    particles.value = particles.value.slice(-100)
  }
}

onMounted(() => {
  generateParticles(30)
  animateParticles()
  
  if (particlesContainer.value) {
    particlesContainer.value.addEventListener('mousemove', handleMouseMove)
    particlesContainer.value.addEventListener('click', handleClick)
  }
})

onUnmounted(() => {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
  }
  
  if (particlesContainer.value) {
    particlesContainer.value.removeEventListener('mousemove', handleMouseMove)
    particlesContainer.value.removeEventListener('click', handleClick)
  }
})
</script>

<style scoped>
.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: all;
  z-index: -1;
}

.particle {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  animation: particle-float infinite ease-in-out;
  will-change: transform;
}

@keyframes particle-float {
  0%, 100% {
    transform: translateY(0) scale(1);
    opacity: 0.8;
  }
  50% {
    transform: translateY(-20px) scale(1.1);
    opacity: 1;
  }
}

/* 粒子消失动画 */
.particle:not(:last-child) {
  animation: particle-float infinite ease-in-out, 
             particle-fade-out 2s ease-out forwards;
}

@keyframes particle-fade-out {
  0% {
    opacity: 0.8;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(0.5);
  }
}

/* 响应式优化 */
@media (max-width: 768px) {
  .particles-container {
    display: none;
  }
}
</style>
