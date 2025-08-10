import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'

import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import Plans from './components/Plans.vue'

// Импорт утилит для Odoo
import { odooService } from './utils/odoo-service.js'

// Конфигурация роутера с логичной структурой
const routes = [
  { path: '/', redirect: '/dashboard' },
  { 
    path: '/dashboard', 
    component: Dashboard, 
    name: 'Dashboard',
    meta: { title: 'Аналитика продаж', icon: '📊' }
  },
  { 
    path: '/plans', 
    component: Plans, 
    name: 'Plans',
    meta: { title: 'Настройки планов', icon: '⚙️' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// Удалена зависимость от Pinia - используем localStorage

// Глобальная функция для создания Vue приложения в Odoo
window.createVueOdooApp = function(mountElement, initialRoute = 'dashboard') {
  const app = createApp(App)
  
  // Подключаем плагины
  app.use(router)
  
  // Глобальные свойства для интеграции с Odoo
  app.config.globalProperties.$odoo = odooService
  app.provide('odoo', odooService)
  
  // Глобальные компоненты
  app.component('Plans', Plans)
  app.component('Dashboard', Dashboard)
  
  // Переходим на нужную страницу
  router.push(`/${initialRoute}`)
  
  // Монтируем приложение
  const vueInstance = app.mount(mountElement)
  
  console.log(`✓ Vue приложение запущено: ${initialRoute}`)
  console.log(`✓ Доступные маршруты:`, routes.map(r => r.path))
  
  return vueInstance
}

// Настройка роутера
router.beforeEach((to, from, next) => {
  // Устанавливаем заголовок страницы
  if (to.meta?.title) {
    document.title = `${to.meta.title} - SMK Analytics`
  }
  
  console.log(`📍 Переход: ${from.path} → ${to.path}`)
  next()
})

// Обработка ошибок роутера
router.onError((error) => {
  console.error('❌ Ошибка роутера:', error)
})

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
  console.log('Vue.js integration для Odoo готов')
  console.log('🚀 Основной компонент: Dashboard (аналитика), дополнительные: Plans (настройки)')
})

export { router }
