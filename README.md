# Hotel Financial Insights

PoC de análisis financiero hotelero con IA generativa. Convierte KPIs de un reporting package en insights automáticos, responde preguntas en lenguaje natural y sugiere análisis relevantes.

---

## Stack tecnológico

**Backend**
- Python 3.12 + FastAPI (API REST + SSE streaming)
- LangChain — agente con tool calling
- OpenAI GPT (ver [selección de modelos](LLM.md))
- SQLite — persistencia de KPIs, insights y feedback
- Loguru — logging estructurado con rotación de ficheros
- Langfuse — observabilidad de LLMs

**Frontend**
- Alpine.js v3 — reactividad
- Tailwind CSS — estilos
- Marked.js — renderizado de markdown

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

Diseño stateless: el agente se construye por petición. El frontend propaga los insights activos como contexto en cada mensaje.

---

## Requisitos previos

- Python 3.12+
- Clave de API de OpenAI

---

## Puesta en marcha

```bash
# 1. Clonar y crear entorno virtual
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

---

## Selección de modelos LLM

Ver [LLM.md](LLM.md) para la justificación de modelos y temperaturas por módulo.

## Pruebas

Ver [UAT.md](UAT.md) para los casos de prueba de aceptación.
