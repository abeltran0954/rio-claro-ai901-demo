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

## Preparación para Azure App Service

La aplicación admite `RIO_CLARO_DB_PATH` para ubicar la base SQLite en almacenamiento persistente. Localmente, si no se define, usa `rioclaro_master.db` junto a `app.py`. En Azure Linux, configura esta variable con una ruta persistente bajo `/home`, por ejemplo `/home/data/rioclaro_master.db`. En el primer inicio copia allí `rioclaro_master.db` del paquete de demostración; en los inicios posteriores conserva la base persistente y no la sobrescribe. **Solo empaqueta la copia sintética aprobada para la demo, nunca una base operativa.**

Configura las variables de Azure OpenAI y Speech en **App Service > Configuration**, nunca en el código, el repositorio ni los registros de despliegue. El inicio de Streamlit para App Service Linux es:

```sh
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8000
```

Antes de habilitar tráfico público, valida el puerto de escucha, WebSockets, persistencia de SQLite, acceso móvil, credenciales de servicios, y las consultas que la aplicación permite a cada perfil.

## Plan de trabajo

1. **Fase 1 — preparación local y protección del repositorio:** asegurar el arranque, separar secretos y archivos operativos, preparar la configuración para almacenamiento persistente y validar la aplicación sin publicar datos.
2. **Fase 2 — publicación y evaluación:** revisar contigo los activos sintéticos que se publicarán, crear el repositorio privado de GitHub, desplegar en Azure usando únicamente el crédito autorizado, verificar la URL desde una sesión externa y completar el Markdown de entrega con capturas y evidencia de los criterios de éxito.

No se deben subir `.env`, secretos, bases de datos, CSV ni audio sin una revisión explícita y una lista permitida de activos sintéticos de demostración.