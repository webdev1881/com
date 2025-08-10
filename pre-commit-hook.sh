#!/bin/sh

# =====================================================
# Pre-commit hook для аддона COM
# =====================================================
# Этот файл нужно скопировать в .git/hooks/pre-commit
# и сделать исполняемым: chmod +x .git/hooks/pre-commit

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Запуск pre-commit проверок...${NC}"

# Проверка наличия npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm не найден! Пропускаем проверки Vue.js${NC}"
    exit 0
fi

# Переходим в папку static для npm команд
cd static/

# 1. Проверка линтинга
echo -e "${YELLOW}📋 Проверка ESLint...${NC}"
if ! npm run lint; then
    echo -e "${RED}❌ ESLint проверка не пройдена!${NC}"
    echo -e "${YELLOW}💡 Исправьте ошибки линтинга перед коммитом${NC}"
    exit 1
fi
echo -e "${GREEN}✅ ESLint проверка пройдена${NC}"

# 2. Сборка проекта
echo -e "${YELLOW}🔨 Сборка Vue.js приложения...${NC}"
if ! npm run build; then
    echo -e "${RED}❌ Ошибка сборки!${NC}"
    echo -e "${YELLOW}💡 Исправьте ошибки сборки перед коммитом${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Сборка успешна${NC}"

# Возвращаемся в корень
cd ..

# 3. Проверка Python файлов (базовая)
echo -e "${YELLOW}🐍 Проверка Python файлов...${NC}"
# Проверяем наличие __pycache__ в коммите
if git diff --cached --name-only | grep -q "__pycache__"; then
    echo -e "${RED}❌ Найдены __pycache__ файлы в коммите!${NC}"
    echo -e "${YELLOW}💡 Используйте .gitignore для исключения __pycache__${NC}"
    exit 1
fi

# Проверяем синтаксис Python файлов
for file in $(git diff --cached --name-only --diff-filter=ACM | grep "\.py$"); do
    if [ -f "$file" ]; then
        if ! python -m py_compile "$file"; then
            echo -e "${RED}❌ Синтаксическая ошибка в $file${NC}"
            exit 1
        fi
    fi
done
echo -e "${GREEN}✅ Python файлы корректны${NC}"

# 4. Проверка размера коммита
echo -e "${YELLOW}📏 Проверка размера изменений...${NC}"
CHANGED_FILES=$(git diff --cached --name-only | wc -l)
if [ "$CHANGED_FILES" -gt 50 ]; then
    echo -e "${YELLOW}⚠️  Много файлов в коммите ($CHANGED_FILES)${NC}"
    echo -e "${YELLOW}💡 Рассмотрите возможность разделения на несколько коммитов${NC}"
fi

# 5. Проверка сообщения коммита (если есть)
if [ -f ".git/COMMIT_EDITMSG" ]; then
    COMMIT_MSG=$(head -n 1 .git/COMMIT_EDITMSG)
    if [ ${#COMMIT_MSG} -lt 10 ]; then
        echo -e "${YELLOW}⚠️  Короткое сообщение коммита${NC}"
        echo -e "${YELLOW}💡 Используйте описательные сообщения коммитов${NC}"
    fi
fi

# 6. Добавляем собранные файлы в коммит
echo -e "${YELLOW}📦 Добавление собранных файлов...${NC}"
git add static/dist/

echo -e "${GREEN}✅ Все проверки пройдены! Коммит разрешен.${NC}"
exit 0
