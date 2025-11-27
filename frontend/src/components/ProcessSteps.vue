<template>
  <div class="process-steps">
    <div class="step" :class="{ active: currentStep >= 1, current: currentStep === 1 }">
      <div class="step-icon">1</div>
      <div class="step-label">创意</div>
    </div>
    <div class="step-line" :class="{ active: currentStep >= 2 }"></div>
    <div class="step" :class="{ active: currentStep >= 2, current: currentStep === 2 }">
      <div class="step-icon">2</div>
      <div class="step-label">文案</div>
    </div>
    <div class="step-line" :class="{ active: currentStep >= 3 }"></div>
    <div class="step" :class="{ active: currentStep >= 3, current: currentStep === 3 }">
      <div class="step-icon">3</div>
      <div class="step-label">图文</div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  currentStep: number
}>()
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