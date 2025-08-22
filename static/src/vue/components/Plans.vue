<template>
  <div class="plans-editor">
    <div class="plans-header">
      <div class="header_title">
        <h2>Редагування Цільових Показників</h2>
        <button @click="saveChanges" class="btn btn-primary" :disabled="!hasChanges">
          Зберегти
        </button>
      </div>
      <div class="plans-actions">
        <button @click="resetToDefaults" class="btn btn-secondary">
          Скинути
        </button>
        <!-- <button @click="downloadTemplate" class="btn btn-info">
          Шаблон Excel
        </button> -->
        <label class="btn btn-upload">
          Завантажити з Excel
          <input 
            type="file" 
            ref="fileInput"
            @change="handleFileUpload" 
            accept=".xlsx,.xls" 
            style="display: none;"
          >
        </label>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Завантаження...</p>
    </div>

    <div v-else-if="error" class="error">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
      <button @click="loadData" class="btn btn-primary">Спробувати ще</button>
    </div>

    <div v-else class="plans-content">
      <div class="plans-section">
        <h3>Налаштування основних балів</h3>
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
                {{ target.type === 'negative' ? '📉 Негативний' : '📈 Позитивний' }}
              </span>
            </div>
            <div class="target-score">
              <label>Максимальний бал:</label>
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

      <div class="plans-section">
        <h3>Цільові Показники по Магазинам</h3>
        
        <div class="filters">
          <img src="../../../icons/srch.png" alt="" class="inp_search">
          <input 
            type="text" 
            v-model="searchStore" 
            placeholder="Пошук магазину..."
            class="search-input"
          >
          <select v-model="selectedTarget" class="target-filter">
            <option value="">Всі показники</option>
            <option v-for="(target, key) in targetsData.targetTree" :key="key" :value="key">
              {{ target.name }}
            </option>
          </select>
        </div>

        <div class="stores-table">
          <div class="table-header">
            <div class="store-name">Магазин</div>
            <div v-for="(target, key) in filteredObj" :key="key" class="target-column">
              {{ target.name }}
              <small>({{ target.type === 'negative' ? 'мін.' : 'макс.' }})</small>
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
              v-for="(target, key) in filteredObj" 
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

      <!-- Швидкі дії -->
      <div class="plans-section">
        <h3>⚡ Швидкі дії</h3>
        <div class="quick-actions">
          <div class="action-group">
            <h4>Застосувати до всіх магазинів:</h4>
            <div class="bulk-inputs">
              <div v-for="(target, key) in filteredObj" :key="key" class="bulk-input">
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
                    Застосувати
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="action-group">
            <h4>Загальні:</h4>
            {{ zaglushka }}
            <div class="stats">
              <div class="stat-item">
                <span class="stat-label">% заглушка:</span>
                <div class="bulk-input zaglushka">
                  <input 
                    type="number" 
                    v-model.number="zaglushka"
                    :step="getZagStep()"
                    @input="markAsChanged"
                    :min="100"
                    :max="1000"
                    class="bulk-value-input"
                  >
                </div>
              </div>

              <div class="stat-item">
                <span class="stat-label">Змін:</span>
                <span class="stat-value" :class="{ 'has-changes': hasChanges }">
                  {{ hasChanges ? 'Є незбережені' : 'Немає змін' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showConfirmModal" class="odx_modal-overlay" @click="cancelReset">
      <div class="odx_modal" @click.stop>
        <h3>Повернутися до налаштувань за замовчуванням</h3>
        <p>Ви впевнені, що хочете скинути всі зміни і повернутися до налаштувань за замовчуванням?</p>
        <div class="odx_modal-actions">
          <button @click="cancelReset" class="btn btn-secondary">Скасувати</button>
          <button @click="confirmReset" class="btn btn-danger">Скинути</button>
        </div>
      </div>
    </div>

    <div v-if="showUploadModal" class="odx_modal-overlay">
      <div class="odx_modal upload-odx_modal" @click.stop>
        <h3>Завантаження Excel файлу</h3>
        <div class="upload-progress">
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: uploadProgress + '%' }"
            ></div>
          </div>
          <div class="progress-text">
            {{ uploadProgress }}% завершено
          </div>
        </div>
        <!-- <div class="upload-stages">
          <div class="stage" :class="{ 'stage-active': uploadProgress >= 20 }">
            <span class="stage-icon">📁</span>
            <span>Читання файлу</span>
          </div>
          <div class="stage" :class="{ 'stage-active': uploadProgress >= 40 }">
            <span class="stage-icon">🔍</span>
            <span>Парсинг даних</span>
          </div>
          <div class="stage" :class="{ 'stage-active': uploadProgress >= 80 }">
            <span class="stage-icon">✅</span>
            <span>Валідація</span>
          </div>
          <div class="stage" :class="{ 'stage-active': uploadProgress >= 100 }">
            <span class="stage-icon">💾</span>
            <span>Застосування</span>
          </div>
        </div> -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as XLSX from 'xlsx'

const emit = defineEmits(['close'])

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
const showConfirmModal = ref(true)
const fileInput = ref(null)
const uploadProgress = ref(0)
const showUploadModal = ref(false)
const zaglushka = ref(null)

const filteredObj = computed(() => {
  return Object.fromEntries(
    Object.entries(targetsData.value.targetTree).slice(1)
  )
})

const getStoreName = (storeId) => {
  const storeTargets = targetsData.value?.storeTargets || {}
  
  console.log(`🔍 Получаем имя магазина для ID: ${storeTargets[storeId]}`);
  
  if (typeof storeTargets[storeId] === 'string') {
    return storeTargets[storeId]
  }

  if (typeof storeTargets[storeId] === 'object') {
    const store = storeTargets[storeId]
    return store?.store || store?.store || store?.store || `Магазин ${storeTargets[storeId]}`
  }
  
  return `Магазин ${storeTargets[storeId]}`
}

const getInputStep = (targetKey) => {
  return targetKey === 'unprocessed' ? 1 : 0.1
}
const getZagStep = () => {
  return 50
}

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

const STORAGE_KEY = 'targetsData'

const loadData = async () => {
  try {
    loading.value = true
    error.value = null

    const savedData = getSavedData()
    
    if (savedData) {
      targetsData.value = savedData
    } else {
      const response = await fetch('/com/static/data/targets.json')
      if (!response.ok) {
        throw new Error(`Ошибка загрузки: ${response.status}`)
      }
      
      const defaultData = await response.json()
      targetsData.value = defaultData
      
      saveData(defaultData)
    }

    originalData.value = JSON.parse(JSON.stringify(targetsData.value))
    
    initBulkValues()
    
  } catch (err) {
    console.error('❌ Помилка:', err)
    error.value = err.message || 'Помилка завантаження даних'
  } finally {
    loading.value = false
  }
}

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
    console.log('✓ в localStorage')
    return true
  } catch (err) {
    console.error('❌ Помилка в localStorage:', err)
    return false
  }
}

const initBulkValues = () => {
  Object.keys(targetsData.value.targetTree).forEach(key => {
    bulkValues.value[key] = 0.0
  })
}

const markAsChanged = () => {
  hasChanges.value = true
}

const applyBulkValue = (targetKey) => {
  const value = bulkValues.value[targetKey]
  if (value === undefined || value === null) return

  Object.keys(targetsData.value.storeTargets).forEach(storeId => {
    targetsData.value.storeTargets[storeId][targetKey] = value
  })
  
  markAsChanged()
  console.log(`✓ Применено значение ${value} для ${targetKey} ко всем магазинам`)
}

const saveChanges = () => {
  if (!hasChanges.value) return

  const success = saveData(targetsData.value)
  
  if (success) {
    hasChanges.value = false
    
    emitDataUpdate()
  
    showNotification('Зміни збережено!', 'success')
  } else {
    showNotification('Помилка!', 'error')
  }
}

const emitDataUpdate = () => {
  const event = new CustomEvent('plansDataUpdated', {
    detail: targetsData.value,
    zaglushka: zaglushka.value
  })
  window.dispatchEvent(event)
  
  console.log('оновлення')
}

const resetToDefaults = () => {
  showConfirmModal.value = true
}

const confirmReset = async () => {
  try {
    loading.value = true
    showConfirmModal.value = false
    
    localStorage.removeItem(STORAGE_KEY)
    
    const response = await fetch('/com/static/data/targets.json')
    const defaultData = await response.json()
    
    targetsData.value = defaultData
    originalData.value = JSON.parse(JSON.stringify(defaultData))
    hasChanges.value = false
    
    saveData(defaultData)
    
    emitDataUpdate()
    
    showNotification('Дані оновлені за замовчуванням', 'info')
    
  } catch (err) {
    console.error('', err)
    showNotification('Помилка онавлення!', 'error')
  } finally {
    loading.value = false
  }
}

const cancelReset = () => {
  showConfirmModal.value = false
}

const showNotification = (message, type = 'info') => {
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


const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  try {
    showUploadModal.value = true
    uploadProgress.value = 0
    
    if (!file.name.match(/\.(xlsx|xls)$/i)) {
      throw new Error('Неподдерживаемый формат файла. Используйте .xlsx или .xls')
    }

    uploadProgress.value = 20

    const arrayBuffer = await file.arrayBuffer()
    uploadProgress.value = 40


    const workbook = XLSX.read(arrayBuffer, {
      type: 'array',
      cellDates: true,
      cellNF: true,
      cellText: false
    })

    uploadProgress.value = 60

    const parsedData = parseExcelData(workbook)
    uploadProgress.value = 80

    const validatedData = validateExcelData(parsedData)
    uploadProgress.value = 90

    await applyExcelData(validatedData)
    uploadProgress.value = 100

    console.log('✅ Файл успешно обработан')
    showNotification('Excel файл успешно загружен!', 'success')

  } catch (error) {
    console.error('❌ Ошибка обработки Excel файла:', error)
    showNotification(`Ошибка: ${error.message}`, 'error')
  } finally {

    if (fileInput.value) {
      fileInput.value.value = ''
    }
    
    setTimeout(() => {
      showUploadModal.value = false
      uploadProgress.value = 0
    }, 1000)
  }
}

const parseExcelData = (workbook) => {
  const result = {
    targetTree: {},
    storeTargets: {}
  }

  if (workbook.SheetNames.includes('Настройки показателей')) {
    const settingsSheet = workbook.Sheets['Настройки показателей']
    const settingsData = XLSX.utils.sheet_to_json(settingsSheet, { header: 1 })
    
    for (let i = 1; i < settingsData.length; i++) {
      const row = settingsData[i]
      if (row[0] && row[1] && row[2] && row[3]) {
        const key = row[0].toString() // Оставляем ключ как есть
        result.targetTree[key] = {
          name: row[1],
          maxScore: Number(row[2]) || 100,
          type: row[3].toString().toLowerCase() === 'negative' ? 'negative' : 'positive'
        }
      }
    }
  }

  if (workbook.SheetNames.includes('Цілі')) {
    const targetsSheet = workbook.Sheets['Цілі']
    const targetsData = XLSX.utils.sheet_to_json(targetsSheet, { header: 1 })
    
    if (targetsData.length < 2) {
      throw new Error('Лист "Цели" пустОЙ или некорректный')
    }
    
    const headers = targetsData[0]
    console.log('🔍 Заголовки Excel:', headers)

    const nameToKeyMapping = {
      'Списання': 'losses',
      'Нестачі': 'shortages', 
      'ФОП': 'fop',
      'Повернення': 'shiftRemainder',
      'Непровед.': 'unprocessed',
      'Непровед. списання': 'unprocessed'
    }
    
    const targetKeys = []
    for (let j = 1; j < headers.length - 1; j++) {
      const headerName = headers[j]
      if (headerName) {
        let key = null
        for (const [name, keyValue] of Object.entries(nameToKeyMapping)) {
          if (headerName.includes(name)) {
            key = keyValue
            break
          }
        }
        
        if (!key) {
          for (const [treeKey, treeValue] of Object.entries(targetsData.value.targetTree)) {
            if (headerName.includes(treeValue.name) || treeValue.name.includes(headerName)) {
              key = treeKey
              break
            }
          }
        }
        
        if (key) {
          targetKeys.push(key)
        } else {
          console.warn(`⚠️ Не найден ключ для колонки: ${headerName}`)
        }
      }
    }
    
    console.log('🔑 Ключи показателей:', targetKeys)
    
    for (let i = 1; i < targetsData.length; i++) {
      const row = targetsData[i]
      if (row[0]) {
        const storeId = row[0].toString()
        const storeName = row[row.length - 1] // Последняя колонка - название
        
        result.storeTargets[storeId] = {
          store: storeName || `Магазин ${storeId}`
        }
        
        for (let j = 0; j < targetKeys.length; j++) {
          const key = targetKeys[j]
          const value = Number(row[j + 1])
          if (!isNaN(value)) {
            result.storeTargets[storeId][key] = value
          } else {
            console.warn(`⚠️ Некорректное значение для магазина ${storeId}, показатель ${key}: ${row[j + 1]}`)
          }
        }
      }
    }
  }

  console.log('📋 Парсинг завершен:', {
    targetTree: Object.keys(result.targetTree).length,
    storeTargets: Object.keys(result.storeTargets).length
  })
  
  return result
}

const validateExcelData = (data) => {
  const errors = []
  const warnings = []
  
  console.log('🔍 Начинаем валидацию данных...')
  
  if (data.targetTree && Object.keys(data.targetTree).length > 0) {
    Object.keys(data.targetTree).forEach(key => {
      const target = data.targetTree[key]
      if (!target.name) {
        errors.push(`Отсутствует название для показателя: ${key}`)
      }
      if (typeof target.maxScore !== 'number' || target.maxScore < 1 || target.maxScore > 500) {
        errors.push(`Некорректный максимальный балл для ${key}: ${target.maxScore} (должен быть 1-500)`)
      }
      if (!['positive', 'negative'].includes(target.type)) {
        errors.push(`Некорректный тип показателя ${key}: ${target.type} (должен быть positive или negative)`)
      }
    })
    console.log(`✅ Проверены настройки ${Object.keys(data.targetTree).length} показателей`)
  }
  
  if (!data.storeTargets || Object.keys(data.storeTargets).length === 0) {
    errors.push('Не найдены цели по магазинам в листе "Цели по магазинам"')
  } else {
    Object.keys(data.storeTargets).forEach(storeId => {
      const storeData = data.storeTargets[storeId]

      Object.keys(storeData).forEach(targetKey => {
        if (targetKey === 'store') return
        
        const value = storeData[targetKey]
        
        if (typeof value !== 'number' || isNaN(value)) {
          errors.push(`Нечисловое значение для магазина ${storeId}, показатель ${targetKey}: "${value}"`)
          return
        }
        
        const maxValue = targetKey === 'unprocessed' ? 10 : 1
        if (value < 0) {
          errors.push(`Отрицательное значение для магазина ${storeId}, показатель ${targetKey}: ${value}`)
        } else if (value > maxValue) {
          if (value > maxValue * 10) {
            errors.push(`Слишком большое значение для магазина ${storeId}, показатель ${targetKey}: ${value} (максимум: ${maxValue * 10})`)
          } else {
            warnings.push(`Большое значение для магазина ${storeId}, показатель ${targetKey}: ${value} (обычно до ${maxValue})`)
          }
        }
      })
    })
    
    console.log(`✅ Проверены данные ${Object.keys(data.storeTargets).length} магазинов`)
  }
  
  if (warnings.length > 0) {
    console.warn('⚠️ Предупреждения:')
    warnings.forEach(warning => console.warn(warning))
  }

  if (errors.length > 0) {
    const errorMessage = 'Ошибки валидации:\n' + errors.join('\n')
    if (warnings.length > 0) {
      errorMessage += '\n\nПредупреждения:\n' + warnings.join('\n')
    }
    throw new Error(errorMessage)
  }
  
  console.log('✅ Валидация завершена успешно')
  return data
}

const applyExcelData = async (data) => {
  const backup = JSON.parse(JSON.stringify(targetsData.value))
  
  try {
    console.log('💾 Применяем данные из Excel...')
    console.log('📄 Новые данные:', data)
    
    if (data.targetTree && Object.keys(data.targetTree).length > 0) {
      Object.assign(targetsData.value.targetTree, data.targetTree)
      console.log('✅ Обновлены настройки показателей')
    }
    
    if (data.storeTargets && Object.keys(data.storeTargets).length > 0) {
      console.log('🏢 Старые магазины:', Object.keys(targetsData.value.storeTargets))
      console.log('🏢 Новые магазины:', Object.keys(data.storeTargets))
      
      targetsData.value.storeTargets = { ...data.storeTargets }
      
      console.log('✅ Магазины полностью заменены')
      console.log('🏢 Результат:', Object.keys(targetsData.value.storeTargets))
    }

    initBulkValues()

    markAsChanged()

    emitDataUpdate()
    
    console.log('✅ Данные из Excel успешно применены')
  } catch (error) {
    console.error('❌ Ошибка применения данных:', error)
    targetsData.value = backup
    throw error
  }
}

const downloadTemplate = () => {
  try {
    const workbook = XLSX.utils.book_new()
  
    const settingsData = [['Ключ', 'Название', 'Макс. балл', 'Тип', 'Описание']]
    
    Object.keys(targetsData.value.targetTree).forEach(key => {
      const target = targetsData.value.targetTree[key]
      settingsData.push([
        key,
        target.name,
        target.maxScore,
        target.type,
        `Показатель: ${target.name}`
      ])
    })
    
    const settingsSheet = XLSX.utils.aoa_to_sheet(settingsData)
    XLSX.utils.book_append_sheet(workbook, settingsSheet, 'Настройки показателей')
    
    const currentStores = targetsData.value.storeTargets
    const storeIds = Object.keys(currentStores)
    
    const indicators = Object.keys(targetsData.value.targetTree)
      .filter(key => key !== 'turnover')
    
    const targetsHeaders = ['ID Магазина', ...indicators.map(key => targetsData.value.targetTree[key].name), 'Название магазина']
    const targetsData_array = [targetsHeaders]
    
    storeIds.forEach(storeId => {
      const storeData = currentStores[storeId]
      const row = [
        storeId, 
        ...indicators.map(key => storeData[key] || 0), 
        storeData.store || `Магазин ${storeId}`
      ]
      targetsData_array.push(row)
    })
    
    const targetsSheet = XLSX.utils.aoa_to_sheet(targetsData_array)
    XLSX.utils.book_append_sheet(workbook, targetsSheet, 'Цели по магазинам')
    
    const fileName = `Шаблон_планов_SMK_${new Date().toISOString().slice(0,10)}.xlsx`
    XLSX.writeFile(workbook, fileName)
    
    console.log(`📥 Шаблон Excel скачан: ${fileName} (${storeIds.length} магазинов)`)
    showNotification(`Шаблон Excel скачан! ${storeIds.length} магазинов`, 'info')
    
  } catch (error) {
    console.error('❌ Ошибка создания шаблона:', error)
    showNotification('Ошибка создания шаблона!', 'error')
  }
}


const handleKeydown = (event) => {
  if (event.ctrlKey && event.key === 's') {
    event.preventDefault()
    saveChanges()
  }
  if (event.key === 'Escape') {
    emit('close')
  }
}

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
  padding: 4px 10px;
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

.btn-info {
  background: #06b6d4;
  color: white;
}

.btn-info:hover {
  background: #0891b2;
  transform: translateY(-1px);
}

.btn-upload {
  background: #10b981;
  color: white;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.btn-upload:hover {
  background: #059669;
  transform: translateY(-1px);
}

.btn-small {
  padding: 4px 8px;
  font-size: 12px;
  background-color: #2563eb ;
  color: #d1d5db;
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
  display: flex;
  gap: 16px;
}

.target-card {
  min-width: 190px;
  border: 2px solid #3b82f6;
  border-radius: 8px;
  padding: 16px;
  background: #f8fafc;
  transition: all 0.2s ease;
}

.target-card:hover {
  border-color: #2a5fb4;
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

.odx_modal-overlay {
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

.odx_modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}

.odx_modal h3 {
  margin: 0 0 16px 0;
  color: #1e293b;
  font-size: 18px;
  font-weight: 600;
}

.odx_modal p {
  margin: 0 0 20px 0;
  color: #64748b;
  line-height: 1.5;
}

.odx_modal-actions {
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

  
  .search-input, .target-filter {
    min-width: auto;
    width: 100%;
  }
  .search-input, .target-filter {
    min-width: auto;
    width: 100%;
    padding-left: 15px;
  }
}
.filters {
  flex-direction: column;
  position: relative;
}
.target-filter {
  min-width: auto;
  width: 100%;
  background-image: url("data:image/svg+xml;utf8,<svg fill='black' height='24' viewBox='0 0 24 24' width='24' xmlns='http://www.w3.org/2000/svg'><path d='M7 10l5 5 5-5z'/><path d='M0 0h24v24H0z' fill='none'/></svg>");
  background-repeat: no-repeat;
  background-position-x: 100%;
  background-position-y: 7px;
}

.search-input {
  padding-left: 45px;
}

.inp_search {
  position: absolute;
  top: 3px;
  left: 3px;
  height: 35px;
  width: 35px;
  /* padding-left: 10px; */
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

/* ==== EXCEL UPLOAD STYLES ==== */

.upload-odx_modal {
  max-width: 500px;
  min-height: 300px;
}

.upload-progress {
  margin: 20px 0;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6 0%, #06b6d4 100%);
  border-radius: 10px;
  transition: width 0.3s ease;
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.3) 50%,
    transparent 100%
  );
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.progress-text {
  text-align: center;
  margin-top: 12px;
  font-weight: 600;
  color: #374151;
  font-size: 16px;
}

.upload-stages {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
}

.stage {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
  opacity: 0.5;
}

.stage-active {
  background: #f0f9ff;
  border-color: #3b82f6;
  opacity: 1;
  transform: scale(1.02);
}

.stage-icon {
  font-size: 18px;
  min-width: 24px;
  text-align: center;
}

.stage span:last-child {
  font-weight: 600;
  color: #374151;
}

.stage-active span:last-child {
  color: #1e40af;
}

/* Адаптивность для мобильных */
@media (max-width: 480px) {
  .upload-odx_modal {
    max-width: 95%;
    margin: 20px;
  }
  
  .stage {
    padding: 8px 12px;
  }
  
  .stage-icon {
    font-size: 16px;
  }
  
  .stage span:last-child {
    font-size: 14px;
  }

}
.header_title {
  display: flex;
  gap: 8px;
}
</style>
