# Tech Stack

## Backend

| Tecnología | Versión | Rol |
|---|---|---|
| **Python** | 3.12 | Lenguaje principal |
| **FastAPI** | 0.135 | Framework API REST + SSE streaming |
| **Uvicorn** | — | Servidor ASGI |
| **Pydantic / pydantic-settings** | — | Validación de modelos y configuración por entorno |
| **LangChain** | 1.2 | Framework de agente (ReAct loop, tool calling, memory) |
| **langchain-openai** | 1.1 | Integración LangChain ↔ OpenAI |
| **Pandas** | 3.0 | Cálculo y agregación de KPIs sobre datos tabulares |
| **SQLite** | stdlib | Persistencia ligera (KPIs, insights, sugerencias, feedback) |
| **Loguru** | 0.7 | Logging estructurado con rotación de ficheros |
| **sse-starlette** | 3.3 | Server-Sent Events para streaming de respuestas del agente |
| **aiofiles** | 25.1 | I/O asíncrono de ficheros estáticos |
| **python-dotenv** | 1.2 | Carga de variables de entorno desde `.env` |
| **tabulate** | 0.10 | Formateo de tablas en markdown para contexto LLM |

---

## Inteligencia Artificial

| Tecnología | Rol |
|---|---|
| **OpenAI API** | Proveedor de modelos LLM (GPT-5.4 Mini y Nano) |
| **LangChain ReAct Agent** | Orquestación del agente: razonamiento + uso de herramientas |
| **Langfuse** | Observabilidad de LLMs: trazas, latencias, costes, evaluación |

Ver [LLM.md](../LLM.md) para la justificación de modelos y temperaturas por módulo.

---

## Frontend

| Tecnología | Versión | Rol |
|---|---|---|
| **Alpine.js** | 3.14 | Reactividad declarativa (sin build step) |
| **Tailwind CSS** | CDN | Estilos utilitarios |
| **Marked.js** | 13.0 | Renderizado de markdown en respuestas del agente |

Aplicación de página única servida como fichero estático por FastAPI. Sin framework SPA ni proceso de build.

---

## Datos

| Elemento | Detalle |
|---|---|
| **Origen** | Datos sintéticos generados para el PoC |
| **Formato de ingesta** | CSV cargados a SQLite en el primer arranque |
| **Granularidad** | Mensual por hotel y escenario (REAL / BUDGET) |
| **Cobertura temporal** | 2025 – 2026 (parcial) |
| **Escenarios** | REAL (ejecutado) vs BUDGET (presupuesto) |

---

## Infraestructura y operación

| Elemento | Detalle |
|---|---|
| **Despliegue** | Proceso único Uvicorn; apto para contenedor Docker |
| **Configuración** | Variables de entorno vía `.env` + `pydantic-settings` |
| **Logs** | Consola (INFO) + fichero rotativo `logs/` (DEBUG, máx. 10 MB) |
| **Observabilidad LLM** | Langfuse (opcional; el sistema funciona sin él) |
| **Base de datos** | Fichero SQLite local; autocompletado en primer arranque |
