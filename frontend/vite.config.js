import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  // Base path according to repo name for GitHub Pages
  base: '/AI-Flight-Guardian/',
  plugins: [react()],
})
