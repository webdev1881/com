import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import Plans from './components/Plans.vue'
import { odooService } from './utils/odoo-service.js'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { 
    path: '/dashboard', 
    component: Dashboard,  
    name: 'Dashboard',
    meta: { title: 'Компасс', icon: '📊' }
  },
  { 
    path: '/plans', 
    component: Plans, 
    name: 'Plans',
    meta: { title: 'Цільові Показники', icon: '⚙️' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

window.createVueOdooApp = function(mountElement, initialRoute = 'dashboard') {
  const app = createApp(App)
  app.use(router)
  app.config.globalProperties.$odoo = odooService
  app.provide('odoo', odooService)
  app.component('Plans', Plans)
  app.component('Dashboard', Dashboard)
  router.push(`/${initialRoute}`)
  const vueInstance = app.mount(mountElement)
  return vueInstance
}

router.beforeEach((to, from, next) => {
  if (to.meta?.title) {
    document.title = `${to.meta.title} - SMK Analytics`
  }
  next()
})


router.onError((error) => {
  console.error('Ошибка:', error)
})


document.addEventListener('DOMContentLoaded', () => {
})

export { router }
