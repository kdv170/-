@echo off
rem Сборка внешней обработки из XML-выгрузки.
rem Запускать на машине с установленной платформой 1С и базой ERP.
rem
rem Пример:
rem   set V8="C:\Program Files\1cv8\8.3.23.1865\bin\1cv8.exe"
rem   set IB=/S "app-server\erp"
rem   set USER=/N"Админ" /P"пароль"
rem   tools\собрать-обработку.cmd

if "%V8%"=="" set V8=1cv8.exe
if "%IB%"=="" (
  echo Задайте переменные V8 и IB. Пример:
  echo   set V8="C:\Program Files\1cv8\8.3.23.1865\bin\1cv8.exe"
  echo   set IB=/F "C:\Bases\ERP"
  echo   set USER=/N"Админ" /P""
  exit /b 1
)

if not exist build mkdir build

%V8% DESIGNER %IB% %USER% /DisableStartupDialogs /LoadExternalDataProcessorOrReportFromFiles "%~dp0..\src\ЗагрузкаУчетаДанныхДляНДФЛИзЗУП.xml" "%~dp0..\build\ЗагрузкаУчетаДанныхДляНДФЛИзЗУП.epf"
if errorlevel 1 (
  echo Сборка не удалась.
  exit /b 1
)
echo Готово: build\ЗагрузкаУчетаДанныхДляНДФЛИзЗУП.epf
