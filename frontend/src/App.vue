<template>
  <div id="app">
    <header class="app-header">
      <h1>图宝 - AI小红书图文生成器</h1>
      <p class="subtitle">一句话生成完整小红书图文</p>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <p>© 2024 图宝. 让创作更简单.</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
// 应用根组件
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}

.app-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 600;
}

.subtitle {
  margin: 0.5rem 0 0;
  opacity: 0.9;
  font-size: 1rem;
}

.app-main {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.app-footer {
  background: #f5f5f5;
  padding: 1rem;
  text-align: center;
  color: #666;
}

.app-footer p {
  margin: 0;
}
</style>