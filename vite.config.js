import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
assetsInclude: ['**/*.otf', '**/*.ttf', '**/*.woff', '**/*.woff2']


export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE_PATH || '/vulnx',
  
  
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})


