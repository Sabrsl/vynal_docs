import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Import global styles
import './styles/base.scss'

// Create and mount the app
const app = createApp(App)

// Use plugins
app.use(router)

// Mount the app
app.mount('#app') 