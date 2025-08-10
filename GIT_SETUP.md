# Git Setup для аддона COM

## 🚀 Быстрая инициализация репозитория

```bash
# В папке com/
git init
git add .
git commit -m "Initial commit: Odoo аддон с Vue.js интеграцией"

# Добавление remote origin (замените на ваш URL)
git remote add origin https://github.com/your-username/your-repo.git
git branch -M main
git push -u origin main
```

## 📦 Что включено в версионирование

### ✅ Включено:
- Исходный код Python (контроллеры, модели)
- Vue.js компоненты и утилиты  
- Конфигурация Odoo (manifests, views, security)
- Статические файлы (CSS, данные JSON)
- **Собранные файлы** (`static/dist/`) - для продакшена
- Конфигурация сборки (vite.config.js, package.json)

### ❌ Исключено:
- `node_modules/` - восстанавливается через `npm install`
- `__pycache__/` - Python кэш файлы
- `.vscode/`, `.idea/` - настройки IDE
- Логи и временные файлы
- OS-специфичные файлы (Thumbs.db, .DS_Store)

## 🔄 Workflow для разработчиков

### Первоначальная настройка:
```bash
git clone <repository-url>
cd com/static/
npm install
npm run build
```

### Процесс разработки:
```bash
# Запуск hot reload для Vue.js
cd static/
npm run build-watch

# В другом терминале - перезагрузка Odoo
# (после изменений Python кода)
```

### Перед коммитом:
```bash
# Сборка для продакшена
cd static/
npm run build

# Проверка линтинга
npm run lint

# Коммит изменений
git add .
git commit -m "feat: описание изменений"
git push
```

## 🏷️ Соглашения о коммитах

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - новая функциональность
- `fix:` - исправление бага
- `docs:` - изменения в документации
- `style:` - форматирование кода
- `refactor:` - рефакторинг без изменения функциональности
- `perf:` - улучшения производительности
- `test:` - добавление/изменение тестов
- `chore:` - обновление зависимостей, конфигурации

## 📋 Checklist перед релизом

- [ ] Код прошел линтинг (`npm run lint`)
- [ ] Vue приложение собрано (`npm run build`)
- [ ] Проверена работа в Odoo
- [ ] Обновлена документация
- [ ] Версия обновлена в `__manifest__.py`
- [ ] Созданы release notes

## 🔒 Безопасность

⚠️ **Никогда не коммитьте:**
- Пароли и API ключи
- Конфиденциальные данные компании
- Локальные конфигурационные файлы с секретами

## 🌿 Ветвления

Рекомендуемая схема:
- `main` - стабильная версия для продакшена
- `develop` - основная ветка разработки
- `feature/название` - разработка новой функциональности
- `hotfix/название` - критические исправления для продакшена

---

💡 **Совет:** Используйте `git status` и `git diff` перед каждым коммитом!
