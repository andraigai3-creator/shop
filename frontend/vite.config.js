import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // base нужен для GitHub Pages — меняй на имя репозитория если деплоишь туда
  // Для Vercel оставь '/'
  base: '/shop/',
})
