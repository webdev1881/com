<template>
  <div class="plans-editor">
    <div class="plans-header">
      <h2>🎯 Редактирование Целевых Показателей</h2>
      <div class="plans-actions">
        <button @click="resetToDefaults" class="btn btn-secondary">
          🔄 Сбросить к умолчанию
        </button>
        <button @click="saveChanges" class="btn btn-primary" :disabled="!hasChanges">
          💾 Сохранить изменения
        </button>
        <button @click="$emit('close')" class="btn btn-close">
          ✕ Закрыть
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Загрузка данных...</p>
    </div>

    <div v-else-if="error" class="error">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
      <button @click="loadData" class="btn btn-primary">Попробовать снова</button>
    </div>

    <div v-else class="plans-content">
      <!-- Общие настройки показателей -->
      <div class="plans-section">
        <h3>📊 Настройка Показателей</h3>
        <div class="targets-grid">
          <div 
            v-for="(target, key) in targetsData.targetTree" 
            :key="key" 
            class="target-card"
            :class="{ 'target-negative': target.type === 'negative' }"
          >
            <div class="target-header">
              <h4>{{ target.name }}</h4>
              <span class="target-type">
                {{ target.type === 'negative' ? '📉 Негативный' : '📈 Позитивный' }}
              </span>
            </div>
            <div class="target-score">
              <label>Максимальный балл:</label>
              <input 
                type="number" 
                v-model.number="targetsData.targetTree[key].maxScore"
                @input="markAsChanged"
                min="1"
                max="200"
                class="score-input"
              >
            </div>
          </div>
        </div>
      </div>

      <!-- Настройки по магазинам -->
      <div class="plans-section">
        <h3>🏪 Целевые Показатели по Магазинам</h3>
        
        <div class="filters">
          <input 
            type="text" 
            v-model="searchStore" 
            placeholder="🔍 Поиск магазина..."
            class="search-input"
          >
          <select v-model="selectedTarget" class="target-filter">
            <option value="">Все показатели</option>
            <option v-for="(target, key) in targetsData.targetTree" :key="key" :value="key">
              {{ target.name }}
            </option>
          </select>
        </div>

        <div class="stores-table">
          <div class="table-header">
            <div class="store-name">Магазин</div>
            <div v-for="(target, key) in filteredTargets" :key="key" class="target-column">
              {{ target.name }}
              <small>({{ target.type === 'negative' ? 'мин.' : 'макс.' }})</small>
            </div>
          </div>

          <div 
            v-for="(storeTargets, storeId) in filteredStores" 
            :key="storeId" 
            class="table-row"
          >
            <div class="store-name">
              <div class="store-info">
                <span class="store-id">ID: {{ storeId }}</span>
                <span class="store-full-name">{{ getStoreName(storeId) }}</span>
              </div>
            </div>
            <div 
              v-for="(target, key) in filteredTargets" 
              :key="key" 
              class="target-value"
            >
              <input 
                type="number" 
                v-model.number="targetsData.storeTargets[storeId][key]"
                @input="markAsChanged"
                :step="getInputStep(key)"
                :min="0"
                :max="1"
                class="target-input"
                :class="{ 'negative-target': target.type === 'negative' }"
              >
              <span class="target-percent">
                {{ (targetsData.storeTargets[storeId][key] * 100).toFixed(3) }}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Быстрые действия -->
      <div class="plans-section">
        <h3>⚡ Быстрые Действия</h3>
        <div class="quick-actions">
          <div class="action-group">
            <h4>Применить ко всем магазинам:</h4>
            <div class="bulk-inputs">
              <div v-for="(target, key) in targetsData.targetTree" :key="key" class="bulk-input">
                <label>{{ target.name }}:</label>
                <div class="input-group">
                  <input 
                    type="number" 
                    v-model.number="bulkValues[key]"
                    :step="getInputStep(key)"
                    :min="0"
                    :max="1"
                    class="bulk-value-input"
                  >
                  <button @click="applyBulkValue(key)" class="btn btn-small">
                    Применить
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="action-group">
            <h4>Статистика:</h4>
            <div class="stats">
              <div class="stat-item">
                <span class="stat-label">Всего магазинов:</span>
                <span class="stat-value">{{ Object.keys(targetsData.storeTargets).length }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Показателей:</span>
                <span class="stat-value">{{ Object.keys(targetsData.targetTree).length }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Изменений:</span>
                <span class="stat-value" :class="{ 'has-changes': hasChanges }">
                  {{ hasChanges ? 'Есть несохраненные' : 'Нет изменений' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно подтверждения -->
    <div v-if="showConfirmModal" class="modal-overlay" @click="cancelReset">
      <div class="modal" @click.stop>
        <h3>🔄 Сброс к настройкам по умолчанию</h3>
        <p>Вы уверены, что хотите сбросить все изменения и вернуться к настройкам по умолчанию?</p>
        <div class="modal-actions">
          <button @click="cancelReset" class="btn btn-secondary">Отмена</button>
          <button @click="confirmReset" class="btn btn-danger">Сбросить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// События компонента
const emit = defineEmits(['close'])

// Реактивные данные
const loading = ref(true)
const error = ref(null)
const targetsData = ref({
  targetTree: {},
  storeTargets: {}
})
const originalData = ref(null)
const hasChanges = ref(false)
const searchStore = ref('')
const selectedTarget = ref('')
const bulkValues = ref({})
const showConfirmModal = ref(false)

// Получение имени магазина по ID
const getStoreName = (storeId) => {
  // В реальном приложении здесь будет поиск в данных продаж
  const storeNames = {
    '1': '108 Киев (РУЛЬКА)',
    '2': '001 Днепр (РУЛЬКА)',
    '3': '102 БЦ (РУЛЬКА)',
    '4': '101 БЦ (ЩЕДРИК)',
    '5': '240 Богодухов (РУЛЬКА)',
    '6': '230 Чугуев (РУЛЬКА)',
    '7': '222 Лозовая (РУЛЬКА)',
    '8': '220 Ольшаны (РУЛЬКА)',
    '9': '267 Пересичное (РУЛЬКА)',
    '10': '229 Красноград (РУЛЬКА)',
    '11': '199 Первомайский (РУЛЬКА)',
    '12': '235 Харьков (РУЛЬКА)',
    '13': '282 Максимовка (ЩЕДРИК)',
    '14': '271 Горького (ЩЕДРИК)',
    '15': '210 Люботин (ЩЕДРИК)',
    '16': '100 БЦ (РУЛЬКА)'
  }
  return storeNames[storeId] || `Магазин ${storeId}`
}

// Шаг для полей ввода
const getInputStep = (targetKey) => {
  return targetKey === 'unprocessed' ? 0.0000001 : 0.00001
}

// Фильтрованные данные
const filteredTargets = computed(() => {
  if (!selectedTarget.value) {
    return targetsData.value.targetTree
  }
  return {
    [selectedTarget.value]: targetsData.value.targetTree[selectedTarget.value]
  }
})

const filteredStores = computed(() => {
  if (!searchStore.value) {
    return targetsData.value.storeTargets
  }
  
  const filtered = {}
  Object.keys(targetsData.value.storeTargets).forEach(storeId => {
    const storeName = getStoreName(storeId)
    if (storeName.toLowerCase().includes(searchStore.value.toLowerCase()) ||
        storeId.includes(searchStore.value)) {
      filtered[storeId] = targetsData.value.storeTargets[storeId]
    }
  })
  return filtered
})

// Ключ для localStorage
const STORAGE_KEY = 'targetsData'

// Загрузка данных
const loadData = async () => {
  try {
    loading.value = true
    error.value = null

    // Проверяем сохраненные данные в localStorage
    const savedData = getSavedData()
    
    if (savedData) {
      targetsData.value = savedData
      console.log('✓ Загружены сохраненные данные из localStorage')
    } else {
      // Загружаем данные по умолчанию из targets.json
      const response = await fetch('/com/static/data/targets.json')
      if (!response.ok) {
        throw new Error(`Ошибка загрузки: ${response.status}`)
      }
      
      const defaultData = await response.json()
      targetsData.value = defaultData
      
      // Сохраняем в localStorage как базовые настройки
      saveData(defaultData)
      console.log('✓ Загружены данные по умолчанию из targets.json')
    }

    // Сохраняем копию оригинальных данных
    originalData.value = JSON.parse(JSON.stringify(targetsData.value))
    
    // Инициализируем значения для массовых изменений
    initBulkValues()
    
  } catch (err) {
    console.error('❌ Ошибка загрузки данных:', err)
    error.value = err.message || 'Ошибка загрузки данных'
  } finally {
    loading.value = false
  }
}

// Работа с localStorage
const getSavedData = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved ? JSON.parse(saved) : null
  } catch (err) {
    console.error('❌ Ошибка чтения localStorage:', err)
    return null
  }
}

const saveData = (data) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    console.log('✓ Данные сохранены в localStorage')
    return true
  } catch (err) {
    console.error('❌ Ошибка сохранения в localStorage:', err)
    return false
  }
}

// Инициализация значений для массовых изменений
const initBulkValues = () => {
  Object.keys(targetsData.value.targetTree).forEach(key => {
    bulkValues.value[key] = 0.001
  })
}

// Отметка об изменениях
const markAsChanged = () => {
  hasChanges.value = true
}

// Применение массового значения
const applyBulkValue = (targetKey) => {
  const value = bulkValues.value[targetKey]
  if (value === undefined || value === null) return

  Object.keys(targetsData.value.storeTargets).forEach(storeId => {
    targetsData.value.storeTargets[storeId][targetKey] = value
  })
  
  markAsChanged()
  console.log(`✓ Применено значение ${value} для ${targetKey} ко всем магазинам`)
}

// Сохранение изменений
const saveChanges = () => {
  if (!hasChanges.value) return

  const success = saveData(targetsData.value)
  
  if (success) {
    hasChanges.value = false
    
    // Отправляем событие об обновлении данных
    emitDataUpdate()
    
    console.log('✅ Изменения сохранены успешно')
    
    // Показываем уведомление
    showNotification('Изменения сохранены!', 'success')
  } else {
    showNotification('Ошибка сохранения!', 'error')
  }
}

// Отправка события об обновлении данных
const emitDataUpdate = () => {
  // Создаем событие для Dashboard компонента
  const event = new CustomEvent('plansDataUpdated', {
    detail: targetsData.value
  })
  window.dispatchEvent(event)
  
  console.log('📡 Отправлено событие обновления данных')
}

// Сброс к настройкам по умолчанию
const resetToDefaults = () => {
  showConfirmModal.value = true
}

const confirmReset = async () => {
  try {
    loading.value = true
    showConfirmModal.value = false
    
    // Удаляем данные из localStorage
    localStorage.removeItem(STORAGE_KEY)
    
    // Загружаем оригинальные данные
    const response = await fetch('/com/static/data/targets.json')
    const defaultData = await response.json()
    
    targetsData.value = defaultData
    originalData.value = JSON.parse(JSON.stringify(defaultData))
    hasChanges.value = false
    
    // Сохраняем как новые базовые настройки
    saveData(defaultData)
    
    // Уведомляем Dashboard об изменениях
    emitDataUpdate()
    
    console.log('🔄 Данные сброшены к настройкам по умолчанию')
    showNotification('Данные сброшены к настройкам по умолчанию', 'info')
    
  } catch (err) {
    console.error('❌ Ошибка сброса данных:', err)
    error.value = 'Ошибка сброса данных'
    showNotification('Ошибка сброса данных!', 'error')
  } finally {
    loading.value = false
  }
}

const cancelReset = () => {
  showConfirmModal.value = false
}

// Показ уведомлений
const showNotification = (message, type = 'info') => {
  // Простая реализация уведомлений
  const notification = document.createElement('div')
  notification.className = `notification notification-${type}`
  notification.textContent = message
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    border-radius: 6px;
    color: white;
    font-weight: 600;
    z-index: 10000;
    animation: slideInRight 0.3s ease;
    background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
  `
  
  document.body.appendChild(notification)
  
  setTimeout(() => {
    notification.remove()
  }, 3000)
}

// Отслеживание изменений с клавиатуры
const handleKeydown = (event) => {
  if (event.ctrlKey && event.key === 's') {
    event.preventDefault()
    saveChanges()
  }
  if (event.key === 'Escape') {
    emit('close')
  }
}

// Lifecycle hooks
onMounted(() => {
  loadData()
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.plans-editor {
  width: 100%;
  height: 100vh;
  overflow-y: auto;
  background: #f8fafc;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.plans-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: white;
  border-bottom: 2px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.plans-header h2 {
  margin: 0;
  color: #1e293b;
  font-size: 20px;
  font-weight: 700;
}

.plans-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: 1px solid transparent;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-close {
  background: #f1f5f9;
  color: #64748b;
  border-color: #cbd5e1;
}

.btn-close:hover {
  background: #e2e8f0;
  color: #475569;
}

.btn-small {
  padding: 4px 8px;
  font-size: 12px;
}

.loading, .error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  padding: 40px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  color: #dc2626;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.plans-content {
  padding: 24px;
}

.plans-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.plans-section h3 {
  margin: 0 0 20px 0;
  color: #1e293b;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 2px solid #f1f5f9;
  padding-bottom: 12px;
}

.targets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.target-card {
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  background: #f8fafc;
  transition: all 0.2s ease;
}

.target-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.target-negative {
  border-color: #f59e0b;
  background: #fffbeb;
}

.target-negative:hover {
  border-color: #d97706;
}

.target-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.target-header h4 {
  margin: 0;
  color: #1e293b;
  font-size: 16px;
  font-weight: 600;
}

.target-type {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.target-score {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.target-score label {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.score-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  text-align: center;
  color: #1e293b;
}

.score-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-input, .target-filter {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  min-width: 200px;
}

.search-input:focus, .target-filter:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.stores-table {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.table-header, .table-row {
  display: grid;
  grid-template-columns: 250px repeat(auto-fit, minmax(120px, 1fr));
  gap: 1px;
  background: #e2e8f0;
}

.table-header {
  background: #f1f5f9;
  font-weight: 600;
  color: #374151;
}

.table-header > div, .table-row > div {
  padding: 12px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.table-header .store-name {
  justify-content: flex-start;
  font-weight: 700;
  color: #1e293b;
}

.table-row .store-name {
  justify-content: flex-start;
  background: #f8fafc;
}

.store-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.store-id {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.store-full-name {
  font-size: 14px;
  color: #1e293b;
  font-weight: 600;
}

.target-column {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.target-column small {
  color: #64748b;
  font-weight: 400;
  font-size: 11px;
}

.target-value {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.target-input {
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 13px;
  text-align: center;
  width: 100%;
}

.target-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.negative-target {
  border-color: #f59e0b;
  background: #fffbeb;
}

.negative-target:focus {
  border-color: #d97706;
  box-shadow: 0 0 0 2px rgba(217, 119, 6, 0.1);
}

.target-percent {
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
}

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.action-group h4 {
  margin: 0 0 16px 0;
  color: #1e293b;
  font-size: 16px;
  font-weight: 600;
}

.bulk-inputs {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bulk-input {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bulk-input label {
  min-width: 120px;
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.input-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.bulk-value-input {
  padding: 6px 10px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  width: 100px;
  text-align: center;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.has-changes {
  color: #f59e0b !important;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}

.modal h3 {
  margin: 0 0 16px 0;
  color: #1e293b;
  font-size: 18px;
  font-weight: 600;
}

.modal p {
  margin: 0 0 20px 0;
  color: #64748b;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .plans-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .plans-actions {
    justify-content: center;
  }

  .table-header, .table-row {
    grid-template-columns: 200px repeat(auto-fit, minmax(100px, 1fr));
  }

  .quick-actions {
    grid-template-columns: 1fr;
  }

  .filters {
    flex-direction: column;
  }

  .search-input, .target-filter {
    min-width: auto;
    width: 100%;
  }
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
