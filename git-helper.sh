#!/bin/bash

# =====================================================
# Git Helper Script для аддона COM
# =====================================================

set -e  # Выход при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода заголовков
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

# Проверка наличия git
check_git() {
    if ! command -v git &> /dev/null; then
        print_error "Git не установлен!"
        exit 1
    fi
}

# Проверка наличия npm
check_npm() {
    if ! command -v npm &> /dev/null; then
        print_error "npm не установлен!"
        exit 1
    fi
}

# Инициализация репозитория
init_repo() {
    print_header "Инициализация Git репозитория"
    
    if [ -d ".git" ]; then
        print_warning "Git репозиторий уже инициализирован"
        return
    fi
    
    git init
    git add .
    git commit -m "Initial commit: Odoo аддон COM с Vue.js интеграцией"
    print_success "Репозиторий инициализирован"
}

# Установка зависимостей
install_deps() {
    print_header "Установка зависимостей"
    
    cd static/
    npm install
    cd ..
    
    print_success "Зависимости установлены"
}

# Сборка проекта
build_project() {
    print_header "Сборка Vue.js приложения"
    
    cd static/
    npm run build
    cd ..
    
    print_success "Проект собран"
}

# Проверка кода
lint_code() {
    print_header "Проверка кода (ESLint)"
    
    cd static/
    if npm run lint; then
        print_success "Код прошел проверку"
    else
        print_error "Найдены ошибки в коде"
        exit 1
    fi
    cd ..
}

# Подготовка к коммиту
prepare_commit() {
    print_header "Подготовка к коммиту"
    
    # Сборка
    build_project
    
    # Проверка кода
    lint_code
    
    # Показать статус
    git status
    
    print_success "Готово к коммиту"
}

# Быстрый коммит
quick_commit() {
    print_header "Быстрый коммит"
    
    if [ -z "$1" ]; then
        print_error "Необходимо указать сообщение коммита"
        echo "Использование: ./git-helper.sh commit \"сообщение\""
        exit 1
    fi
    
    prepare_commit
    
    git add .
    git commit -m "$1"
    
    print_success "Коммит создан: $1"
}

# Создание релиза
create_release() {
    print_header "Создание релиза"
    
    if [ -z "$1" ]; then
        print_error "Необходимо указать версию релиза"
        echo "Использование: ./git-helper.sh release \"v1.0.0\""
        exit 1
    fi
    
    prepare_commit
    
    git add .
    git commit -m "chore: подготовка к релизу $1"
    git tag -a "$1" -m "Релиз $1"
    
    print_success "Релиз $1 создан"
}

# Обновление зависимостей
update_deps() {
    print_header "Обновление зависимостей"
    
    cd static/
    npm update
    npm audit fix
    cd ..
    
    print_success "Зависимости обновлены"
}

# Показать помощь
show_help() {
    echo -e "${BLUE}Git Helper для аддона COM${NC}"
    echo ""
    echo "Использование:"
    echo "  ./git-helper.sh <команда> [аргументы]"
    echo ""
    echo "Команды:"
    echo "  init                 - Инициализировать git репозиторий"
    echo "  install              - Установить npm зависимости"
    echo "  build                - Собрать Vue.js приложение"
    echo "  lint                 - Проверить код (ESLint)"
    echo "  prepare              - Подготовить к коммиту (build + lint)"
    echo "  commit \"сообщение\"   - Быстрый коммит с проверками"
    echo "  release \"v1.0.0\"     - Создать релиз с тегом"
    echo "  update               - Обновить npm зависимости"
    echo "  help                 - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  ./git-helper.sh init"
    echo "  ./git-helper.sh commit \"feat: добавлена новая функция\""
    echo "  ./git-helper.sh release \"v1.2.0\""
}

# Основная логика
main() {
    check_git
    
    case ${1:-help} in
        "init")
            init_repo
            ;;
        "install")
            check_npm
            install_deps
            ;;
        "build")
            check_npm
            build_project
            ;;
        "lint")
            check_npm
            lint_code
            ;;
        "prepare")
            check_npm
            prepare_commit
            ;;
        "commit")
            check_npm
            quick_commit "$2"
            ;;
        "release")
            check_npm
            create_release "$2"
            ;;
        "update")
            check_npm
            update_deps
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Запуск
main "$@"
