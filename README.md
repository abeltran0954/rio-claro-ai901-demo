# Río Claro IA

Prototipo de demostración construido con Streamlit para explorar asistentes de IA y flujos operativos de Distribuidora Río Claro. No es un sistema listo para producción.

## Enlaces

- **Aplicación de demostración:** [Río Claro IA](https://rio-claro-aca-validation.yellowrock-2b43caa9.centralus.azurecontainerapps.io/)
- **Repositorio:** [abeltran0954/rio-claro-ai901-demo](https://github.com/abeltran0954/rio-claro-ai901-demo) — privado; el propietario debe autorizar el acceso.
- **Guía para evaluación:** [ENTREGABLE_EVALUADOR.md](./ENTREGABLE_EVALUADOR.md)

## Funcionalidad

- Control de acceso por perfil (RBAC): módulos y algunas vistas se delimitan según el rol y la sucursal.
- Asistente con Azure OpenAI para consultar el catálogo y ventas registradas, registrar solicitudes de traslado entre sucursales e incidencias de clientes.
- Dictado por voz con Azure Speech, si está configurado y el navegador tiene permiso para usar el micrófono.
- Flujos de captura y revisión asistidos por IA para ventas, recepción de mercancía y validación de facturas, con confirmación humana antes de registrar.
- Bandeja de solicitudes e incidencias y vistas de datos según los módulos habilitados para el perfil.

La revisión manual de los perfiles y permisos de demostración continúa. Consulta las limitaciones antes de evaluar o compartir la aplicación.

## Adaptación del caso AI-901

La aplicación adapta el escenario a las sucursales configuradas para esta demostración: Culiacán, Guasave, Los Mochis, Mazatlán y Navolato. El caso de referencia menciona Guadalajara, Zapopan, León, Querétaro y Aguascalientes; no se plantea una equivalencia uno a uno entre ambas listas.

## Ejecución local

Requiere Python 3.12 o posterior y [`uv`](https://docs.astral.sh/uv/).

```powershell
uv sync
uv run streamlit run app.py
```

Configura estas variables en un `.env` local o en el entorno del proceso:

| Variable | Requisito | Uso |
|---|---|---|
| `AZURE_OPENAI_ENDPOINT` | Requerida | Endpoint de Azure OpenAI. |
| `AZURE_OPENAI_API_KEY` | Requerida | Clave de Azure OpenAI. |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Requerida | Nombre del despliegue de modelo. |
| `DEMO_LOGIN_PIN` | Requerida para iniciar sesión | PIN compartido de cuatro dígitos para la demostración. El valor se entrega por un canal autorizado, nunca en el repositorio. |
| `AZURE_SPEECH_KEY` | Opcional | Habilita el dictado por voz. |
| `AZURE_SPEECH_REGION` | Opcional | Región de Azure Speech; si se omite, la aplicación usa su región predeterminada. |

No agregues `.env` ni archivos de secretos a Git.

## Publicación y despliegue

El flujo [Publish Río Claro demo container](./.github/workflows/publish-container.yml) construye y publica imágenes en GitHub Container Registry al actualizar `main`. Genera una etiqueta inmutable con el commit (`sha-<commit>`) y la etiqueta `latest`; para crear una revisión en Azure Container Apps, prefiere la etiqueta `sha-<commit>`.

La imagen utiliza `Dockerfile` y necesita la configuración de Azure OpenAI, Azure Speech y `DEMO_LOGIN_PIN` en los secretos o variables de entorno de Container Apps. No guardes sus valores en el código ni en este documento.

## Datos y limitaciones

- El contenedor incluye una base SQLite inicial y un archivo de empleados para la demostración. Revisa y autoriza el contenido de todos los datos antes de compartir el repositorio o la imagen.
- La aplicación no tiene almacenamiento persistente configurado para SQLite en Azure. Los cambios guardados en la base pueden perderse al sustituir la réplica o desplegar otra revisión.
- El prototipo sí aplica RBAC a sus módulos y limita determinadas vistas por sucursal. El PIN compartido de demostración y la selección de empleado no verifican identidad individual; antes de usar datos reales se requiere autenticación individual adecuada al entorno.
- El asistente limita las consultas SQL de “Consultas Mostrador” al catálogo de productos. Las consultas de ventas agregadas siguen un flujo separado.
- La nómina aparece como una posible función ERP futura; el prototipo no implementa un módulo funcional de nómina.
- Los modelos de IA pueden equivocarse al transcribir, extraer o interpretar información. Revisa los resultados antes de registrar operaciones.
- Usa exclusivamente datos ficticios o autorizados para pruebas. No cargues facturas, datos de clientes ni información personal real.
- El repositorio debe permanecer privado mientras contenga datos de operación o activos que no hayan sido revisados para publicación.

No hay una suite de pruebas automatizadas configurada. La comprobación de sintaxis de Python puede ejecutarse sin importar la aplicación ni abrir la base de datos:

```powershell
uv run --no-sync python -m py_compile app.py
```
