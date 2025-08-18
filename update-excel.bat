@echo off
setlocal enabledelayedexpansion

REM =====================================================
REM Скрипт обновления Excel функциональности - v2.0 (Windows)
REM =====================================================

set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

echo %BLUE%================================%NC%
echo %BLUE%Обновление Excel функциональности COM модуля%NC%
echo %BLUE%================================%NC%
echo.

echo 🚀 Начинаем процесс обновления...
echo.

REM Проверка что мы в правильной папке
if not exist "__manifest__.py" (
    echo %RED%❌ Скрипт должен запускаться из корневой папки модуля COM%NC%
    echo %RED%Перейдите в папку: cd C:\path\to\odoo\custom_addons\com\%NC%
    pause
    exit /b 1
)

echo %GREEN%✅ Найден файл __manifest__.py - мы в правильной папке%NC%

REM Проверка наличия Node.js и npm
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo %RED%❌ Node.js не установлен!%NC%
    echo Установите Node.js с https://nodejs.org/
    pause
    exit /b 1
)

where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo %RED%❌ npm не установлен!%NC%
    echo Установите npm вместе с Node.js
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i

echo %GREEN%✅ Node.js !NODE_VERSION! и npm !NPM_VERSION! найдены%NC%

REM Переходим в папку static
echo.
echo %BLUE%================================%NC%
echo %BLUE%Установка зависимостей%NC%
echo %BLUE%================================%NC%

if not exist "static" (
    echo %RED%❌ Папка static не найдена!%NC%
    pause
    exit /b 1
)

cd static

REM Проверяем package.json
if not exist "package.json" (
    echo %RED%❌ Файл package.json не найден в папке static!%NC%
    pause
    exit /b 1
)

echo %GREEN%✅ Найден package.json%NC%

REM Проверяем наличие зависимости xlsx
findstr /c:"xlsx" package.json >nul
if %ERRORLEVEL% equ 0 (
    echo %GREEN%✅ Зависимость xlsx найдена в package.json%NC%
) else (
    echo %YELLOW%⚠️  Зависимость xlsx не найдена, добавляем...%NC%
    npm install xlsx@^0.18.5 --save
)

REM Устанавливаем зависимости
echo.
echo 📦 Установка npm зависимостей...
npm install

if %ERRORLEVEL% equ 0 (
    echo %GREEN%✅ Зависимости установлены успешно%NC%
) else (
    echo %RED%❌ Ошибка установки зависимостей%NC%
    pause
    exit /b 1
)

REM Сборка проекта
echo.
echo %BLUE%================================%NC%
echo %BLUE%Сборка Vue.js приложения%NC%
echo %BLUE%================================%NC%

echo 🔨 Запускаем сборку...
npm run build

if %ERRORLEVEL% equ 0 (
    echo %GREEN%✅ Сборка завершена успешно%NC%
) else (
    echo %RED%❌ Ошибка сборки%NC%
    pause
    exit /b 1
)

REM Проверка результата сборки
if exist "dist\js\vue-app.iife.js" if exist "dist\css\vue-app.css" (
    echo %GREEN%✅ Найдены собранные файлы:%NC%
    echo   📄 dist\js\vue-app.iife.js
    echo   🎨 dist\css\vue-app.css
) else (
    echo %YELLOW%⚠️  Некоторые файлы сборки могут отсутствовать%NC%
)

REM Возвращаемся в корень модуля
cd ..

REM Проверка компонента Plans.vue
echo.
echo %BLUE%================================%NC%
echo %BLUE%Проверка файлов%NC%
echo %BLUE%================================%NC%

if exist "static\src\vue\components\Plans.vue" (
    REM Проверяем наличие Excel функций
    findstr /c:"handleFileUpload" static\src\vue\components\Plans.vue >nul
    if %ERRORLEVEL% equ 0 (
        echo %GREEN%✅ Excel функции найдены в Plans.vue%NC%
    ) else (
        echo %YELLOW%⚠️  Excel функции могут отсутствовать в Plans.vue%NC%
    )
    
    findstr /c:"xlsx" static\src\vue\components\Plans.vue >nul
    if %ERRORLEVEL% equ 0 (
        echo %GREEN%✅ Импорт библиотеки xlsx найден%NC%
    ) else (
        echo %YELLOW%⚠️  Импорт xlsx может отсутствовать%NC%
    )
) else (
    echo %RED%❌ Файл Plans.vue не найден!%NC%
)

REM Финальная проверка
echo.
echo %BLUE%================================%NC%
echo %BLUE%Финальная проверка%NC%
echo %BLUE%================================%NC%

echo 📋 Результаты проверки:
echo.

set "all_good=true"

REM Проверяем основные файлы
set "files[1]=static\package.json:package.json"
set "files[2]=static\dist\js\vue-app.iife.js:Собранный JS"
set "files[3]=static\dist\css\vue-app.css:Собранный CSS"
set "files[4]=static\src\vue\components\Plans.vue:Plans компонент"
set "files[5]=__manifest__.py:Манифест модуля"

for /l %%i in (1,1,5) do (
    for /f "tokens=1,2 delims=:" %%a in ("!files[%%i]!") do (
        if exist "%%a" (
            echo %GREEN%✅ %%b%NC%
        ) else (
            echo %RED%❌ %%b - НЕ НАЙДЕН%NC%
            set "all_good=false"
        )
    )
)

echo.

if "!all_good!"=="true" (
    echo %BLUE%================================%NC%
    echo %BLUE%🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!%NC%
    echo %BLUE%================================%NC%
    echo.
    echo 📋 Следующие шаги:
    echo 1. Обновите модуль в Odoo: Apps → Update List → Upgrade 'com'
    echo 2. Откройте 'Настройки планов' в SMK Analytics
    echo 3. Протестируйте кнопки:
    echo    📥 'Шаблон Excel' - должен скачать файл с 17 магазинами
    echo    📤 'Завантажити Excel' - должен загрузить и заменить данные
    echo.
    echo 🔍 Для отладки откройте консоль браузера (F12)
    echo.
    echo %GREEN%✅ Excel импорт готов к использованию!%NC%
) else (
    echo %BLUE%================================%NC%
    echo %BLUE%⚠️ ОБНОВЛЕНИЕ ЗАВЕРШЕНО С ПРЕДУПРЕЖДЕНИЯМИ%NC%
    echo %BLUE%================================%NC%
    echo.
    echo Некоторые файлы отсутствуют. Проверьте логи выше.
    echo Возможно потребуется ручная настройка.
)

echo.
echo 📚 Документация:
echo   📖 EXCEL_IMPORT_GUIDE.md - подробное руководство
echo   ⚡ EXCEL_QUICK_START.md - быстрая инструкция
echo   🔧 EXCEL_FIXES_v2.md - описание исправлений
echo.
echo 🆘 При проблемах:
echo   1. Проверьте консоль браузера (F12)
echo   2. Убедитесь что Odoo модуль обновлен
echo   3. Перезагрузите страницу

echo.
pause
