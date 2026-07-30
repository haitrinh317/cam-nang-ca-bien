import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  // Multi-page app: mỗi HTML là 1 entry point
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        browse: resolve(__dirname, 'browse.html'),
        species: resolve(__dirname, 'species.html'),
        tap: resolve(__dirname, 'tap.html'),
      },
    },
    outDir: 'dist',
  },
  // Dev server
  server: {
    port: 3000,
    open: true,
  },
})
