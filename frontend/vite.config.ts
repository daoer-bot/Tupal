import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        // 代理到后端服务（后端端口在 backend/.env 中配置）
        target: 'http://localhost:5030',
        changeOrigin: true
      },
      '/uploads': {
        // 🔧 代理上传文件访问到后端
        target: 'http://localhost:5030',
        changeOrigin: true
      }
    }
  }
})