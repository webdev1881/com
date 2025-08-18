#!/bin/bash

# =====================================================
# Скрипт обновления Excel функциональности - v2.0
# =====================================================

set -e  # Выход при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header "Обновление Excel функциональности COM модуля"

echo "🚀 Начинаем процесс обновления..."
echo ""

# Проверка что мы в правильной папке
if [ ! -f "__manifest__.py" ]; then
    print_error "Скрипт должен запускаться из корневой папки модуля COM"
    print_error "Перейдите в папку: cd /path/to/odoo/custom_addons/com/"
    exit 1
fi

print_success "Найден файл __manifest__.py - мы в правильной папке"

# Проверка наличия Node.js и npm
if ! command -v node &> /dev/null; then
    print_error "Node.js не установлен!"
    echo "Установите Node.js с https://nodejs.org/"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    print_error "npm не установлен!"
    echo "Установите npm вместе с Node.js"
    exit 1
fi

print_success "Node.js $(node --version) и npm $(npm --version) найдены"

# Переходим в папку static
print_header "Установка зависимостей"

if [ ! -d "static" ]; then
    print_error "Папка static не найдена!"
    exit 1
fi

cd static/

# Проверяем package.json
if [ ! -f "package.json" ]; then
    print_error "Файл package.json не найден в папке static!"
    exit 1
fi

print_success "Найден package.json"

# Проверяем наличие зависимости xlsx
if grep -q '"xlsx"' package.json; then
    print_success "Зависимость xlsx найдена в package.json"
else
    print_warning "Зависимость xlsx не найдена, добавляем..."
    npm install xlsx@^0.18.5 --save
fi

# Устанавливаем зависимости
echo ""
echo "📦 Установка npm зависимостей..."
npm install

if [ $? -eq 0 ]; then
    print_success "Зависимости установлены успешно"
else
    print_error "Ошибка установки зависимостей"
    exit 1
fi

# Сборка проекта
echo ""
print_header "Сборка Vue.js приложения"

echo "🔨 Запускаем сборку..."
npm run build

if [ $? -eq 0 ]; then
    print_success "Сборка завершена успешно"
else
    print_error "Ошибка сборки"
    exit 1
fi

# Проверка результата сборки
if [ -f "dist/js/vue-app.iife.js" ] && [ -f "dist/css/vue-app.css" ]; then
    print_success "Найдены собранные файлы:"
    echo "  📄 dist/js/vue-app.iife.js"
    echo "  🎨 dist/css/vue-app.css"
else
    print_warning "Некоторые файлы сборки могут отсутствовать"
fi

# Возвращаемся в корень модуля
cd ..

# Проверка компонента Plans.vue
print_header "Проверка файлов"

if [ -f "static/src/vue/components/Plans.vue" ]; then
    # Проверяем наличие Excel функций
    if grep -q "handleFileUpload" static/src/vue/components/Plans.vue; then
        print_success "Excel функции найдены в Plans.vue"
    else
        print_warning "Excel функции могут отсутствовать в Plans.vue"
    fi
    
    if grep -q "xlsx" static/src/vue/components/Plans.vue; then
        print_success "Импорт библиотеки xlsx найден"
    else
        print_warning "Импорт xlsx может отсутствовать"
    fi
else
    print_error "Файл Plans.vue не найден!"
fi

# Финальная проверка
print_header "Финальная проверка"

echo "📋 Результаты проверки:"
echo ""

# Проверяем основные файлы
files_to_check=(
    "static/package.json:package.json"
    "static/dist/js/vue-app.iife.js:Собранный JS"
    "static/dist/css/vue-app.css:Собранный CSS"
    "static/src/vue/components/Plans.vue:Plans компонент"
    "__manifest__.py:Манифест модуля"
)

all_good=true

for file_check in "${files_to_check[@]}"; do
    IFS=':' read -r filepath description <<< "$file_check"
    if [ -f "$filepath" ]; then
        print_success "$description"
    else
        print_error "$description - НЕ НАЙДЕН"
        all_good=false
    fi
done

echo ""

if [ "$all_good" = true ]; then
    print_header "🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!"
    echo ""
    echo "📋 Следующие шаги:"
    echo "1. Обновите модуль в Odoo: Apps → Update List → Upgrade 'com'"
    echo "2. Откройте 'Настройки планов' в SMK Analytics"
    echo "3. Протестируйте кнопки:"
    echo "   📥 'Шаблон Excel' - должен скачать файл с 17 магазинами"
    echo "   📤 'Завантажити Excel' - должен загрузить и заменить данные"
    echo ""
    echo "🔍 Для отладки откройте консоль браузера (F12)"
    echo ""
    print_success "Excel импорт готов к использованию!"
else
    print_header "⚠️ ОБНОВЛЕНИЕ ЗАВЕРШЕНО С ПРЕДУПРЕЖДЕНИЯМИ"
    echo ""
    echo "Некоторые файлы отсутствуют. Проверьте логи выше."
    echo "Возможно потребуется ручная настройка."
fi

echo ""
echo "📚 Документация:"
echo "  📖 EXCEL_IMPORT_GUIDE.md - подробное руководство"
echo "  ⚡ EXCEL_QUICK_START.md - быстрая инструкция"
echo "  🔧 EXCEL_FIXES_v2.md - описание исправлений"
echo ""
echo "🆘 При проблемах:"
echo "  1. Проверьте консоль браузера (F12)"
echo "  2. Убедитесь что Odoo модуль обновлен"
echo "  3. Перезагрузите страницу"
