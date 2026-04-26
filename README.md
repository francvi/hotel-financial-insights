# Hotel Financial Insights

PoC de análisis financiero hotelero con IA generativa. Convierte KPIs de un reporting package en insights automáticos, responde preguntas en lenguaje natural y sugiere análisis relevantes.

---

## Documentación

| Documento | Descripción |
|---|---|
| [Arquitectura](docs/ARCHITECTURE.md) | Diagrama de módulos, flujos de datos y decisiones de diseño |
| [Tech Stack](docs/TECH_STACK.md) | Frameworks, proveedores y versiones por capa |
| [Selección de modelos LLM](docs/LLM_SELECTION.md) | Justificación de modelos y temperaturas por módulo |
| [Casos de prueba UAT](docs/UAT.md) | Framework de pruebas de aceptación |
| [Business Case](docs/BUSINESS_CASE.md) | Motivación, alcance y valor del PoC |

---

## Stack tecnológico

**Backend** — Python 3.12 · FastAPI · LangChain · OpenAI · SQLite · Loguru · Langfuse

**Frontend** — Alpine.js v3 · Tailwind CSS · Marked.js

Ver [Tech Stack completo](docs/TECH_STACK.md).

---

## Arquitectura

```
app/
├── agent/        # Agente conversacional (LangChain + OpenAI)
├── insights/     # Generación y persistencia de insights
├── suggestions/  # Sugerencias de seguimiento contextuales
├── feedback/     # Thumbs up/down por respuesta
├── kpis/         # Cálculo de KPIs desde SQLite
├── integration/  # OpenAI, Langfuse, carga de DB
├── config/       # Settings (env vars)
└── static/       # Frontend (index.html)
```

Diseño stateless: el agente se construye por petición. El frontend propaga los insights activos como contexto en cada mensaje. Ver [arquitectura detallada](docs/ARCHITECTURE.md).

---

## Puesta en marcha

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con OPENAI_API_KEY (y opcionalmente las claves de Langfuse)

# 4. Arrancar el servidor
uvicorn app.main:app --reload
```

Abrir [http://localhost:8000](http://localhost:8000) en el navegador.

### Variables de entorno

| Variable | Obligatoria | Descripción |
|---|---|---|
| `OPENAI_API_KEY` | Sí | Clave de API de OpenAI |
| `DB_NAME` | No | Nombre del fichero SQLite (default: `hotel_financial_insights.db`) |
| `LANGFUSE_SECRET_KEY` | No | Observabilidad con Langfuse |
| `LANGFUSE_PUBLIC_KEY` | No | Observabilidad con Langfuse |
| `LANGFUSE_HOST` | No | Host de Langfuse (default: cloud) |
