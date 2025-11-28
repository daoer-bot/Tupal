<template>
  <div class="process-steps">
    <div
      class="step"
      :class="{ active: currentStep >= 1, current: currentStep === 1, clickable: currentStep > 1 }"
      @click="handleStepClick(1)"
    >
      <div class="step-dot"></div>
      <div class="step-label">创意构思</div>
    </div>
    <div class="step-line" :class="{ active: currentStep >= 2 }"></div>
    <div
      class="step"
      :class="{ active: currentStep >= 2, current: currentStep === 2, clickable: currentStep > 2 }"
      @click="handleStepClick(2)"
    >
      <div class="step-dot"></div>
      <div class="step-label">内容大纲</div>
    </div>
    <div class="step-line" :class="{ active: currentStep >= 3 }"></div>
    <div
      class="step"
      :class="{ active: currentStep >= 3, current: currentStep === 3, clickable: currentStep > 3 }"
      @click="handleStepClick(3)"
    >
      <div class="step-dot"></div>
      <div class="step-label">生成结果</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAppStore } from '../store'

const props = defineProps<{
  currentStep: number
}>()

const router = useRouter()
const store = useAppStore()

const handleStepClick = (step: number) => {
  // 只能点击已经完成的步骤
  if (step >= props.currentStep) {
    return
  }
  
  // 根据步骤跳转
  if (step === 1) {
    router.push('/')
  } else if (step === 2) {
    // 只有当有大纲时才能跳转到文案页
    if (store.currentOutline) {
      router.push('/generator')
    }
  } else if (step === 3) {
    // 只有当有大纲时才能跳转到结果页
    if (store.currentOutline) {
      router.push('/result')
    }
  }
}
</script>

<style scoped>
.process-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  padding: 0.5rem 0;
}

.step {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 1;
  transition: var(--transition);
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-md);
}

.step.clickable {
  cursor: pointer;
}

.step.clickable:hover {
  background: var(--hover-bg);
}

.step.clickable:hover .step-label {
  color: var(--primary-color);
}

.step-dot {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  background: var(--border-color);
  transition: var(--transition);
  position: relative;
}

.step-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
  transition: var(--transition);
}

.step.active .step-dot {
  background: var(--primary-color);
  box-shadow: 0 0 0 3px var(--primary-light);
}

.step.active .step-label {
  color: var(--primary-color);
  font-weight: 600;
}

.step.current .step-dot {
  transform: scale(1.2);
}

.step-line {
  width: 3rem;
  height: 1px;
  background: var(--border-color);
  margin: 0 0.5rem;
  transition: var(--transition);
}

.step-line.active {
  background: var(--primary-color);
}
</style>