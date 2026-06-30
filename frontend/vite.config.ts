import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 80,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 转发真实的客户端IP
            const clientIp = req.socket.remoteAddress || '127.0.0.1'
            // 处理IPv6回环地址
            const finalIp = clientIp === '::1' ? '127.0.0.1' : clientIp
            console.log(`[API Proxy] 请求: ${req.method} ${req.url} 来自: ${finalIp}`)
            // 添加X-Forwarded-For头
            proxyReq.setHeader('X-Forwarded-For', finalIp)
          })
        }
      },
      '/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            const clientIp = req.socket.remoteAddress || '127.0.0.1'
            const finalIp = clientIp === '::1' ? '127.0.0.1' : clientIp
            proxyReq.setHeader('X-Forwarded-For', finalIp)
          })
        }
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})
