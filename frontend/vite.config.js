import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://111.231.28.98:8000',
        changeOrigin: true,
      },
    },
    host:'0.0.0.0',
    port: 3001,
  },
}) 