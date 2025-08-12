<template>
  <div id="vue-odoo-app" class="vue-app vue-isolated-app">
    <main class="vue-main">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showNavigation = ref(true) //router тогл 

const navRoutes = computed(() => {
  return router.getRoutes()
    .filter(route => route.meta?.title && route.path !== '/' && route.name !== 'Plans-Alt')
    .sort((a, b) => {
      const order = { 'dashboard': 1, 'plans': 2, 'components': 3 }
      const aOrder = order[a.name?.toLowerCase()] || 999
      const bOrder = order[b.name?.toLowerCase()] || 999
      return aOrder - bOrder
    })
})
</script>

<style scoped>
.vue-app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #333;
  background: #f8f9fa;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.vue-nav {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  color: white;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.nav-brand h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: white;
}

.nav-menu {
  display: flex;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.2s ease;
  font-weight: 500;
  font-size: 14px;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item--active {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.nav-icon {
  font-size: 16px;
}

.nav-label {
  font-weight: 500;
}

.vue-main {
  flex: 1;
  overflow: hidden;
  background: #f8fafc;
}

@media (max-width: 768px) {
  .vue-nav {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
  }
  
  .nav-menu {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .nav-item {
    font-size: 13px;
    padding: 6px 12px;
  }
}
</style>