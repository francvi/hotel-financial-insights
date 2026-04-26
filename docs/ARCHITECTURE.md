# Arquitectura del Sistema

## Visión general

El sistema transforma datos financieros hoteleros en insights accionables y conversación inteligente. Está compuesto por cinco módulos funcionales independientes que comparten una base de datos SQLite centralizada y se exponen a través de una API REST.

---

## Diagrama de módulos

```mermaid
flowchart TD
    UI["🖥️ Frontend\nAlpine.js · Tailwind CSS · Marked.js"]

    UI -->|"GET /api/insights"| IR[Insights Router]
    UI -->|"GET /api/suggestions\nPOST /api/suggestions/followup"| SR[Suggestions Router]
    UI -->|"POST /api/chat (SSE)"| AR[Agent Router]
    UI -->|"POST /api/feedback"| FR[Feedback Router]

    subgraph API["FastAPI — app/"]
        AR
        IR
        SR
        FR
    end

    AR --> AS["⚙️ Agent Service\nLangChain ReAct"]
    IR --> IS["💡 Insights Service\nGPT-5.4 Mini · T=0.1"]
    SR --> SS["💬 Suggestions Service\nGPT-5.4 Nano · T=0.7"]

    AS -->|"Tool calls"| KPI

    subgraph KPI["🔧 KPI Tools — kpis/"]
        T1["overall_kpis_annual\nTodos los KPIs por año"]
        T2["kpis_by_hotel_annual\nKPIs por hotel y año"]
        T3["kpis_monthly\nKPIs mensuales por año"]
        T4["departmental_kpis_annual\nDesglose Rooms · FB · Undistrib por año"]
        T5["departmental_kpis_monthly\nDesglose departamental mensual"]
        T6["get_portfolio_context\nPerfil y metadatos del portafolio"]
    end

    AS -->|"Completion\nGPT-5.4 Mini · T=0.1"| LLM[("☁️ OpenAI API")]
    IS --> LLM
    SS --> LLM

    KPI -->|"SQL queries"| DB[("🗄️ SQLite\nhotel_financial_insights.db")]
    IS -->|"Leer / escribir insights"| DB
    SS -->|"Leer / escribir sugerencias"| DB
    FR -->|"Guardar feedback"| DB

    AS -->|"Trazas"| LF["📊 Langfuse\nObservabilidad LLM"]
    IS -->|"Trazas"| LF
    SS -->|"Trazas"| LF
```

---

## Flujos principales

### Arranque del servidor
Al iniciar, el servidor ejecuta `load_insights()`. Si la tabla de insights está vacía, llama al motor de insights para generarlos a partir de los KPIs y los persiste en SQLite. Coste cero en reinicios posteriores.

### Conversación (chat)
1. El frontend envía `message + history + insights` al endpoint `/api/chat`.
2. El Agent Router construye el agente en tiempo de petición, inyectando los insights activos como contexto adicional en el system prompt.
3. El agente ejecuta un bucle ReAct: razona, llama herramientas KPI, observa resultados y genera la respuesta.
4. La respuesta se transmite token a token mediante **Server-Sent Events (SSE)**.

> El agente es **stateless**: se construye por petición a partir del estado que propaga el frontend. No hay estado compartido entre workers.

### Insights
- `GET /api/insights` → lee de SQLite; si está vacío, genera vía LLM.
- `POST /api/insights/refresh` → borra insights y sugerencias, regenera ambos.
- Los insights se propagan desde el frontend al agente en cada mensaje, garantizando coherencia sin estado servidor.

### Sugerencias
- `GET /api/suggestions` → sugerencias iniciales basadas en KPIs (cacheadas en DB).
- `POST /api/suggestions/followup` → genera 3 preguntas de seguimiento contextuales usando los últimos 10 mensajes de la conversación.

### Feedback
`POST /api/feedback` persiste la valoración (👍/👎), comentario opcional, contenido del mensaje evaluado e historial de los últimos 10 mensajes.

---

## Base de datos — `hotel_financial_insights.db`

| Tabla | Contenido |
|---|---|
| `pnl` | Datos financieros mensuales por hotel y escenario (REAL/BUDGET) |
| `hotels` | Metadatos del portafolio (país, categoría, habitaciones) |
| `insights` | Insights generados por LLM (cacheados) |
| `suggestions` | Sugerencias iniciales generadas por LLM (cacheadas) |
| `feedback` | Valoraciones de usuarios por mensaje |

---

## Decisiones de diseño destacadas

| Decisión | Justificación |
|---|---|
| Agente stateless | Seguridad en entornos multi-worker; sin estado compartido entre peticiones |
| Insights propagados desde el frontend | Permite que el agente siempre tenga los insights vigentes sin consultar la DB en cada petición |
| Un único fichero SQLite | Simplicidad operativa; suficiente para el volumen del PoC |
| SSE para streaming | Mejora la percepción de velocidad en respuestas largas del agente |
| Módulo aislado por dominio | Cada módulo gestiona su router, servicio y acceso a DB de forma independiente |
