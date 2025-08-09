# README: Asistente RAG 

## Introducción
Este proyecto es un asistente RAG (Retrieval Augmented Generation) basado en IA para consultar información de archivos PDF, Excels y bases de datos PostgreSQL (e.g., Atlas CMMS). Prioriza la **fidelidad** a los datos originales, citando verbatim y fuentes/páginas, y soporta grandes volúmenes (>3000 páginas). Usa LangChain, FastAPI, Ollama (local) o Gemini (cloud), con aceleración GPU (RTX 3090).

El asistente funciona en modo web (`chat.html`) y soporta consultas generales/completas. Para una PC limpia (sin nada instalado), sigue estas instrucciones paso a paso. Asumo Windows (basado en tus logs), pero adapta para otros OS.

## Requisitos Previos
- **Hardware**: PC con GPU NVIDIA RTX 3090 (o similar) para aceleración. RAM >16GB recomendada para >3000 páginas.
- **Software Básico**:
  - Windows 10/11 (o Linux/Mac con ajustes).
  - Acceso a internet para descargar dependencias y modelos.
  - Cuenta Google para Gemini API (opcional, pero necesario para `llm_choice="gemini"`).
  - Espacio en disco ~50GB para modelos IA y Chroma DB.
- **Herramientas Externas**:
  - Tesseract OCR (para PDFs con imágenes/tablas).
  - Poppler (para procesamiento de PDFs).
  - CUDA Toolkit 12.1 para GPU (NVIDIA).

## Instalación

### 1. Instalación de Python 3.11
- Descarga e instala Python 3.11 desde [python.org](https://www.python.org/downloads/release/python-31110/).
  - Marca "Agregar Python al PATH" durante la instalación.
- Verifica:
  ```bash
  python --version
  ```
  Debería mostrar `Python 3.11.x`.

### 2. Instalación de CUDA y cuDNN para GPU (RTX 3090)
- Descarga CUDA Toolkit 12.1 desde [NVIDIA CUDA](https://developer.nvidia.com/cuda-12-1-0-download-archive) (elige Windows, x86_64).
- Instala y reinicia la PC.
- Descarga cuDNN v8.9 para CUDA 12.x desde [NVIDIA cuDNN](https://developer.nvidia.com/cudnn) (requiere cuenta NVIDIA gratuita).
  - Copia los archivos de cuDNN a la carpeta de CUDA (e.g., `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\bin`).
- Verifica:
  ```bash
  nvcc --version
  ```
  Debería mostrar CUDA 12.1.

### 3. Instalación de Tesseract y Poppler
- **Tesseract**: Descarga desde [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki). Instala en `C:\Program Files\Tesseract-OCR`.
  - Agrega al PATH: Edita variables de entorno (Sistema > Avanzado > Variables de entorno > Path > Agregar `C:\Program Files\Tesseract-OCR`).
  - Descarga `spa.traineddata` para español desde [Tessdata](https://github.com/tesseract-ocr/tessdata) y copia a `C:\Program Files\Tesseract-OCR\tessdata`.
- **Poppler**: Descarga desde [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows). Extrae a `C:\poppler-24.02.0`.
  - Agrega `bin/` al PATH: `C:\poppler-24.02.0\bin`.
- Verifica:
  ```bash
  tesseract --version
  pdftoppm --version
  ```

### 4. Crear Entorno Virtual y Instalar Dependencias
- En la carpeta del proyecto:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
- Instala PyTorch con CUDA:
  ```bash
  pip install torch==2.4.1+cu121 torchvision==0.19.1+cu121 torchaudio==2.4.1+cu121 --index-url https://download.pytorch.org/whl/cu121
  ```
- Instala las dependencias:
  ```bash
  pip install -r requirements.txt
  ```
- Verifica GPU:
  ```bash
  python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
  ```
  Debería mostrar `True NVIDIA GeForce RTX 3090`.

### 5. Instalación de Ollama y Modelos
- Descarga Ollama desde [ollama.ai](https://ollama.ai/) e instala.
- Ejecuta:
  ```bash
  ollama run gemma3:12b
  ```
  (Descarga el modelo ~7GB; toma tiempo).
- Opcional: `ollama run llama3` para backup.

### 6. Configuración de Keys y Archivos
- En `app/settings.py`:
  - Actualiza `GOOGLE_API_KEY` con tu key de Gemini (consigue en [Google AI Studio](https://aistudio.google.com/)).
  - Configura `DATABASES` con tus creds de PostgreSQL.
- Coloca archivos en `source/` (PDFs, Excels, TXT).
- Crea `load_data.bat` y `run.bat` en la raíz con el contenido de mensajes previos (incluyen activación de venv).

### 7. Ejecución
1. **Ingestar Datos**:
   ```bash
   load_data.bat
   ```
   (Procesará archivos en `source/` y crea `chroma_db/`).

2. **Iniciar Servidor**:
   ```bash
   run.bat
   ```
   - Abre `http://127.0.0.1:8000` en el navegador.
   - Selecciona fuente, LLM (ollama para Gemma), pregunta (e.g., "cuales son las tablas de cuentas corrientes?") y envía.

3. **Parar**: Ctrl+C en la consola o cierra la ventana.

### Depuración Común
- **Error en ingesta**: Verifica Tesseract/Poppler en PATH, archivos en `source/`.
- **Error en consultas**: Asegura Ollama corriendo, API key válida, colecciones en `metadata.json`.
- **GPU no detectada**: Verifica CUDA con `nvcc --version`.
- **Alucinaciones en Gemma**: Usa Gemini para consultas complejas o ajusta temperature=0.
- **Lento**: Aumenta batch_size en embeddings si VRAM lo permite.
