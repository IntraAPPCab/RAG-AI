@echo off
:: Establece el título de la ventana.
title Servidor RAG - Asistente para CMMS

:: Cambia al directorio del script.
cd /d "%~dp0"

echo.
echo =======================================================
echo      INICIANDO SERVIDOR DEL ASISTENTE RAG
echo =======================================================
echo.

:: Verifica si Python está instalado.
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

echo [PASO 1] Verificando e instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Falló la instalación de dependencias. Revisa requirements.txt.
    pause
    exit /b 1
)

echo.
echo [PASO 2] Iniciando el servidor del asistente...
echo.
echo El servidor estará disponible en: http://127.0.0.1:8000
echo.
echo Para detener el servidor, cierra esta ventana o presiona CTRL+C.
echo.

:: Ejecuta el servidor FastAPI con Uvicorn.
uvicorn app.main:app --host 0.0.0.0 --port 8000
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo iniciar el servidor. Verifica la configuración en app/main.py.
    pause
    exit /b 1
)