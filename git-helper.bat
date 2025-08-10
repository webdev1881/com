@echo off
setlocal enabledelayedexpansion

REM =====================================================
REM Git Helper Script для аддона COM (Windows)
REM =====================================================

set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="init" goto init_repo
if "%1"=="install" goto install_deps
if "%1"=="build" goto build_project
if "%1"=="lint" goto lint_code
if "%1"=="prepare" goto prepare_commit
if "%1"=="commit" goto quick_commit
if "%1"=="release" goto create_release
if "%1"=="update" goto update_deps
goto help

:init_repo
echo %BLUE%================================%NC%
echo %BLUE%Инициализация Git репозитория%NC%
echo %BLUE%================================%NC%

if exist ".git" (
    echo %YELLOW%⚠️  Git репозиторий уже инициализирован%NC%
    goto :eof
)

git init
git add .
git commit -m "Initial commit: Odoo аддон COM с Vue.js интеграцией"
echo %GREEN%✅ Репозиторий инициализирован%NC%
goto :eof

:install_deps
echo %BLUE%================================%NC%
echo %BLUE%Установка зависимостей%NC%
echo %BLUE%================================%NC%

where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo %RED%❌ npm не установлен!%NC%
    exit /b 1
)

cd static
npm install
cd ..
echo %GREEN%✅ Зависимости установлены%NC%
goto :eof

:build_project
echo %BLUE%================================%NC%
echo %BLUE%Сборка Vue.js приложения%NC%
echo %BLUE%================================%NC%

where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo %RED%❌ npm не установлен!%NC%
    exit /b 1
)

cd static
npm run build
cd ..
echo %GREEN%✅ Проект собран%NC%
goto :eof

:lint_code
echo %BLUE%================================%NC%
echo %BLUE%Проверка кода (ESLint)%NC%
echo %BLUE%================================%NC%

cd static
npm run lint
if %ERRORLEVEL% neq 0 (
    echo %RED%❌ Найдены ошибки в коде%NC%
    cd ..
    exit /b 1
)
cd ..
echo %GREEN%✅ Код прошел проверку%NC%
goto :eof

:prepare_commit
echo %BLUE%================================%NC%
echo %BLUE%Подготовка к коммиту%NC%
echo %BLUE%================================%NC%

call :build_project
call :lint_code
git status
echo %GREEN%✅ Готово к коммиту%NC%
goto :eof

:quick_commit
if "%2"=="" (
    echo %RED%❌ Необходимо указать сообщение коммита%NC%
    echo Использование: git-helper.bat commit "сообщение"
    exit /b 1
)

echo %BLUE%================================%NC%
echo %BLUE%Быстрый коммит%NC%
echo %BLUE%================================%NC%

call :prepare_commit
git add .
git commit -m "%~2"
echo %GREEN%✅ Коммит создан: %~2%NC%
goto :eof

:create_release
if "%2"=="" (
    echo %RED%❌ Необходимо указать версию релиза%NC%
    echo Использование: git-helper.bat release "v1.0.0"
    exit /b 1
)

echo %BLUE%================================%NC%
echo %BLUE%Создание релиза%NC%
echo %BLUE%================================%NC%

call :prepare_commit
git add .
git commit -m "chore: подготовка к релизу %~2"
git tag -a "%~2" -m "Релиз %~2"
echo %GREEN%✅ Релиз %~2 создан%NC%
goto :eof

:update_deps
echo %BLUE%================================%NC%
echo %BLUE%Обновление зависимостей%NC%
echo %BLUE%================================%NC%

cd static
npm update
npm audit fix
cd ..
echo %GREEN%✅ Зависимости обновлены%NC%
goto :eof

:help
echo %BLUE%Git Helper для аддона COM%NC%
echo.
echo Использование:
echo   git-helper.bat ^<команда^> [аргументы]
echo.
echo Команды:
echo   init                 - Инициализировать git репозиторий
echo   install              - Установить npm зависимости
echo   build                - Собрать Vue.js приложение
echo   lint                 - Проверить код (ESLint)
echo   prepare              - Подготовить к коммиту (build + lint)
echo   commit "сообщение"   - Быстрый коммит с проверками
echo   release "v1.0.0"     - Создать релиз с тегом
echo   update               - Обновить npm зависимости
echo   help                 - Показать эту справку
echo.
echo Примеры:
echo   git-helper.bat init
echo   git-helper.bat commit "feat: добавлена новая функция"
echo   git-helper.bat release "v1.2.0"
echo.
goto :eof
