import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store' 
import axios from 'axios'
import VueToast from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-default.css'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap/dist/js/bootstrap.js'
import 'bootstrap-icons/font/bootstrap-icons.css' 

const app = createApp(App)

// Configure axios
axios.defaults.baseURL = 'http://127.0.0.1:8000'

const axiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000',
})

axiosInstance.interceptors.request.use(
  (config) => {
    const token = store.state.token
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response && error.response.status === 401) {
      // Token has expired
      await store.dispatch('logout')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

app.config.globalProperties.$axios = axiosInstance
app.config.globalProperties.$toast = app.use(VueToast).config.globalProperties.$toast

app.use(store) 
app.use(router)
app.mount('#app')

// Check authentication status when app starts
store.dispatch('checkAuth')