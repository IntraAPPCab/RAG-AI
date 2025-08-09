@echo off
:: Establece el título de la ventana de la consola.
title Cargador de Datos RAG - PDFs y Excels

:: Cambia al directorio donde se encuentra el script.
cd /d "%~dp0"

echo.
echo =======================================================
echo      CARGADOR DE DATOS PARA EL ASISTENTE RAG
echo =======================================================
echo.
echo Este script procesará los PDFs y Excels en la carpeta 'source'.
echo Asegúrate de colocar los archivos en la carpeta 'source' antes de continuar.
echo.

:: Verifica si Python está instalado y en el PATH.
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no se encuentra. Por favor, instala Python y asegúrate de que esté en el PATH.
    pause
    exit /b 1
)

:: Verifica si requirements.txt existe.
if not exist "requirements.txt" (
    echo [ERROR] No se encuentra el archivo requirements.txt.
    pause
    exit /b 1
)

:: Verifica si la carpeta source existe.
if not exist "source" (
    echo [ERROR] No se encuentra la carpeta 'source'. Crea la carpeta y coloca los archivos allí.
    pause
    exit /b 1
)

echo [PASO 1] Verificando e instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Falló la instalación de dependencias. Revisa requirements.txt.
    pause
    exit /b 1
)

echo.
echo [PASO 2] Iniciando el proceso de carga de datos...
echo No cierres esta ventana hasta que el proceso finalice.
echo.

:: Ejecuta el script de ingesta de datos.
python -m app.ingest
if %errorlevel% neq 0 (
    echo [ERROR] Falló el proceso de ingesta. Verifica los archivos en 'source' y app/ingest.py.
    pause
    exit /b 1
)

echo.
echo =======================================================
echo      PROCESO DE CARGA FINALIZADO
echo =======================================================
echo.
pause