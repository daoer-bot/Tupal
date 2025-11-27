<template>
  <div class="process-steps">
    <div
      class="step"
      :class="{ active: currentStep >= 1, current: currentStep === 1, clickable: currentStep > 1 }"
      @click="handleStepClick(1)"
    >
      <div class="step-icon">1</div>
      <div class="step-label">创意</div>
    </div>
    <div class="step-line" :class="{ active: currentStep >= 2 }"></div>
    <div
      class="step"
      :class="{ active: currentStep >= 2, current: currentStep === 2, clickable: currentStep > 2 }"
      @click="handleStepClick(2)"
    >
      <div class="step-icon">2</div>
      <div class="step-label">文案</div>
    </div>
    <div class="step-line" :class="{ active: currentStep >= 3 }"></div>
    <div
      class="step"
      :class="{ active: currentStep >= 3, current: currentStep === 3, clickable: currentStep > 3 }"
      @click="handleStepClick(3)"
    >
      <div class="step-icon">3</div>
      <div class="step-label">图文</div>
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
  margin-bottom: 2rem;
  padding: 1rem 0;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 1;
  transition: var(--transition);
}

.step.clickable {
  cursor: pointer;
}

.step.clickable:hover .step-icon {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.step.clickable:hover .step-label {
  color: var(--primary-color);
}

.step-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: var(--surface-color);
  border: 2px solid var(--border-color);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: var(--transition);
}

.step-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
  transition: var(--transition);
}

.step.active .step-icon {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.step.active .step-label {
  color: var(--primary-color);
}

.step.current .step-icon {
  box-shadow: 0 0 0 4px var(--primary-light);
}

.step-line {
  flex: 0 0 60px;
  height: 2px;
  background: var(--border-color);
  margin: 0 0.5rem 1.5rem;
  transition: var(--transition);
}

.step-line.active {
  background: var(--primary-color);
}
</style>