# 🚀 Установка Git Environment для аддона COM

## 📋 Что было добавлено

1. **`.gitignore`** - исключения для git
2. **`GIT_SETUP.md`** - подробная документация по работе с git
3. **`git-helper.sh`** - bash скрипт для автоматизации (Linux/Mac)
4. **`git-helper.bat`** - batch скрипт для автоматизации (Windows)
5. **`pre-commit-hook.sh`** - автоматические проверки перед коммитом
6. **`GLOBAL_GITIGNORE_TEMPLATE.txt`** - шаблон для корневого .gitignore

## ⚡ Быстрая установка

### Шаг 1: Инициализация репозитория

**Linux/Mac:**
```bash
chmod +x git-helper.sh
./git-helper.sh init
```

**Windows:**
```cmd
git-helper.bat init
```

### Шаг 2: Установка зависимостей

**Linux/Mac:**
```bash
./git-helper.sh install
```

**Windows:**
```cmd
git-helper.bat install
```

### Шаг 3: Установка pre-commit hook (опционально)

```bash
# Копируем hook в git папку
cp pre-commit-hook.sh .git/hooks/pre-commit

# Делаем исполняемым (Linux/Mac)
chmod +x .git/hooks/pre-commit
```

### Шаг 4: Первая сборка

**Linux/Mac:**
```bash
./git-helper.sh build
```

**Windows:**
```cmd
git-helper.bat build
```

## 🔧 Ежедневное использование

### Быстрый коммит:
```bash
# Linux/Mac
./git-helper.sh commit "feat: добавлена новая функция"

# Windows
git-helper.bat commit "feat: добавлена новая функция"
```

### Создание релиза:
```bash
# Linux/Mac
./git-helper.sh release "v1.0.0"

# Windows
git-helper.bat release "v1.0.0"
```

### Подготовка к коммиту:
```bash
# Linux/Mac
./git-helper.sh prepare

# Windows
git-helper.bat prepare
```

## 🌐 Настройка remote repository

```bash
# GitHub
git remote add origin https://github.com/your-username/odoo-com-addon.git

# GitLab
git remote add origin https://gitlab.com/your-username/odoo-com-addon.git

# Bitbucket
git remote add origin https://your-username@bitbucket.org/your-username/odoo-com-addon.git

# Первый push
git branch -M main
git push -u origin main
```

## 📁 Рекомендуемая структура для команды

```
project-root/
├── .git/
├── .gitignore                    # Корневой gitignore
├── README.md                     # Описание всего проекта
├── custom_addons/
│   ├── com/                      # Ваш аддон
│   │   ├── .gitignore           # ✅ Добавлен
│   │   ├── git-helper.sh        # ✅ Добавлен
│   │   ├── git-helper.bat       # ✅ Добавлен
│   │   ├── pre-commit-hook.sh   # ✅ Добавлен
│   │   ├── GIT_SETUP.md         # ✅ Добавлен
│   │   └── ... (остальные файлы)
│   └── other_addon/
└── requirements.txt              # Python зависимости
```

## 🛡️ Безопасность и Best Practices

### ❌ Никогда не коммитьте:
- Пароли и API ключи
- `node_modules/`
- `__pycache__/`
- Локальные конфигурации с секретами
- Временные и log файлы

### ✅ Всегда коммитьте:
- Исходный код
- Конфигурационные файлы проекта
- Документацию
- Собранные файлы (`static/dist/`) для продакшена

## 🔄 Workflow для команды

### 1. Разработчик клонирует проект:
```bash
git clone <repository-url>
cd odoo-com-addon
./git-helper.sh install  # или .bat для Windows
```

### 2. Создает ветку для новой функции:
```bash
git checkout -b feature/new-dashboard-widget
```

### 3. Разрабатывает с hot reload:
```bash
cd static/
npm run build-watch
```

### 4. Коммитит изменения:
```bash
./git-helper.sh commit "feat: добавлен новый виджет дашборда"
```

### 5. Создает Pull Request:
```bash
git push origin feature/new-dashboard-widget
# Затем создать PR в веб-интерфейсе
```

## 🚨 Troubleshooting

### Проблема: "permission denied: git-helper.sh"
**Решение:**
```bash
chmod +x git-helper.sh
```

### Проблема: "npm not found"
**Решение:** Установите Node.js с [nodejs.org](https://nodejs.org/)

### Проблема: "pre-commit hook не работает"
**Решение:**
```bash
chmod +x .git/hooks/pre-commit
```

### Проблема: Конфликты в dist/ файлах
**Решение:** 
1. Добавьте `static/dist/` в `.gitignore`
2. Собирайте только перед релизом
3. Или используйте CI/CD для автоматической сборки

---

## 🎉 Готово!

Теперь ваш аддон готов к профессиональной разработке в команде с автоматизированными проверками и удобными инструментами!

### Следующие шаги:
1. ✅ Добавьте remote repository
2. ✅ Настройте CI/CD (опционально)
3. ✅ Добавьте команду в Slack/Teams для уведомлений о коммитах
4. ✅ Настройте code review процесс
