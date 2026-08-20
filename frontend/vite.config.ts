import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/simulate': 'http://localhost:8000',
      '/recover': 'http://localhost:8000',
      '/graph': 'http://localhost:8000',
      '/resilience': 'http://localhost:8000',
      '/cross-training': 'http://localhost:8000',
    },
  },
})
