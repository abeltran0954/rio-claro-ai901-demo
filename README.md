# Río Claro — prototipo AI-901

Aplicación Streamlit para el caso aprobado de Distribuidora Río Claro. El repositorio debe permanecer privado durante la preparación y revisión de los datos de demostración.

## Ejecución local

Requiere Python 3.12 y `uv`.

```powershell
uv sync
uv run streamlit run app.py
```

Configura las variables requeridas en un archivo `.env` local o en el entorno del proceso. No agregues `.env` al repositorio:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT_NAME`

Para habilitar el dictado por voz, configura también `AZURE_SPEECH_KEY` y, si corresponde, `AZURE_SPEECH_REGION`. `DEMO_LOGIN_PIN` es un PIN compartido únicamente para demostración; no es autenticación apta para producción.

## Azure Container Apps

El `Dockerfile` crea una imagen Linux de Python 3.12 y contiene solo el código, el CSV de empleados y la base SQLite aprobada como datos sintéticos. `.dockerignore` excluye `.env`, archivos locales, datos auxiliares y el resto del árbol de trabajo. El flujo de GitHub Actions publica la imagen en el GitHub Container Registry privado del repositorio al actualizar `main`.

Para desplegar:

1. Ejecuta el flujo **Publish Río Claro demo container** en GitHub Actions y espera que finalice correctamente.
2. En Container Apps, configura el registro privado `ghcr.io` con el usuario de GitHub y un token personal de solo lectura de paquetes (`read:packages`). No guardes ese token en el repositorio ni lo compartas por chat.
3. Usa la imagen `ghcr.io/abeltran0954/rio-claro-ai901-demo:latest`, el puerto de destino `8000` y habilita ingress externo HTTPS.
4. Agrega en la configuración de la app `DEMO_LOGIN_PIN=1234` y configura como secretos `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` y `AZURE_OPENAI_DEPLOYMENT_NAME`. `AZURE_SPEECH_KEY` y `AZURE_SPEECH_REGION` son opcionales para dictado. No copies valores desde `.env` al código ni a GitHub.
5. Mantén una sola réplica mientras se use SQLite. Sin un volumen persistente, los cambios a la base son temporales y pueden perderse cuando Azure sustituya la réplica; la base sintética incluida en la imagen sirve como estado inicial.

El acceso demo con PIN compartido no es autenticación para producción. Antes de usar datos reales, se requiere diseñar autenticación individual, controles de acceso, almacenamiento persistente y protección de datos.

## Plan de trabajo

1. **Fase 1 — preparación local y protección del repositorio:** asegurar el arranque, separar secretos y archivos operativos, preparar la configuración para almacenamiento persistente y validar la aplicación.
2. **Fase 2 — publicación y evaluación:** publicar únicamente los activos sintéticos aprobados, desplegar en Azure usando el crédito autorizado, verificar la URL desde una sesión externa y completar la evidencia de los criterios de éxito.

No se deben subir `.env`, secretos, bases de datos, CSV ni audio sin una revisión explícita y una lista permitida de activos sintéticos de demostración.