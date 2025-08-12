<template>
  <div class="odx-sales-dashboard">
    <img :class="{ 'odx-palette-toggle--active': isPaletteOpen }" class="odx-palette-toggle" @click="togglePalette"
      src="https://toppng.com/uploads/preview/the-icon-is-shaped-like-an-oval-that-slightly-resembles-paint-palette-icon-11553394861oazcgcebd1.png"
      alt="Palette">

    <div class="odx-color-palette" :class="{ 'odx-color-palette--open': isPaletteOpen }">
      <div class="odx-color-palette__content">
        <h3>Палітра:</h3>
        <div class="odx-color-palette__grid">
          <div v-for="color in darkColors" :key="color" class="odx-color-option"
            :class="{ 'odx-color-option--selected': selectedColor === color }" :style="{ backgroundColor: color }"
            @click="changeColor(color)" :title="color" />
        </div>
        <div class="odx-format-controls">
          <label class="odx-toggle">
            <input type="checkbox" v-model="formatter" @click="formatter = !formatter" />
            <span class="odx-toggle__slider" :style="headerStyle"></span>
            <span class="odx-toggle__label">Форматування</span>
          </label>
        </div>
      </div>
    </div>

    <div v-if="isPaletteOpen" class="odx-overlay" @click="closePalette"></div>

    <div v-if="loading" class="odx-loading">
      <div class="odx-loading__progress"></div>
    </div>


    <!-- Компонент редактора планов -->
    <div v-if="showPlansEditor" class="odx-plans-overlay">
      <div class="odx-plans-container">
        <Plans @close="showPlansEditor = false" />
      </div>
    </div>

    <div v-if="error" class="odx-error">
      <div class="odx-error__icon">⚠️</div>
      <div class="odx-error__message">{{ error }}</div>
      <button class="odx-error__retry" @click="refreshData">Попробовать снова</button>
    </div>

    <div v-if="!loading && !error" class="odx-dashboard">
      <div class="odx-controls">
        <div :style="headerStyle" class="odx-controls__refresh" @click="refreshData" :disabled="loading">
          Оновити
        </div>
        <div class="tooltip-controls">
          <label class="tooltip-toggle">
            <input type="checkbox" v-model="tooltipEnabled" />
            <span class="toggle-slider" :style="headerStyle"></span>
            <span class="toggle-label">Деталі</span>
          </label>
        </div>
      </div>

      <div class="odx-table-container">
        <div class="odx-table">
          <div class="odx-table__header" :style="headerStyle">
            <div class="odx-table__row odx-table__row--header-top">
              <div class="odx-table__cell odx-table__cell--static">Регіон / Магазин</div>
              <div class="odx-table__cell odx-table__cell--group" :style="{ width: dynamicRowWidth }">
                <div v-for="week in weeks" :key="week.id" class="odx-week">
                  <div class="odx-week__name">{{ week.name }} ({{ week.dateRange }})</div>
                </div>
              </div>
            </div>

            <div class="odx-table__row odx-table__row--header-middle">
              <div class="odx-table__cell odx-table__cell--static"></div>
              <div v-for="week in weeks" :key="week.id" class="odx-week">
                <div class="odx-week__groups">
                  <div v-for="group in visibleGroups" :key="group.key"
                    class="odx-table__cell odx-table__cell--group-header" :style="getGroupStyle(group.key)">
                    <div @click="toggleGroupVisibility(group.key)" class="odx-group-toggle">
                      <span>{{ group.label }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="odx-table__row odx-table__row--header-bottom">
              <div class="odx-table__cell odx-table__cell--static"></div>
              <div v-for="week in weeks" :key="week.id" class="odx-week">
                <div class="odx-week__columns">
                  <div v-for="indicator in availableIndicators" :key="indicator.key"
                    class="odx-table__cell odx-table__cell--metric" :style="getStyle(indicator.key)"
                    @click="handleRegionSort(week.id, indicator.key)">
                    <div class="odx-metric-header">
                      <span v-html="getIndicatorHeader(indicator)"></span>
                      <span class="odx-sort-arrow" :class="getSortArrowClass(week.id, indicator.key)">
                        {{ getSortIcon(week.id, indicator.key) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="odx-table__body">
            <div class="odx-regions">
              <transition-group name="table-row" tag="div">

                <div v-for="region in sortedRegions" :key="`region-${region.id}`"
                  class="odx-table__row odx-table__row--region" :class="getRegionRowClass(region.regionRank)">
                  <div class="odx-table__cell odx-table__cell--static">
                    <div class="odx-region-info">
                      <div class="odx-region-info__indicator" :style="{ backgroundColor: region.color }"></div>
                      <span class="odx-region-info__title">{{ region.name }}</span>
                    </div>
                  </div>
                  <div class="odx-table__data">
                    <div v-for="week in weeks" :key="week.id" class="odx-week">
                      <div class="odx-week__columns">
                        <div v-for="indicator in availableIndicators"
                          :key="`region-${region.id}-${week.id}-${indicator.key}`"
                          class="odx-table__cell odx-table__cell--data odx-tooltip-trigger"
                          :class="getRegionCellClass(indicator.key, region, week.id)" :style="getStyle(indicator.key)"
                          @mouseenter="showTooltip($event, region, 'region', week.id, indicator.key)"
                          @mouseleave="hideTooltip" @mousemove="updateTooltipPosition">
                          {{ getRegionData(region, week.id, indicator.key) }}
                          <!-- | {{ region.overallTotalScore }} -->
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </transition-group>
            </div>

            <div class="odx-separator">
              <div class="odx-sort-controls">
                <div class="odx-sort-controls__row">
                  <div class="odx-sort-controls__static"></div>
                  <div class="odx-sort-controls__weeks">
                    <div v-for="week in weeks" :key="week.id" class="odx-sort-week">
                      <div class="odx-sort-week__columns">
                        <div v-for="indicator in availableIndicators" :key="`sort-${week.id}-${indicator.key}`"
                          class="odx-sort-control" :class="getStoreSortArrowClass(week.id, indicator.key)"
                          :style="getStyle(indicator.key)"
                          :title="`Сортировать магазины по ${indicator.label.replace(/<br>/g, ' ')} (${week.name})`"
                          @click="handleStoreSort(week.id, indicator.key)">
                          <span class="odx-sort-arrow">
                            {{ getStoreSortIcon(week.id, indicator.key) }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="odx-stores">
              <transition-group name="table-row" tag="div">

                <div v-for="store in allStores" :key="`store-${store.id}`" class="odx-table__row odx-table__row--store"
                  :class="getStoreRowClass(store.overallRank)">
                  <div class="odx-table__cell odx-table__cell--static">
                    <div class="odx-store-info">
                      <div class="odx-store-info__indicator" :style="{ backgroundColor: store.regionColor }"></div>
                      <span class="odx-store-info__title">{{ store.name }}</span>
                    </div>
                  </div>
                  <div class="odx-table__data">
                    <div v-for="week in weeks" :key="week.id" class="odx-week">
                      <div class="odx-week__columns">
                        <div v-for="indicator in availableIndicators"
                          :key="`store-${store.id}-${week.id}-${indicator.key}`"
                          class="odx-table__cell odx-table__cell--data odx-tooltip-trigger"
                          :class="[getCellClass(indicator.key, getStoreWeekData(store, week.id), false), indicator.key]"
                          :style="getStyle(indicator.key)"
                          @mouseenter="showTooltip($event, store, 'store', week.id, indicator.key)"
                          @mouseleave="hideTooltip" @mousemove="updateTooltipPosition">
                          {{ getStoreData(store, week.id, indicator.key) }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </transition-group>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="kpi">
      <div v-if="!isOpen" @click="togglePanel" class="kpi-toggle-btn" title="Открыть панель КПИ">
        <img src="https://i.ibb.co/fV6qHXLb/com.png" alt="" class="comp">
      </div>
      <div v-if="isOpen" class="kpi-overlay" @click="closePanel"></div>
      <div class="kpi-sidebar" :class="{ 'kpi-sidebar--open': isOpen }">
        <div class="kpi-header">
          <h2>📊 Ключові показники</h2>
          <button @click="closePanel" class="close-btn" title="Закрыть">✕</button>
        </div>

        <div class="kpi-content" v-if="processedData">

          <div class="kpi-section">
            <h3>🎯 Загальне зведення</h3>
            <div class="kpi-cards">
              <div class="kpi-card primary">
                <div class="kpi-value">{{ processedData.totalStores }}</div>
                <div class="kpi-label">Всьго магазинів</div>
              </div>
              <div class="kpi-card success">
                <div class="kpi-value">{{ processedData.totalRegions }}</div>
                <div class="kpi-label">Регіонів</div>
              </div>
              <div class="kpi-card info">
                <div class="kpi-value">{{ formatNumber(processedData.averageScore) }}</div>
                <div class="kpi-label">Середній бал</div>
              </div>
              <div class="kpi-card warning">
                <div class="kpi-value">{{ processedData.planExecutionPercent }}%</div>
                <div class="kpi-label">Выконання плану</div>
              </div>
            </div>
          </div>

          <div class="kpi-section">
            <h3>🏆 Топ регіони</h3>
            <div class="kpi-list">
              <div v-for="(region, index) in processedData.topRegions" :key="region.id" class="kpi-list-item"
                :class="`rank-${index + 1}`">
                <div class="rank-badge">{{ index + 1 }}</div>
                <div class="region-info">
                  <div class="region-indicator" :style="{ backgroundColor: region.color }"></div>
                  <span class="region-name">{{ region.name }}</span>
                </div>
                <div class="region-score">{{ formatNumber(region.score) }}</div>
              </div>
            </div>
          </div>

          <div class="kpi-section">
            <h3>⭐ Топ <b> {{ KPITopStores }} </b> магазини</h3>
            <div class="kpi-list">
              <div v-for="(store, index) in processedData.topStores" :key="store.id" class="kpi-list-item"
                :class="`rank-${index + 1}`">
                <div class="rank-badge">{{ index + 1 }}</div>
                <div class="store-info">
                  <div class="store-region-indicator" :style="{ backgroundColor: store.regionColor }">
                  </div>
                  <span class="store-name">{{ store.name }}</span>
                  <span class="store-region">{{ store.regionName }}</span>
                </div>
                <div class="store-score">{{ formatNumber(store.overallTotalScore) }}</div>
              </div>
            </div>
          </div>

          <div class="kpi-section">
            <h3>⚠️ Проблемні зони</h3>
            <div class="kpi-cards">
              <div class="kpi-card danger">
                <div class="kpi-value">{{ processedData.problemStores }}</div>
                <div class="kpi-label">Магазинів в зоні ризику</div>
              </div>
              <div class="kpi-card warning">
                <div class="kpi-value">{{ processedData.belowPlanStores }}</div>
                <div class="kpi-label">Не виконують план</div>
              </div>
            </div>

            <div class="problem-details">
              <div class="problem-item" v-for="issue in processedData.topIssues" :key="issue.type">
                <div class="issue-type">{{ issue.name }}</div>
                <div class="issue-stats">
                  <span class="issue-value">{{ formatNumber(issue.totalValue) }}</span>
                  <span class="issue-stores">{{ issue.affectedStores }} магазинів</span>
                </div>
              </div>
            </div>
          </div>

          <div class="kpi-section">
            <h3>📈 Динаміка по неділям</h3>
            <div class="week-comparison">
              <div v-for="week in processedData.weeklyComparison" :key="week.id" class="week-stats">
                <div class="week-header">
                  <div class="week-name">{{ week.name }}</div>
                  <div class="week-period">{{ week.dateRange }}</div>
                </div>
                <div class="week-metrics">
                  <div class="metric">
                    <span class="metric-label">Загальний бал:</span>
                    <span class="metric-value">{{ formatNumber(week.totalScore) }}</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">Выконання плану:</span>
                    <span class="metric-value">{{ week.planExecution }}%</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">Середній факт:</span>
                    <span class="metric-value">{{ formatNumber(week.averageFact) }}</span>
                  </div>
                </div>
              </div>

              <div class="trend-indicator" v-if="processedData.weeklyTrend">
                <div class="trend-label">Тренд:</div>
                <div class="trend-value" :class="processedData.weeklyTrend.type">
                  {{ processedData.weeklyTrend.icon }} {{ processedData.weeklyTrend.text }}
                </div>
              </div>
            </div>
          </div>

          <div class="kpi-section">
            <h3>🎯 Цілі та досягнення</h3>
            <div class="targets-overview">
              <div v-for="target in processedData.targetsOverview" :key="target.key" class="target-item">
                <div class="target-header">
                  <span class="target-name">{{ target.name }}</span>
                  <span class="target-score">{{ target.averageScore }}/{{ target.maxScore }}</span>
                </div>
                <div class="target-progress">
                  <div class="progress-bar" :style="{ width: `${(target.averageScore / target.maxScore) * 100}%` }">
                  </div>
                </div>
                <div class="target-stats">
                  <span class="success-stores">✅ {{ target.successfulStores }}</span>
                  <span class="problem-stores">❌ {{ target.problemStores }}</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <div v-if="tooltip.visible && tooltip.data" class="odx-tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px', opacity: tooltip.x === 0 && tooltip.y === 0 ? 0 : 1 }">
      <div class="odx-tooltip__header">
        <div class="odx-tooltip__title">{{ tooltip.data.entityName }}</div>
        <div class="odx-tooltip__subtitle">{{ tooltip.data.weekName }} </div>
      </div>
      <div class="odx-tooltip__main">{{ tooltip.data.mainValue }}</div>
      <div class="odx-tooltip__details">
        <div v-for="detail in tooltip.data.details" :key="detail.label" class="odx-tooltip__detail">
          <span class="odx-tooltip__detail-label">{{ detail.label }}:</span>
          <span class="odx-tooltip__detail-value">{{ detail.value }}</span>
        </div>
      </div>
    </div>

    <!-- Тултип -->
        <div v-if="tooltip.visible && tooltip.data" ref="tooltipRef" class="custom-tooltip" :style="{
            left: tooltip.x + 'px',
            top: tooltip.y + 'px',
            opacity: tooltip.x === 0 && tooltip.y === 0 ? 0 : 1
            }">
            <div class="tooltip-header">
                <div class="tooltip-title">{{ tooltip.data.entityName }}</div>
                <div class="tooltip-subtitle">{{ tooltip.data.weekName }} • {{ tooltip.data.indicator }}</div>
            </div>

            <div class="tooltip-main-value">
                {{ tooltip.data.mainValue }}
            </div>

            <div class="tooltip-details">
                <div v-for="detail in tooltip.data.details" :key="detail.label" class="tooltip-detail-row">
                    <span class="detail-label">{{ detail.label }}:</span>
                    <span class="detail-value">{{ detail.value }}</span>
                </div>
            </div>
        </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, reactive, nextTick, watch } from 'vue'
import Plans from '../components/Plans.vue'

const loading = ref(true)
const error = ref(null)
const salesData = ref(null)
const targetsData = ref(null)
const sortByTotalScore = ref(true)
const regions = ref([])
const tooltipEnabled = ref(true)
const formatter = ref(false)
const KPITopStores = ref(5)
const isOpen = ref(false)
const planScore = ref(0)

const showPlansEditor = ref(false)
const dynamicTargetsData = ref(null)

const loadData = async () => {
  try {
    loading.value = true
    error.value = null
    const [salesResponse, targetsResponse] = await Promise.all([
      fetch('/com/static/data/real-data.json'),
      fetch('/com/static/data/targets.json')
    ])


    if (!salesResponse.ok || !targetsResponse.ok) {
      throw new Error(`HTTP error! status: ${salesResponse.status || targetsResponse.status}`)
    }

    const [salesDataResult, targetsDataResult] = await Promise.all([
      salesResponse.json(),
      targetsResponse.json()
    ])

    if (!salesDataResult.weeks || !salesDataResult.regions) {
      throw new Error('Неверная структура данных продаж')
    }

    if (!targetsDataResult.targetTree || !targetsDataResult.storeTargets) {
      throw new Error('Неверная структура данных целей')
    }

    // НОВОЕ: Проверяем сохраненные данные в памяти
    const savedTargets = getSavedTargetsFromMemory()
    
    salesData.value = salesDataResult
    targetsData.value = savedTargets || targetsDataResult
    dynamicTargetsData.value = targetsData.value
    regions.value = Object.values(salesDataResult.regions)

    initializeVisibility()
    processData()
  } catch (err) {
    console.error('Ошибка загрузки данных:', err)
    error.value = err.message || 'Ошибка загрузки данных'
  } finally {
    setTimeout(() => {
      loading.value = false
    }, 400)
  }
}



// Функция получения сохраненных данных из localStorage
const getSavedTargetsFromMemory = () => {
  try {
    const saved = localStorage.getItem('targetsData')
    return saved ? JSON.parse(saved) : null
  } catch (err) {
    console.error('❌ Ошибка чтения localStorage:', err)
    return null
  }
}

// Функция сохранения в localStorage
const saveTargetsToMemory = (data) => {
  try {
    localStorage.setItem('targetsData', JSON.stringify(data))
    console.log('✓ Данные планов сохранены в localStorage:', data)
    return true
  } catch (err) {
    console.error('❌ Ошибка сохранения в localStorage:', err)
    return false
  }
}

// Слушаем изменения от компонента планов
const handlePlansDataUpdate = (event) => {
  const newTargetsData = event.detail
  
  // Обновляем данные
  targetsData.value = newTargetsData
  dynamicTargetsData.value = newTargetsData
  
  // Сохраняем в память
  saveTargetsToMemory(newTargetsData)
  
  // Пересчитываем все данные с новыми планами
  processData()
  
  console.log('Планы обновлены динамически!')
}

// Переключение редактора планов
const togglePlansEditor = () => {
  showPlansEditor.value = !showPlansEditor.value
}






const togglePanel = () => { isOpen.value = !isOpen.value }
const closePanel = () => { isOpen.value = false }

const processedData = computed(() => {
  if (!salesData.value || !regions.value || !weeks.value) return null

  const allStores = []
  regions.value.forEach(region => {
    if (region.stores) {
      region.stores.forEach(store => {
        allStores.push({
          ...store,
          regionId: region.id,
          regionName: region.name,
          regionColor: region.color
        })
      })
    }
  })

  const totalStores = allStores.length
  const totalRegions = regions.value.length
  const totalScore = allStores.reduce((sum, store) => sum + (store.overallTotalScore || 0), 0)
  const averageScore = totalStores > 0 ? Math.round(totalScore / totalStores) : 0



  let totalPlan = 0
  let totalFact = 0
  allStores.forEach(store => {
    weeks.value.forEach(week => {
      const weekData = store.weeklyData?.find(w => w.weekId === week.id)
      if (weekData) {
        totalPlan += weekData.plan || 0
        totalFact += weekData.fact || 0
      }
    })
  })
  const planExecutionPercent = totalPlan > 0 ? Math.round((totalFact / totalPlan) * 100) : 0

  const regionsWithScores = regions.value.map(region => {
    let regionScore = 0
    if (region.stores) {
      region.stores.forEach(store => {
        regionScore += store.overallTotalScore || 0
      })
    }
    return { ...region, score: regionScore }
  }).sort((a, b) => b.score - a.score).slice(0, 5)

  const topStores = [...allStores]
    .sort((a, b) => (b.overallTotalScore || 0) - (a.overallTotalScore || 0))
    .slice(0, KPITopStores.value)

  const problemStores = allStores.filter(store => (store.overallTotalScore || 0) < averageScore * 0.7).length
  const belowPlanStores = allStores.filter(store => {
    let storePlan = 0
    let storeFact = 0
    weeks.value.forEach(week => {
      const weekData = store.weeklyData?.find(w => w.weekId === week.id)
      if (weekData) {
        storePlan += weekData.plan || 0
        storeFact += weekData.fact || 0
      }
    })
    return storePlan > 0 && (storeFact / storePlan) < 0.95
  }).length

  const topIssues = []
  let summ = 0;
  if (targetsData.value.targetTree) {
    Object.entries(targetsData.value.targetTree).forEach(([key, target]) => {
      let totalValue = 0
      let affectedStores = 0
      summ += target.maxScore
      allStores.forEach(store => {
        let storeValue = 0
        weeks.value.forEach(week => {
          const weekData = store.weeklyData?.find(w => w.weekId === week.id)
          if (weekData && weekData[key]) {
            storeValue += weekData[key] || 0
          }
        })
        if (storeValue > 0) {
          totalValue += storeValue
          affectedStores++
        }
      })

      if (totalValue > 0) {
        topIssues.push({
          type: key,
          name: target.name,
          totalValue,
          affectedStores
        })
      }
    })
  }
  planScore.value = summ
  topIssues.sort((a, b) => b.totalValue - a.totalValue).splice(3)

  const weeklyComparison = weeks.value.map(week => {
    let weekTotalScore = 0
    let weekTotalPlan = 0
    let weekTotalFact = 0
    let storeCount = 0

    allStores.forEach(store => {
      const weekData = store.weeklyData?.find(w => w.weekId === week.id)
      if (weekData) {
        weekTotalScore += weekData.totalScore || 0
        weekTotalPlan += weekData.plan || 0
        weekTotalFact += weekData.fact || 0
        storeCount++
      }
    })

    return {
      ...week,
      totalScore: weekTotalScore,
      planExecution: weekTotalPlan > 0 ? Math.round((weekTotalFact / weekTotalPlan) * 100) : 0,
      averageFact: storeCount > 0 ? Math.round(weekTotalFact / storeCount) : 0
    }
  })

  let weeklyTrend = null
  if (weeklyComparison.length >= 2) {
    const latestWeek = weeklyComparison[0]
    const previousWeek = weeklyComparison[1]
    const scoreDiff = latestWeek.totalScore - previousWeek.totalScore
    const planDiff = latestWeek.planExecution - previousWeek.planExecution

    if (scoreDiff > 0 && planDiff > 0) {
      weeklyTrend = { type: 'positive', icon: '📈', text: 'Позитивна динаміка' }
    } else if (scoreDiff < 0 || planDiff < 0) {
      weeklyTrend = { type: 'negative', icon: '📉', text: 'Негативна динаміка' }
    } else {
      weeklyTrend = { type: 'stable', icon: '➡️', text: 'Стабільні показники' }
    }
  }

  const targetsOverview = []
  if (targetsData.value.targetTree) {
    Object.entries(targetsData.value.targetTree).forEach(([key, target]) => {
      let totalScore = 0
      let successfulStores = 0
      let problemStores = 0

      allStores.forEach(store => {
        let storeScore = 0
        weeks.value.forEach(week => {
          const weekData = store.weeklyData?.find(w => w.weekId === week.id)
          if (weekData && weekData[`${key}_score`]) {
            storeScore += weekData[`${key}_score`] || 0
          }
        })

        totalScore += storeScore
        const averageStoreScore = weeks.value.length > 0 ? storeScore / weeks.value.length : 0

        if (averageStoreScore >= target.maxScore * 0.8) {
          successfulStores++
        } else if (averageStoreScore < target.maxScore * 0.5) {
          problemStores++
        }
      })

      const averageScore = allStores.length > 0 ? Math.round(totalScore / allStores.length) : 0

      targetsOverview.push({
        key,
        name: target.name,
        maxScore: target.maxScore,
        averageScore,
        successfulStores,
        problemStores
      })
    })
  }

  return {
    totalStores,
    totalRegions,
    averageScore,
    planExecutionPercent,
    topRegions: regionsWithScores,
    topStores,
    problemStores,
    belowPlanStores,
    topIssues,
    weeklyComparison,
    weeklyTrend,
    targetsOverview,
  }
})




const handleKeydown = (event) => {
  if (event.key === 'Escape' && isOpen.value) {
    closePanel()
  }
}

watch(isOpen, (newValue) => {
  if (newValue) {
    document.addEventListener('keydown', handleKeydown)
    document.body.style.overflow = 'hidden'
  } else {
    document.removeEventListener('keydown', handleKeydown)
    document.body.style.overflow = ''
  }
})

const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  data: null,
  type: null,
  width: 0,
  height: 0
})

const showTooltip = (event, data, type, weekId, indicator) => {
  if (!tooltipEnabled.value) return
  const tooltipData = getTooltipData(data, weekId, indicator, type)
  tooltip.value = {
    visible: true,
    x: 0,
    y: 0,
    data: tooltipData,
    type: type,
    width: 0,
    height: 0
  }
  nextTick(() => {
    updateTooltipPosition(event)
  })
}

const updateTooltipPosition = (event) => {
  if (!tooltip.value.visible) return

  const tooltipElement = document.querySelector('.odx-tooltip')
  if (!tooltipElement) return

  const tooltipRect = tooltipElement.getBoundingClientRect()
  const windowWidth = window.innerWidth
  const windowHeight = window.innerHeight

  let x = event.clientX + 10
  let y = event.clientY + 10

  if (x + tooltipRect.width > windowWidth - 10) {
    x = event.clientX - tooltipRect.width - 10
  }
  if (y + tooltipRect.height > windowHeight - 10) {
    y = event.clientY - tooltipRect.height - 10
  }
  if (x < 10) x = 10
  if (y < 10) y = 10

  tooltip.value.x = x
  tooltip.value.y = y
  tooltip.value.width = tooltipRect.width
  tooltip.value.height = tooltipRect.height
}

const hideTooltip = () => {
  tooltip.value.visible = false
}

const getTooltipData = (entity, weekId, indicator, type) => {
  const weekData = type === 'store'
    ? getStoreWeekData(entity, weekId)
    : entity.weeklyData?.find(w => w.weekId === weekId) || {}

  const week = weeks.value.find(w => w.id === weekId)
  const indicatorConfig = availableIndicators.value.find(ind => ind.key === indicator)
  const currentGroup = indicatorGroups.value.find(group =>
    group.indicators.some(ind => ind.key === indicator)
  )

  const result = {
    entityName: entity.name,
    weekName: week?.name || `Неділя ${weekId}`,
    groupName: currentGroup?.label || 'Показники',
    indicator: indicatorConfig?.label || indicator,
    mainValue: getDisplayValue(weekData, indicator),
    details: []
  }

  if (currentGroup) {
    if (currentGroup.key === 'score') {
      result.details.push({
        label: 'Загальний бал',
        value: weekData.totalScore || 0
      })
    } else if (currentGroup.key === 'turnover') {
      result.details.push(
        { label: 'План', value: formatNumber(weekData.plan || 0) },
        {
          label: 'Факт',
          value: `${formatNumber(weekData.fact || 0)} (${weekData.percent || 0}% от плана)`
        },
        { label: 'Процент обороту', value: `${weekData.percent || 0}%` }
      )

      if (weekData.turnover_score !== undefined) {
        const maxScore = targetsData.value?.targetTree?.turnover?.maxScore || 100
        result.details.push({
          label: `Бал за оборот (з ${maxScore})`,
          value: weekData.turnover_score || 0
        })
      }
    } else {
      const groupKey = currentGroup.key
      const target = targetsData.value?.targetTree?.[groupKey]

      if (target) {
        const value = weekData[groupKey] || 0
        const percent = weekData[`${groupKey}_percent`] || 0
        const score = weekData[`${groupKey}_score`] || 0
        const targetValue = weekData[`${groupKey}_target`] || 0
        const factValue = weekData.fact || 0
        const planValue = factValue > 0 ? targetValue : 0

        result.details.push(
          { label: `${target.name} (факт)`, value: formatNumber(value) },
          {
            label: `План, коеф. %`,
            value: `  (${((targetValue / factValue) * 100).toFixed(2)}% від факту)`
          },
          {
            label: `Розрахунковий план. грн`,
            value: ` ${formatNumber(planValue)} `
          },
          {
            label: 'Факт обороту →',
            value: `${formatNumber(factValue)}`
          },
          { label: `Процент виконання`, value: `${percent}%` },
          {
            label: `Бал (з ${target.maxScore})`,
            value: `${score} / ${target.maxScore}`
          }
        )
      }
    }
  }

  if (weekData.columnRanks && weekData.columnRanks[indicator]) {
    const totalItems = type === 'store'
      ? regions.value?.reduce((total, region) => total + (region.stores?.length || 0), 0) || 0
      : regions.value?.length || 0

    result.details.push({
      label: 'Ранг по показнику',
      value: `${weekData.columnRanks[indicator]} з ${totalItems}`
    })
  }

  return result
}

const getDisplayValue = (weekData, indicator) => {
  switch (indicator) {
    case 'totalScore':
    case 'turnover_score':
      return weekData[indicator] || '-'
    case 'plan':
    case 'fact':
      return formatNumber(weekData[indicator] || '-')
    case 'percent':
      return `${weekData.percent || 0}%`
    default:
      if (indicator.endsWith('_percent')) {
        return `${weekData[indicator] || 0}%`
      } else if (indicator.endsWith('_score')) {
        return weekData[indicator] || '-'
      } else {
        return formatNumber(weekData[indicator] || '-')
      }
  }
}

const darkColors = ref([
  '#2c3e50', '#34495e', '#1abc9c', '#16a085', '#27ae60', '#2ecc71',
  '#8e44ad', '#9b59b6', '#2980b9', '#3498db', '#e74c3c', '#c0392b',
  '#d35400', '#e67e22', '#f39c12', '#f1c40f', '#7f8c8d', '#95a5a6'
])

const selectedColor = ref('#1c699b')
const isPaletteOpen = ref(false)

const darkenColor = (color, percent = 20) => {
  const num = parseInt(color.replace("#", ""), 16)
  const amt = Math.round(2.55 * percent)
  const R = (num >> 16) - amt
  const G = (num >> 8 & 0x00FF) - amt
  const B = (num & 0x0000FF) - amt
  return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
    (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
    (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1)
}

const headerStyle = computed(() => ({
  backgroundColor: selectedColor.value,
  color: '#fff',
  // borderCollapse: 'separate',
  borderSpacing: 0
}))

const changeColor = (color) => { selectedColor.value = color }
const togglePalette = () => { isPaletteOpen.value = !isPaletteOpen.value }
const closePalette = () => { isPaletteOpen.value = false }

const regionSortBy = ref({ weekId: 'week_1', columnKey: 'totalScore', direction: 'desc' })
const storeSortBy = ref({ weekId: 'week_1', columnKey: 'totalScore', direction: 'desc' })

const indicatorGroups = computed(() => {
  const groups = [
    {
      key: 'score',
      label: 'Заг. бал',
      indicators: [{ key: 'totalScore', label: `${planScore.value}` }]
    }
  ]

  if (targetsData.value?.targetTree) {
    Object.entries(targetsData.value.targetTree).forEach(([key, target]) => {
      if (key === 'turnover') {
        groups.push({
          key: 'turnover',
          label: 'Оборот',
          indicators: [
            { key: 'plan', label: 'План' },
            { key: 'fact', label: 'Факт' },
            { key: 'percent', label: '%' },
            { key: 'turnover_score', label: 'planScore.value' }
          ]
        })
      } else {
        groups.push({
          key: key,
          label: target.name,
          indicators: [
            { key: key, label: 'факт' },
            { key: `${key}_percent`, label: '%' },
            { key: `${key}_score`, label: 'Бал' }
          ]
        })
      }
    })
  } else {
    groups.push({
      key: 'turnover',
      label: 'Оборот',
      indicators: [
        { key: 'plan', label: 'План' },
        { key: 'fact', label: 'Факт' },
        { key: 'percent', label: '%' }
      ]
    })
  }

  return groups
})

const availableIndicators = computed(() => {
  const indicators = []
  indicatorGroups.value.forEach(group => {
    group.indicators.forEach(indicator => {
      indicators.push({
        ...indicator,
        groupKey: group.key,
        groupLabel: group.label
      })
    })
  })
  return indicators
})

const visible = reactive({})
const groupVisibility = reactive({})

const initializeVisibility = () => {
  indicatorGroups.value.forEach(group => {
    if (group.key === 'score') {
      groupVisibility[group.key] = true
    } else {
      groupVisibility[group.key] = false
    }
  })

  indicatorGroups.value.forEach(group => {
    group.indicators.forEach(indicator => {
      if (indicator.key === 'totalScore') {
        visible[indicator.key] = true
      } else if (indicator.key.includes('_score')) {
        visible[indicator.key] = true
      } else if (group.key === 'score') {
        visible[indicator.key] = true
      } else {
        visible[indicator.key] = groupVisibility[group.key] || false
      }
    })
  })
}

const toggleGroupVisibility = (groupKey) => {
  if (groupKey === 'score') return
  groupVisibility[groupKey] = !groupVisibility[groupKey]
  const group = indicatorGroups.value.find(g => g.key === groupKey)
  if (group) {
    group.indicators.forEach(indicator => {
      if (indicator.key.includes('_score') || indicator.key === 'totalScore') {
        visible[indicator.key] = true
      } else {
        visible[indicator.key] = groupVisibility[groupKey]
      }
    })
  }
}

const visibleIndicators = computed(() =>
  availableIndicators.value.filter(indicator => visible[indicator.key])
)

const visibleGroups = computed(() => {
  return indicatorGroups.value.map(group => ({
    ...group,
    indicators: group.indicators.filter(indicator => visible[indicator.key]),
    visibleCount: group.indicators.filter(indicator => visible[indicator.key]).length
  })).filter(group => group.visibleCount > 0)
})

const dynamicRowWidth = computed(() => {
  const total = visibleIndicators.value.length
  return total > 0 ? '100%' : '0%'
})

function getStyle(key) {
  const total = visibleIndicators.value.length
  const isVisible = visible[key]
  const width = isVisible ? `${100 / total}%` : '0%'

  return {
    width,
    transform: isVisible ? 'scaleX(1)' : 'scaleX(0)',
    willChange: 'transform',
    transformOrigin: 'left right',
    fontWeight: key === 'totalScore' ? '700' : 'normal',
    borderRight: isVisible ? '1px solid #ddd!important' : 'none!important',
  }
}

function getGroupStyle(groupKey) {
  const group = visibleGroups.value.find(g => g.key === groupKey)
  if (!group) return { width: '0%', transform: 'scaleX(0)' }

  const total = visibleIndicators.value.length
  const groupWidth = group.visibleCount > 0 ? `${(group.visibleCount / total) * 100}%` : '0%'

  return {
    width: groupWidth,
    transform: group.visibleCount > 0 ? 'scaleX(1)' : 'scaleX(0)',
    willChange: 'transform',
    transformOrigin: 'left right',
    background: group.visibleCount > 1 ? darkenColor(selectedColor.value, 13) : '',
  }
}

const processData = () => {
  if (!regions.value || !salesData.value || !targetsData.value) return

  regions.value.forEach(region => {
    if (region.stores) {
      region.stores.forEach(store => {
        store.regionId = region.id
        store.regionName = region.name
        store.regionColor = region.color
      })
    }
  })

  const allStores = []
  regions.value.forEach(region => {
    if (region.stores) {
      region.stores.forEach(store => {
        allStores.push(store)
      })
    }
  })

  salesData.value.weeks.forEach(week => {
    calculateWeeklyMetrics(week.id, allStores)
  })

  calculateRegionMetrics()
  calculateRegionColumnRanks()
  calculateOverallScores(allStores)
}

const calculateWeeklyMetrics = (weekId, allStores) => {
  const { targetTree, storeTargets } = targetsData.value

  allStores.forEach(store => {
    const weekData = getStoreWeekData(store, weekId)
    const storeTargetConfig = storeTargets[store.id] || {}
    weekData.percent = calculateTurnoverPercent(weekData.plan, weekData.fact)
    let weeklyScore = 0

    Object.entries(targetTree).forEach(([key, targetConfig]) => {
      if (key === 'turnover') return

      const targetPercent = storeTargetConfig[key] || 0
      const actualValue = weekData[key] || 0
      const target = targetPercent * weekData.fact
      let achievementPercent = 0

      if (target > 0) {
        if (targetConfig.type === 'negative') {
          achievementPercent = Math.min((target / actualValue) * 100, 200)
        } else {
          achievementPercent = (actualValue / target) * 100
        }
      }

      weekData[`${key}_percent`] = Math.round(achievementPercent)
      weekData[`${key}_target`] = target
    })

    Object.entries(targetTree).forEach(([key, targetConfig]) => {
      if (key === 'turnover') return

      const achievementPercent = weekData[`${key}_percent`] || 0
      const maxPercent = Math.max(...allStores.map(s => {
        const sWeekData = getStoreWeekData(s, weekId)
        return sWeekData[`${key}_percent`] || 0
      }))

      let score = 0
      if (maxPercent > 0) {
        score = Math.round((achievementPercent / maxPercent) * targetConfig.maxScore)
      }

      weekData[`${key}_score`] = score
      weeklyScore += score
    })

    weekData.totalScore = weeklyScore
  })

  if (targetTree.turnover) {
    const maxTurnoverPercent = Math.max(...allStores.map(store => {
      const weekData = getStoreWeekData(store, weekId)
      return weekData.percent || 0
    }))

    allStores.forEach(store => {
      const weekData = getStoreWeekData(store, weekId)
      const turnoverPercent = weekData.percent || 0
      let turnoverScore = 0

      if (maxTurnoverPercent > 0) {
        turnoverScore = Math.round((turnoverPercent / maxTurnoverPercent) * targetTree.turnover.maxScore)
      }

      weekData.turnover_score = turnoverScore
      weekData.totalScore = (weekData.totalScore || 0) + turnoverScore
    })
  } else {
    allStores.forEach(store => {
      const weekData = getStoreWeekData(store, weekId)
      const turnoverScore = Math.round(weekData.percent || 0)
      weekData.totalScore = (weekData.totalScore || 0) + turnoverScore
    })
  }

  calculateColumnRanks(weekId, allStores)
}

const calculateRegionMetrics = () => {
  if (!regions.value || !salesData.value || !targetsData.value) return
  const { targetTree, storeTargets } = targetsData.value
  salesData.value.weeks.forEach(week => {
    regions.value.forEach(region => {
      if (!region.stores) return
      if (!region.weeklyData) {
        region.weeklyData = []
      }

      let regionWeekData = region.weeklyData.find(w => w.weekId === week.id)
      if (!regionWeekData) {
        regionWeekData = { weekId: week.id }
        region.weeklyData.push(regionWeekData)
      }
      let totalPlan = 0
      let totalFact = 0
      region.stores.forEach(store => {
        const storeWeekData = getStoreWeekData(store, week.id)
        totalPlan += storeWeekData.plan || 0
        totalFact += storeWeekData.fact || 0
      })

      regionWeekData.plan = totalPlan
      regionWeekData.fact = totalFact
      regionWeekData.percent = calculateTurnoverPercent(totalPlan, totalFact)

      Object.entries(targetTree).forEach(([key, targetConfig]) => {
        if (key === 'turnover') return
        let totalValue = 0
        let totalTarget = 0
        region.stores.forEach(store => {
          const storeWeekData = getStoreWeekData(store, week.id)
          const storeTargetConfig = storeTargets[store.id] || {}
          const targetPercent = storeTargetConfig[key] || 0

          totalValue += storeWeekData[key] || 0
          totalTarget += targetPercent * (storeWeekData.fact || 0)
        })

        regionWeekData[key] = totalValue

        let achievementPercent = 0
        if (totalTarget > 0) {
          if (targetConfig.type === 'negative') {
            achievementPercent = Math.min((totalTarget / totalValue) * 100, 200)
          } else {
            achievementPercent = (totalValue / totalTarget) * 100
          }
        }

        regionWeekData[`${key}_percent`] = Math.round(achievementPercent)
        regionWeekData[`${key}_target`] = totalTarget
      })
    })

    Object.entries(targetTree).forEach(([key, targetConfig]) => {
      if (key === 'turnover') return
      const maxPercent = Math.max(...regions.value.map(region => {
        const regionWeekData = region.weeklyData?.find(w => w.weekId === week.id)
        return regionWeekData?.[`${key}_percent`] || 0
      }))

      regions.value.forEach(region => {
        const regionWeekData = region.weeklyData?.find(w => w.weekId === week.id)
        if (!regionWeekData) return

        const achievementPercent = regionWeekData[`${key}_percent`] || 0
        let score = 0
        if (maxPercent > 0) {
          score = Math.round((achievementPercent / maxPercent) * targetConfig.maxScore)
        }
        regionWeekData[`${key}_score`] = score
      })
    })

    if (targetTree.turnover) {
      const maxTurnoverPercent = Math.max(...regions.value.map(region => {
        const regionWeekData = region.weeklyData?.find(w => w.weekId === week.id)
        return regionWeekData?.percent || 0
      }))

      regions.value.forEach(region => {
        const regionWeekData = region.weeklyData?.find(w => w.weekId === week.id)
        if (!regionWeekData) return

        const turnoverPercent = regionWeekData.percent || 0
        let turnoverScore = 0
        if (maxTurnoverPercent > 0) {
          turnoverScore = Math.round((turnoverPercent / maxTurnoverPercent) * targetTree.turnover.maxScore)
        }
        regionWeekData.turnover_score = turnoverScore
      })
    }

    regions.value.forEach(region => {
      const regionWeekData = region.weeklyData?.find(w => w.weekId === week.id)
      if (!regionWeekData) return

      let totalScore = 0

      Object.entries(targetTree).forEach(([key, targetConfig]) => {
        if (key === 'turnover') {
          totalScore += regionWeekData.turnover_score || 0
        } else {
          totalScore += regionWeekData[`${key}_score`] || 0
        }
      })

      regionWeekData.totalScore = totalScore
    })
  })
}

const calculateOverallScores = (allStores) => {
  allStores.forEach(store => {
    let totalScore = 0
    salesData.value.weeks.forEach(week => {
      const weekData = getStoreWeekData(store, week.id)
      totalScore += weekData.totalScore || 0
    })
    store.overallTotalScore = totalScore
  })

  allStores.sort((a, b) => b.overallTotalScore - a.overallTotalScore)
  allStores.forEach((store, index) => {
    store.overallRank = index + 1
  })
}

const weeks = computed(() => {
  if (!salesData.value?.weeks) return []
  return [...salesData.value.weeks].sort((a, b) => b.id - a.id)
})

const calculateColumnRanks = (weekId, allStores) => {
  const indicators = availableIndicators.value.map(ind => ind.key)

  indicators.forEach(indicator => {
    const storesWithValues = allStores.map(store => {
      const weekData = getStoreWeekData(store, weekId)
      let value = 0

      switch (indicator) {
        case 'totalScore':
          value = weekData.totalScore || 0
          break
        case 'percent':
          value = weekData.percent || 0
          break
        case 'plan':
          value = weekData.plan || 0
          break
        case 'fact':
          value = weekData.fact || 0
          break
        default:
          value = weekData[indicator] || 0
          break
      }

      return { store, value, weekData }
    })

    storesWithValues.sort((a, b) => b.value - a.value)
    storesWithValues.forEach((item, index) => {
      if (!item.weekData.columnRanks) {
        item.weekData.columnRanks = {}
      }
      item.weekData.columnRanks[indicator] = index + 1
    })
  })
}

const calculateRegionColumnRanks = () => {
  if (!regions.value || !salesData.value) return

  salesData.value.weeks.forEach(week => {
    const indicators = availableIndicators.value.map(ind => ind.key)
    indicators.forEach(indicator => {
      const regionsWithValues = regions.value.map(region => {
        let value = getRegionIndicatorValue(region, week.id, indicator)
        return { region, value }
      })

      regionsWithValues.sort((a, b) => b.value - a.value)
      regionsWithValues.forEach((item, index) => {
        if (!item.region.columnRanks) {
          item.region.columnRanks = {}
        }
        if (!item.region.columnRanks[week.id]) {
          item.region.columnRanks[week.id] = {}
        }
        item.region.columnRanks[week.id][indicator] = index + 1
      })
    })
  })
}

const getRegionIndicatorValue = (region, weekId, indicator) => {
  const regionWeekData = region.weeklyData?.find(w => w.weekId === weekId)
  if (!regionWeekData) return 0
  return regionWeekData[indicator] || 0
}

const sortedRegions = computed(() => {
  if (!regions.value) return []
  let sorted = [...regions.value]

  sorted.forEach(region => {
    let totalScore = 0
    if (region.weeklyData) {
      region.weeklyData.forEach(weekData => {
        totalScore += weekData.totalScore || 0
        console.log(weekData);
      })
    }
    region.overallTotalScore = totalScore
  })



  sorted.sort((a, b) => {
    let aValue = 0
    let bValue = 0

    if (regionSortBy.value.columnKey === 'totalScore') {
      // aValue = a.overallTotalScore
      // bValue = b.overallTotalScore
      aValue = getRegionIndicatorValue(a, regionSortBy.value.weekId, regionSortBy.value.columnKey)
      bValue = getRegionIndicatorValue(b, regionSortBy.value.weekId, regionSortBy.value.columnKey)
    } else {
      aValue = getRegionIndicatorValue(a, regionSortBy.value.weekId, regionSortBy.value.columnKey)
      bValue = getRegionIndicatorValue(b, regionSortBy.value.weekId, regionSortBy.value.columnKey)
    }

    return regionSortBy.value.direction === 'desc' ? bValue - aValue : aValue - bValue
  })

  // sorted.forEach((region, index) => {
  //   region.regionRank = index + 1
  // })

  return sorted
})

const allStores = computed(() => {
  const stores = []

  regions.value.forEach(region => {
    if (region.stores) {
      region.stores.forEach(store => {
        stores.push({
          ...store,
          regionId: region.id,
          regionName: region.name,
          regionColor: region.color
        })
      })
    }
  })

  if (storeSortBy.value.columnKey && storeSortBy.value.weekId) {
    stores.sort((a, b) => {
      let aValue = getStoreSortValue(a, storeSortBy.value.weekId, storeSortBy.value.columnKey)
      let bValue = getStoreSortValue(b, storeSortBy.value.weekId, storeSortBy.value.columnKey)
      return storeSortBy.value.direction === 'desc' ? bValue - aValue : aValue - bValue
    })
  } else if (sortByTotalScore.value) {
    stores.sort((a, b) => (b.overallTotalScore) - (a.overallTotalScore))
  }

  return stores
})

const getStoreSortValue = (store, weekId, indicator) => {
  const weekData = getStoreWeekData(store, weekId)
  switch (indicator) {
    case 'totalScore': return weekData.totalScore || 0
    case 'percent': return weekData.percent || 0
    case 'plan': return weekData.plan || 0
    case 'fact': return weekData.fact || 0
    default: return weekData[indicator] || 0
  }
}

const handleStoreSort = (weekId, indicator) => {
  if (storeSortBy.value.weekId === weekId && storeSortBy.value.columnKey === indicator) {
    storeSortBy.value.direction = storeSortBy.value.direction === 'desc' ? 'asc' : 'desc'
  } else {
    storeSortBy.value = { weekId, columnKey: indicator, direction: 'desc' }
  }
}

const getStoreSortIcon = (weekId, indicator) => {
  if (storeSortBy.value.weekId === weekId && storeSortBy.value.columnKey === indicator) {
    return storeSortBy.value.direction === 'desc' ? '▼' : '▲'
  }
  return '↕'
}

const getStoreSortArrowClass = (weekId, indicator) => {
  if (storeSortBy.value.weekId === weekId && storeSortBy.value.columnKey === indicator) {
    return storeSortBy.value.direction === 'desc' ? 'odx-sort-control--desc' : 'odx-sort-control--asc'
  }
  return 'odx-sort-control--inactive'
}

const handleRegionSort = (weekId, indicator) => {
  if (regionSortBy.value.weekId === weekId && regionSortBy.value.columnKey === indicator) {
    regionSortBy.value.direction = regionSortBy.value.direction === 'desc' ? 'asc' : 'desc'
  } else {
    regionSortBy.value = { weekId, columnKey: indicator, direction: 'desc' }
  }
}

const getSortIcon = (weekId, indicator) => {
  if (regionSortBy.value.weekId === weekId && regionSortBy.value.columnKey === indicator) {
    return regionSortBy.value.direction === 'desc' ? '▼' : '▲'
  }
  return '↕'
}

const getStoreWeekData = (store, weekId) => {
  if (!store || !store.weeklyData) {
    return { plan: 0, fact: 0, percent: 0, totalScore: 0 }
  }
  const weekData = store.weeklyData.find(w => w.weekId === weekId)
  return weekData || { plan: 0, fact: 0, percent: 0, totalScore: 0 }
}

const getStoreData = (store, weekId, indicator) => {
  const weekData = getStoreWeekData(store, weekId, indicator)

  switch (indicator) {
    case 'totalScore': return weekData.totalScore || '-'
    case 'plan': return formatNumber(weekData.plan)
    case 'fact': return formatNumber(weekData.fact)
    case 'percent': return weekData.percent ? `${weekData.percent}%` : '0%'
    case 'turnover_score': return weekData.turnover_score || '-'
    default:
      if (indicator.endsWith('_percent')) {
        return weekData[indicator] ? `${weekData[indicator]}%` : '0%'
      } else if (indicator.endsWith('_score')) {
        return weekData[indicator] || '-'
      } else {
        return formatNumber(weekData[indicator] || '-')
      }
  }
}

const getRegionData = (region, weekId, indicator) => {
  const value = getRegionIndicatorValue(region, weekId, indicator)

  switch (value) {
    case 'totalScore': return value
    case 'percent': return `${value}%`
    case 'plan':
    case 'fact': return formatNumber(value)
    case 'turnover_score': return value
    default:
      if (indicator.endsWith('_percent')) {
        return `${value}%`
      } else if (indicator.endsWith('_score')) {
        return value
      } else {
        return formatNumber(value)
      }
  }
}

const calculateTurnoverPercent = (plan, fact) => {
  if (!plan || plan === 0) return 0
  return Math.round((fact / plan) * 100)
}

const formatNumber = (number) => {
  if (number === null || number === undefined || isNaN(number)) {
    return '-'
  }
  return new Intl.NumberFormat('UA', { maximumFractionDigits: 0 }).format(number)
}

const getStoreRowClass = (rank) => {
  if (rank <= 3) return 'odx-table__row--top-rank'
  if (rank <= 6) return 'odx-table__row--mid-rank'
  return 'odx-table__row--low-rank'
}

const getRegionRowClass = (regionRank) => {
  if (regionRank <= 2) return 'odx-table__row--region-top'
  if (regionRank <= 4) return 'odx-table__row--region-mid'
  return 'odx-table__row--region-low'
}

const getCellClass = (indicator, weekData, isRegion = false, weekId = null, region = null) => {
  const classes = []

  if (indicator === 'totalScore') {
    classes.push('odx-table__cell--score')
  }

  let rank = 0
  let totalItems = 0

  if (isRegion && region && weekId) {
    rank = region.columnRanks?.[weekId]?.[indicator] || 0
    totalItems = regions.value?.length || 0
  } else {
    rank = weekData.columnRanks?.[indicator] || 0
    totalItems = regions.value?.reduce((total, region) => {
      return total + (region.stores?.length || 0)
    }, 0) || 0
  }

  if (rank > 0 && totalItems > 0) {
    const percentile = (rank / totalItems) * 100
    if (indicator.endsWith('_score') || indicator === 'totalScore' ||
      indicator.endsWith('_percent') || indicator === 'percent') {

      if (percentile <= 20) {
        classes.push('odx-table__cell--percentile-top')
        if (formatter.value) { classes.push('odx-table__cell--formatted-top') }
      } else if (percentile <= 40) {
        classes.push('odx-table__cell--percentile-excellent')
        if (formatter.value) { classes.push('odx-table__cell--formatted-excellent') }
      } else if (percentile <= 60) {
        classes.push('odx-table__cell--percentile-good')
        if (formatter.value) { classes.push('odx-table__cell--formatted-good') }
      } else if (percentile <= 80) {
        classes.push('odx-table__cell--percentile-average')
        if (formatter.value) { classes.push('odx-table__cell--formatted-average') }
      } else {
        classes.push('odx-table__cell--percentile-poor')
        if (formatter.value) { classes.push('odx-table__cell--formatted-poor') }
      }
    }
  }

  return classes.join(' ')
}

const getIndicatorHeader = (indicator) => {
  if (indicator.key.endsWith('_score')) {
    const baseKey = indicator.key.replace('_score', '')
    if (baseKey === 'turnover' && targetsData.value?.targetTree?.turnover) {
      return targetsData.value.targetTree.turnover.maxScore.toString()
    } else if (targetsData.value?.targetTree?.[baseKey]) {
      return targetsData.value.targetTree[baseKey].maxScore.toString()
    }
    return 'Бал'
  }
  return indicator.label
}

const getRegionCellClass = (indicator, region, weekId) => {
  const regionWeekData = region.weeklyData?.find(w => w.weekId === weekId) || {}

  if (region.columnRanks && region.columnRanks[weekId]) {
    regionWeekData.columnRanks = { [indicator]: region.columnRanks[weekId][indicator] }
  }

  return getCellClass(indicator, regionWeekData, true, weekId, region)
}

const getSortArrowClass = (weekId, indicator) => {
  if (regionSortBy.value.weekId === weekId && regionSortBy.value.columnKey === indicator) {
    return regionSortBy.value.direction === 'desc' ? 'odx-sort-arrow--desc' : 'odx-sort-arrow--asc'
  }
  return 'odx-sort-arrow--inactive'
}

const refreshData = async () => {
  await loadData()
}

onMounted(() => {
  // Слушаем события изменения планов
  window.addEventListener('plansDataUpdated', handlePlansDataUpdate)
  loadData()
})

// Очистка слушателей
onUnmounted(() => {
  window.removeEventListener('plansDataUpdated', handlePlansDataUpdate)
})

</script>

<style lang="scss" scoped>
.odx-sales-dashboard {
  --odx-primary: #1c699b;
  --odx-success: #10b981;
  --odx-warning: #f59e0b;
  --odx-danger: #ef4444;
  --odx-info: #6366f1;
  --odx-text: #1e293b;
  --odx-text-muted: #64748b;
  --odx-border: #e2e8f0;
  --odx-surface: #ffffff;
  --odx-surface-hover: #f8fafc;
  --odx-neutral: #f1f5f9;

  width: 100%;
  height: 100vh;
  overflow-y: auto;
  padding: 0;
  margin: 0;
  background: var(--odx-neutral);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  position: relative;
  box-sizing: border-box;

  * {
    box-sizing: border-box;
  }

  .odx-palette-toggle {
    position: fixed;
    bottom: 10px;
    right: 10px;
    width: 20px;
    height: 20px;
    cursor: pointer;
    z-index: 1000;
    border-radius: 4px;
    transition: transform 0.2s ease;

    &:hover {
      transform: scale(1.1);
    }

    &--active {
      transform: scale(1.2);
    }
  }

  .odx-color-palette {
    position: fixed;
    top: 0;
    right: -300px;
    width: 280px;
    height: 100vh;
    background: var(--odx-surface);
    border-left: 1px solid var(--odx-border);
    z-index: 1001;
    transition: right 0.3s ease;
    overflow-y: auto;
    box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);

    &--open {
      right: 0;
    }

    &__content {
      padding: 20px;
    }

    &__grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin: 20px 0;
    }
  }

  .odx-color-option {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.2s ease;

    &:hover {
      transform: scale(1.1);
    }

    &--selected {
      border-color: var(--odx-text);
      box-shadow: 0 0 0 2px var(--odx-border);
    }
  }

  .odx-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.3);
    z-index: 1000;
    cursor: pointer;
  }

  .odx-loading {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--odx-border);
    z-index: 2000;
    overflow: hidden;

    &__progress {
      height: 100%;
      background: var(--odx-primary);
      animation: odx-loading 1.5s ease-in-out infinite;
    }
  }

  @keyframes odx-loading {
    0% {
      width: 0%;
      transform: translateX(-100%);
    }

    50% {
      width: 70%;
      transform: translateX(0%);
    }

    100% {
      width: 100%;
      transform: translateX(100%);
    }
  }

  .odx-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    padding: 40px;
    margin: 20px;
    background: var(--odx-surface);
    border-radius: 12px;
    border: 1px solid var(--odx-border);

    &__icon {
      font-size: 48px;
      margin-bottom: 16px;
      color: var(--odx-warning);
    }

    &__message {
      color: var(--odx-text);
      font-size: 16px;
      text-align: center;
      margin-bottom: 16px;
    }

    &__retry {
      padding: 12px 20px;
      background: var(--odx-primary);
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.2s ease;

      &:hover {
        background: #2563eb;
        transform: translateY(-1px);
      }
    }
  }

  .odx-dashboard {
    padding: 20px;
    animation: odx-fadeIn 0.6s ease-out;
  }

  @keyframes odx-fadeIn {
    from {
      opacity: 0;
      transform: translateY(16px);
    }

    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .odx-controls {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 16px 20px;
    background: var(--odx-surface);
    border-radius: 8px;
    border: 1px solid var(--odx-border);
    margin-bottom: 16px;

    &__refresh {
      display: flex;
      align-items: center;
      padding: 6px 10px;
      border: 1px solid var(--odx-border);
      // background: var(--odx-primary);
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 400;
      transition: all 0.2s ease;

      &:hover:not(:disabled) {
        transform: translateY(-1px);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }

  .odx-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-size: 14px;
    color: var(--odx-text-muted);

    input[type="checkbox"] {
      display: none;
    }

    &__slider {
      width: 36px;
      height: 20px;
      background: var(--odx-border);
      border-radius: 20px;
      position: relative;
      transition: all 0.3s ease;

      &::after {
        content: '';
        position: absolute;
        width: 16px;
        height: 16px;
        background: white;
        border-radius: 50%;
        top: 2px;
        left: 2px;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
      }
    }

    input[type="checkbox"]:checked+&__slider {
      // background: var(--odx-primary);

      &::after {
        transform: translateX(16px);
      }
    }

    &__label {
      user-select: none;
      white-space: nowrap;
      color: var(--odx-text-muted);
    }
  }

  .odx-table-container {
    // background: var(--odx-surface);
    border-radius: 12px;
    border: 1px solid var(--odx-border);
    // overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }

  .odx-table {
    width: 100%;
    // border-collapse: separate;
    border-spacing: 0;

    &__header {

      position: sticky;
      top: 0;
      z-index: 10;
      // background: var(--odx-surface);
      border-bottom: 2px solid var(--odx-border);
    }

    &__row {
      display: flex;
      width: 100%;
      // border-bottom: 1px solid var(--odx-border);
      // transition: all 0.15s ease;
      will-change: transform;
      transition: all .2s ease;
      transform-origin: center;

      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        z-index: 5;
        position: relative;
      }

      &--header-top,
      &--header-middle,
      &--header-bottom {
        &:hover {
          transform: none;
          box-shadow: none;
        }
      }

      // &--region {
      //   background: var(--odx-neutral);
      //   font-weight: 600;
      //   border-bottom: 2px solid var(--odx-border);
      // }

      // &--store {
      //   background: var(--odx-surface);
      // }

      // &--top-rank {
      //   background: #ecfdf5;
      //   border-left: 4px solid var(--odx-success);
      // }

      // &--mid-rank {
      //   background: #fffbeb;
      //   border-left: 4px solid var(--odx-warning);
      // }

      // &--low-rank {
      //   background: #fef2f2;
      //   border-left: 4px solid var(--odx-danger);
      // }

      // &--region-top {
      //   background: #ecfdf5;
      //   border-left: 6px solid var(--odx-success);
      // }

      // &--region-mid {
      //   background: #fffbeb;
      //   border-left: 6px solid var(--odx-warning);
      // }

      // &--region-low {
      //   background: #fef2f2;
      //   border-left: 6px solid var(--odx-danger);
      // }
    }

    &__cell {
      height: 32px;
      padding: 6px 0px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 13px;
      border-right: 1px solid var(--odx-border);
      text-align: center;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      transition: transform 0.5s ease;
      will-change: transform;

      &--static {
        min-width: 230px;
        flex-shrink: 0;
        // background: var(--odx-neutral);
        font-weight: 600;
        border-right: 2px solid var(--odx-border);
        justify-content: flex-start;
        padding-left: 16px;
      }

      &--group {
        // background: #eef2ff;
        // color: var(--odx-info);
        font-size: 15px;
        font-weight: 700;
        // border-bottom: 2px solid var(--odx-info);
        border-bottom: 1px solid var(--odx-border);
      }

      &--group-header {
        // background: var(--odx-surface);
        font-size: 13px;
        // color: var(--odx-text-muted);
        cursor: pointer;

        &:hover {
          background: #0d598a;
          // color: white;
        }
      }

      &--metric {
        // background: var(--odx-surface);
        font-size: 12px;
        // color: var(--odx-text-muted);
        cursor: pointer;

        &:hover {
          background: #0d598a;
          color: white;
        }
      }

      &--data {
        font-size: 13px;
        font-weight: 500;
        color: var(--odx-text);
      }

      &--score {
        font-weight: 700;
        color: var(--odx-primary);
      }

      &--percentile-top {
        color: #2e7d32;
        font-weight: 600;
      }

      &--percentile-excellent {
        color: #2e7d32;
        font-weight: 600;
      }

      &--percentile-good {
        color: #f57c00;
        font-weight: 600;
      }

      &--percentile-average {
        color: #ea580c;
        font-weight: 600;
      }

      &--percentile-poor {
        color: #dc2626;
        font-weight: 600;
      }

      &--formatted-top {
        background-color: #d0ffea;
        // color: white;
      }

      &--formatted-excellent {
        background-color: #ebfff6;
        // color: #2e7d32;
      }

      &--formatted-good {
        background-color: #fff3e1;
        color: #f57c00;
      }

      &--formatted-average {
        background-color: #fee7c5;
        // color: #ea580c;
      }

      &--formatted-poor {
        background-color: #ffdada;
        // color: white;
      }
    }

    &__data {
      display: flex;
      width: 100%;
      overflow: hidden;
      transition: all .2s ease;
      transform-origin: center;
    }

    &__body {
      background: var(--odx-surface);
    }
  }

  .odx-week {
    display: flex;
    width: 100%;
    border-right: 2px solid var(--odx-border);
    overflow: hidden;
    border-bottom: 1px solid var(--odx-border);

    &__name {
      font-weight: 600;
      // color: var(--odx-info);
      padding: 12px;
      text-align: center;
      font-size: 14px;
      margin: 0;
    }

    &__groups,
    &__columns {
      width: 100%;
      display: flex;
    }
  }

  .odx-group-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 4px 0px;

  }

  .odx-metric-header {
    display: flex;
    align-items: center;
    justify-content: center;

    width: 100%;
  }

  .odx-sort-arrow {
    margin-left: 5px;
    font-size: 10px;
    opacity: 0.6;
    transition: all 0.2s ease;

    &--active {
      opacity: 1;
      color: black;
      font-weight: bold;
    }

    &--desc {
      color: black;
    }

    &--asc {
      color: black;
    }

    &--inactive {
      opacity: 0.3;
    }
  }

  .odx-region-info,
  .odx-store-info {
    display: flex;
    align-items: center;
    gap: 8px;

    &__indicator {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      flex-shrink: 0;
      border: 1px solid rgba(255, 255, 255, 0.8);
    }

    &__title,
    &__name {
      font-weight: 600;
      color: var(--odx-text);
      font-size: 14px;
    }

    &__region {
      font-size: 12px;
      color: var(--odx-text-muted);
      font-weight: 400;
    }
  }

  .odx-store-info {
    &__name {
      font-weight: 400;
    }
  }

  .odx-separator {
    height: 16px;
    background: var(--odx-neutral);
    border-top: 1px solid var(--odx-border);
    border-bottom: 1px solid var(--odx-border);
  }

  .odx-sort-controls {
    display: flex;
    flex-direction: column;

    &__row {
      display: flex;
      width: 100%;
      align-items: center;
      transition: all .2s ease;
      transform-origin: center;
    }

    &__static {
      min-width: 230px;
      flex-shrink: 0;
      padding: 4px 8px;
      font-size: 12px;
      color: var(--odx-text-muted);
    }

    &__weeks {
      display: flex;
      width: 100%;
    }
  }

  .odx-sort-week {
    display: flex;
    width: 100%;
    border-right: 1px solid var(--odx-border);

    &__columns {
      width: 100%;
      display: flex;
    }
  }

  .odx-sort-control {
    // padding: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.2s ease;
    border: 1px solid transparent;
    transition: all .2s ease;
    transform-origin: center;

    &:hover {
      background: var(--odx-surface-hover);
      border-color: var(--odx-border);
    }

    &--desc,
    &--asc {
      // background: var(--odx-primary);
      color: black;
      // border-color: var(--odx-primary);
    }

    &--inactive {
      opacity: 0.5;
    }
  }

  .tooltip-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-secondary);
    transition: all 0.2s ease;
  }

  .tooltip-toggle:hover {
    color: var(--text-primary);
  }

  .tooltip-toggle input[type="checkbox"] {
    display: none;
  }

  .toggle-slider {
    width: 36px;
    height: 20px;
    background: var(--border-color);
    border-radius: 20px;
    position: relative;
    transition: all 0.3s ease;
  }

  .toggle-slider::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    background: white;
    border-radius: 50%;
    top: 2px;
    left: 2px;
    transition: all 0.3s ease;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  }

  .tooltip-toggle input[type="checkbox"]:checked+.toggle-slider {
    background: red
  }

  .tooltip-toggle input[type="checkbox"]:checked+.toggle-slider::after {
    transform: translateX(16px);
  }

  .toggle-label {
    user-select: none;
    white-space: nowrap;
    color: silver;
  }

  .odx-tooltip {
    position: fixed;
        z-index: 10000;
        background: var(--surface);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-xl);
        padding: 16px;
        min-width: 290px;
        max-width: 600px;
        pointer-events: none;
        font-size: 13px;
        backdrop-filter: blur(8px);
        animation: tooltipFadeIn 0.2s ease-out;
        transition: opacity 0.1s ease;


        max-height: 80vh;
        overflow-y: auto;

        &::-webkit-scrollbar {
            width: 4px;
        }

        &::-webkit-scrollbar-track {
            background: var(--border-light);
            border-radius: 2px;
        }

        &::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 2px;
        }
  }

  @keyframes odx-tooltipFadeIn {
    from {
      opacity: 0;
      transform: translateY(-8px);
    }

    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .odx-tooltip-trigger {
    cursor: help;

    &:hover {
      background: rgba(59, 130, 246, 0.05);
    }
  }

  .kpi {

    .comp {
      width: 60px;
      height: 60px;
      border: #2c3e50 1px solid;
      border-radius: 6px;
    }

    .kpi-toggle-btn {
      position: fixed;
      padding: 1px;
      top: 50%;
      right: 10px;
      z-index: 1000;
      display: flex;
      align-items: center;
      // gap: 8px;
      background: white;
      color: white;
      border: none;
      border-radius: 6px;
      font-weight: 600;
      font-size: 14px;
      cursor: pointer;
      // box-shadow: var(--shadow-lg);
      transition: all 0.3s ease;
    }

    .kpi-toggle-btn:hover {
      background: #2c3e50;
      // transform: translateY(-1px);
      // box-shadow: var(--shadow-xl);
    }

    .kpi-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 1001;
      backdrop-filter: blur(4px);
      animation: fadeIn 0.3s ease;
      border-left: var(--shadow-md)
    }

    @keyframes fadeIn {
      from {
        opacity: 0;
      }

      to {
        opacity: 1;
      }
    }

    .kpi-sidebar {
      position: fixed;
      top: 0;
      right: 0;
      width: 420px;
      height: 100vh;
      background: white;
      box-shadow: var(--shadow-xl);
      z-index: 1002;
      transform: translateX(100%);
      transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
      display: flex;
      flex-direction: column;
      box-shadow: 0 0 15px 0px #818181;
    }

    .kpi-sidebar--open {
      transform: translateX(0);
    }

    .kpi-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 20px 24px;
      border-bottom: 2px solid var(--border-color);
      background: var(--neutral-light);
      position: sticky;
      top: 0;
      z-index: 10;
    }

    .kpi-header h2 {
      margin: 0;
      font-size: 18px;
      font-weight: 700;
      color: var(--text-primary);
    }

    .close-btn {
      width: 32px;
      height: 32px;
      border: none;
      background: var(--border-light);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      color: var(--text-secondary);
      font-size: 16px;
      transition: all 0.2s ease;
    }

    .close-btn:hover {
      background: var(--danger-light);
      color: var(--danger-color);
      transform: scale(1.1);
    }

    .kpi-content {
      flex: 1;
      overflow-y: auto;
      padding: 24px;
      scroll-behavior: smooth;
    }

    .kpi-content::-webkit-scrollbar {
      width: 6px;
    }

    .kpi-content::-webkit-scrollbar-track {
      background: var(--border-light);
    }

    .kpi-content::-webkit-scrollbar-thumb {
      background: var(--border-color);
      border-radius: 3px;
    }

    .kpi-section {
      margin-bottom: 20px;
      animation: slideUp 0.6s ease;
    }

    @keyframes slideUp {
      from {
        opacity: 0;
        transform: translateY(20px);
      }

      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .kpi-section h3 {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .kpi-cards {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
      margin-bottom: 16px;
      padding: 5px;
    }

    .kpi-card {
      padding: 16px;
      border-radius: var(--radius-lg);
      text-align: center;
      border: 2px solid transparent;
      transition: all 0.3s ease;
    }

    .kpi-card:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }

    .kpi-card.primary {
      background: var(--info-light);
      border-color: var(--info-color);
    }

    .kpi-card.success {
      background: var(--success-light);
      border-color: var(--odx-success);
    }

    .kpi-card.warning {
      background: var(--warning-light);
      border-color: var(--odx-warning);
    }

    .kpi-card.danger {
      background: var(--danger-light);
      border-color: var(--odx-danger);
    }

    .kpi-card.info {
      background: var(--neutral-light);
      border-color: var(--border-color);
    }

    .kpi-value {
      font-size: 24px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 4px;
    }

    .kpi-label {
      font-size: 12px;
      font-weight: 500;
      color: var(--text-secondary);
    }

    .kpi-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .kpi-list-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 16px;
      background: var(--surface-hover);
      border-radius: var(--radius-md);
      border: 1px solid var(--border-light);
      transition: all 0.2s ease;
    }

    .kpi-list-item:hover {
      background: var(--surface);
      border-color: var(--border-color);
      transform: translateX(4px);
    }

    .kpi-list-item.rank-1 {
      background: var(--success-light);
      border-color: var(--success-color);
    }

    .kpi-list-item.rank-2 {
      background: var(--warning-light);
      border-color: var(--warning-color);
    }

    .kpi-list-item.rank-3 {
      background: var(--info-light);
      border-color: var(--info-color);
    }

    .rank-badge {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 12px;
      color: white;
      background: var(--text-secondary);
      flex-shrink: 0;
    }

    .rank-1 .rank-badge {
      background: var(--success-color);
    }

    .rank-2 .rank-badge {
      background: var(--warning-color);
    }

    .rank-3 .rank-badge {
      background: var(--info-color);
    }

    .region-info,
    .store-info {
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1;
    }

    .region-indicator {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      border: 2px solid white;
      flex-shrink: 0;
    }

    .store-region-indicator {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    .region-name,
    .store-name {
      font-weight: 600;
      color: var(--text-primary);
      font-size: 14px;
    }

    .store-region {
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 400;
    }

    .region-score,
    .store-score {
      font-weight: 700;
      color: var(--primary-color);
      font-size: 14px;
      flex-shrink: 0;
    }

    .problem-details {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-top: 12px;
    }

    .problem-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      background: var(--danger-light);
      border-radius: var(--radius-sm);
      border: 1px solid var(--danger-color);
    }

    .issue-type {
      font-weight: 600;
      color: var(--danger-color);
      font-size: 13px;
    }

    .issue-stats {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 2px;
    }

    .issue-value {
      font-weight: 700;
      color: var(--text-primary);
      font-size: 14px;
    }

    .issue-stores {
      font-size: 11px;
      color: var(--text-muted);
    }

    .week-comparison {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .week-stats {
      padding: 16px;
      background: var(--surface-hover);
      border-radius: var(--radius-md);
      border: 1px solid var(--border-light);
    }

    .week-header {
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border-color);
    }

    .week-name {
      font-weight: 600;
      color: var(--text-primary);
      font-size: 14px;
    }

    .week-period {
      font-size: 12px;
      color: var(--text-muted);
    }

    .week-metrics {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .metric {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .metric-label {
      font-size: 12px;
      color: var(--text-secondary);
    }

    .metric-value {
      font-weight: 600;
      color: var(--text-primary);
      font-size: 13px;
    }

    .trend-indicator {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      background: var(--neutral-light);
      border-radius: var(--radius-md);
      border: 1px solid var(--border-color);
    }

    .trend-label {
      font-weight: 600;
      color: var(--text-secondary);
      font-size: 13px;
    }

    .trend-value {
      font-weight: 600;
      font-size: 13px;
    }

    .trend-value.positive {
      color: var(--success-color);
    }

    .trend-value.negative {
      color: var(--danger-color);
    }

    .trend-value.stable {
      color: var(--warning-color);
    }

    .targets-overview {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .target-item {
      padding: 16px;
      background: var(--surface-hover);
      border-radius: var(--radius-md);
      border: 1px solid var(--border-light);
    }

    .target-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }

    .target-name {
      font-weight: 600;
      color: var(--text-primary);
      font-size: 14px;
    }

    .target-score {
      font-weight: 700;
      color: var(--primary-color);
      font-size: 14px;
    }

    .target-progress {
      height: 8px;
      background: var(--border-light);
      border-radius: 4px;
      overflow: hidden;
      margin-bottom: 8px;
    }

    .progress-bar {
      height: 100%;
      background: linear-gradient(90deg, var(--success-color), var(--primary-color));
      border-radius: 4px;
      transition: width 0.8s ease;
    }

    .target-stats {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 500;
    }

    .success-stores {
      color: var(--success-color);
    }

    .problem-stores {
      color: var(--danger-color);
    }

    @media (max-width: 1024px) {
      .kpi-sidebar {
        width: 360px;
      }
    }

    @media (max-width: 768px) {
      .kpi-sidebar {
        width: 100vw;
      }

      .kpi-content {
        padding: 16px;
      }

      .kpi-cards {
        grid-template-columns: 1fr;
        padding: 5px;
      }

      .kpi-toggle-btn {
        top: 10px;
        right: 10px;
        // padding: 10px 14px;
        font-size: 13px;
      }
    }
  }

  @media (max-width: 1024px) {
    .odx-kpi__sidebar {
      width: 360px;
    }
  }

  @media (max-width: 768px) {
    .odx-kpi__sidebar {
      width: 100vw;
    }

    .odx-kpi__content {
      padding: 16px;
    }

    .odx-kpi__cards {
      grid-template-columns: 1fr;
    }

    .odx-dashboard {
      padding: 10px;
    }

    .odx-table__cell--static {
      min-width: 230px;
    }
  }

  .odx-plans-toggle {
    position: fixed !important;
    top: 70px !important;
    right: 20px !important;
    z-index: 999 !important;
    padding: 12px 16px !important;
    background: var(--odx-warning) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    transition: all 0.3s ease !important;

    &:hover {
      background: #d97706 !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2) !important;
    }
  }

  .odx-plans-overlay {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    background: rgba(0, 0, 0, 0.8) !important;
    z-index: 1000 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    backdrop-filter: blur(4px) !important;
  }

  .odx-plans-container {
    width: 95vw !important;
    height: 95vh !important;
    background: white !important;
    border-radius: 12px !important;
    overflow: auto !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3) !important;
  }
}

* {
  // overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}


.odx-table__row-enter-active,
.odx-table__row-leave-active {
  transition: all 0.4s ease;
}

.odx-table__row-enter-from,
.odx-table__row-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.odx-table__row-move {
  transition: transform 0.4s ease;
}
</style>
