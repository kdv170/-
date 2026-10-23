@echo off
rem Сборка внешней обработки ЗагрузкаДанныхНДФЛИзЗУП.epf из XML-исходников.
rem
rem Сборка выполняется Конфигуратором базы 1С:ERP (или ее копии): реквизит "Организация"
rem формы имеет тип СправочникСсылка.Организации, который должен существовать в конфигурации.
rem
rem Параметры (переменные окружения):
rem   V8_EXE   - путь к 1cv8.exe, например "C:\Program Files\1cv8\8.3.24.1467\bin\1cv8.exe"
rem   IB_CONN  - строка подключения к базе ERP для Конфигуратора:
rem              /F"D:\Bases\ERP"   или   /S"srv-1c\erp"
rem   IB_USER  - пользователь Конфигуратора (необязательно)
rem   IB_PWD   - пароль (необязательно)

chcp 65001 >nul
setlocal

if "%V8_EXE%"=="" (
    echo Не задана переменная V8_EXE - путь к 1cv8.exe
    exit /b 1
)
if "%IB_CONN%"=="" (
    echo Не задана переменная IB_CONN - строка подключения к базе ERP, например /F"D:\Bases\ERP"
    exit /b 1
)

set "ROOT=%~dp0"
set "OUT=%ROOT%build"
if not exist "%OUT%" mkdir "%OUT%"

set "AUTH="
if not "%IB_USER%"=="" set AUTH=/N"%IB_USER%" /P"%IB_PWD%"

"%V8_EXE%" DESIGNER %IB_CONN% %AUTH% /DisableStartupDialogs ^
    /LoadExternalDataProcessorOrReportFromFiles "%ROOT%src\ЗагрузкаДанныхНДФЛИзЗУП.xml" "%OUT%\ЗагрузкаДанныхНДФЛИзЗУП.epf" ^
    /Out "%OUT%\build.log"

if errorlevel 1 (
    echo Ошибка сборки, см. %OUT%\build.log
    type "%OUT%\build.log"
    exit /b 1
)

echo Готово: %OUT%\ЗагрузкаДанныхНДФЛИзЗУП.epf
