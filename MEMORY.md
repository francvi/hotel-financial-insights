# Memoria del Proyecto Capstone

---

## 3. Desarrollo

### 3.1 Visión general del sistema

El proyecto consiste en un sistema de análisis financiero hotelero potenciado por inteligencia artificial. El objetivo es transformar datos financieros brutos de un grupo hotelero —organizados como KPIs reales frente a presupuesto— en insights automáticos, respuestas conversacionales y sugerencias de análisis, todo accesible a través de una interfaz web.

El sistema está compuesto por cinco módulos funcionales independientes que comparten una base de datos SQLite centralizada y se exponen a través de una API REST construida con FastAPI.

```
Frontend (Alpine.js)
       │
       ├── GET  /api/insights       → Motor de Insights
       ├── GET  /api/suggestions    → Motor de Sugerencias
       ├── POST /api/chat (SSE)     → Agente Conversacional
       └── POST /api/feedback       → Módulo de Feedback
                                           │
                               SQLite: hotel_financial_insights.db
                                           │
                                      OpenAI API
                                      Langfuse
```

### 3.2 Arquitectura y decisiones de diseño

#### Diseño stateless

Una de las decisiones arquitectónicas más relevantes es el diseño completamente stateless de la API. El agente no mantiene estado entre peticiones; se construye en tiempo de ejecución por cada solicitud recibida. Los insights activos —generados previamente y almacenados en base de datos— son propagados desde el frontend al agente como contexto adicional en cada mensaje. Esta decisión garantiza la correcta operación en entornos multi-worker y elimina la posibilidad de contaminación de estado entre conversaciones simultáneas.

#### Modularización por dominio

Cada módulo funcional (`agent/`, `insights/`, `suggestions/`, `feedback/`) es autónomo: gestiona su propio router FastAPI, su lógica de servicio y su acceso a base de datos. El archivo `main.py` queda reducido a la composición de routers y el arranque del servidor. Esta estructura facilita el mantenimiento y la extensibilidad independiente de cada componente.

#### Base de datos unificada

Todos los módulos comparten un único fichero SQLite (`hotel_financial_insights.db`). El nombre es configurable vía variables de entorno. La carga inicial de datos desde CSV se realiza automáticamente en el primer arranque mediante la función `ensure_loaded()`, que comprueba la existencia de la tabla `pnl` antes de proceder.

### 3.3 Motor de cálculo de KPIs

El motor de KPIs (`app/kpis/kpi_calculator.py`) es el núcleo analítico del sistema. Carga en memoria los datos financieros desde SQLite al arrancar y expone los KPIs como herramientas disponibles para el agente.

#### Métricas implementadas

Se implementaron más de 30 KPIs organizados en cuatro categorías:

| Categoría | KPIs representativos |
|---|---|
| Opex & Labor | CPOR, CPH, LBC, LPC_TOTAL, UNDISTRIB_OPEX_Pct |
| Food & Beverage | Food_Cost_Pct, F&B_GOP_MARGIN, F&B_REVPAR, BANQUETS_CONTRIBUTION |
| Revenue Management | OCC, ADR, REVPAR, TRevPAR, NON_ROOMS_REVENUE_PCT |
| Rentabilidad | GOP, GOPPAR, GOP_MARGIN, PROFIT_POR |

Adicionalmente, se implementó un desglose departamental completo (Rooms, F&B, Undistributed) con métricas absolutas de revenue, opex, personal y profit por departamento.

#### Motor de agregación

El método `_agg_real_budget()` es el núcleo del cálculo. Dado un conjunto de dimensiones de agrupación (año, mes, hotel) y una lista de métricas, agrega los datos brutos por escenario (REAL/BUDGET), aplica las fórmulas vectorizadas de cada métrica y calcula la variación absoluta. Este diseño permite calcular cualquier combinación de KPIs con una única función.

#### Herramientas expuestas al agente

Se exponen cinco herramientas al agente conversacional:

- `overall_kpis_annual()` — KPIs agregados por año, todos los hoteles
- `kpis_by_hotel_annual()` — KPIs por hotel y año
- `kpis_monthly(year)` — KPIs mensuales para un año dado
- `departmental_kpis_annual(year?)` — Desglose departamental anual
- `departmental_kpis_monthly(year)` — Desglose departamental mensual

Todas las herramientas devuelven tablas markdown formateadas, no DataFrames crudos. Esta decisión fue clave para que el agente pueda interpretar correctamente los datos (ver sección 4.3).

### 3.4 Agente conversacional

El agente está construido sobre LangChain con el patrón ReAct (Reasoning + Acting). Recibe un mensaje del usuario, razona sobre qué herramientas necesita, las invoca, observa los resultados y genera una respuesta fundamentada en datos reales.

#### Streaming con SSE

Las respuestas del agente se transmiten token a token mediante Server-Sent Events (SSE). El frontend consume el stream en tiempo real, lo que mejora significativamente la percepción de velocidad para respuestas largas.

#### Contexto de insights

Al construirse por petición, el agente recibe los insights activos del portafolio como extensión del system prompt. Esto permite que sus respuestas sean coherentes con el análisis financiero vigente sin necesidad de una consulta adicional a base de datos.

#### System prompt

El system prompt define el dominio estricto del agente (solo análisis financiero hotelero), las reglas de comportamiento ante ambigüedad (defaultear al año más reciente, inferir contexto del historial) y el formato de respuesta esperado. La política de ambigüedad fue refinada durante las pruebas al detectar que la instrucción original de "siempre preguntar antes de responder" generaba comportamientos subóptimos.

#### Logging estructurado

Todos los turnos de conversación quedan registrados con Loguru: petición entrante, insights recibidos, herramientas invocadas con sus respuestas completas, y respuesta final con tiempo de ejecución. Los logs se emiten en consola (nivel INFO) y en fichero rotativo de 10 MB (nivel DEBUG).

### 3.5 Motor de insights

El motor de insights (`app/insights/`) analiza los KPIs del portafolio y extrae automáticamente los tres hallazgos con mayor impacto en el negocio. Cada insight incluye texto descriptivo, valor numérico clave y recomendación accionable, todo en inglés y español.

Los insights se generan una sola vez y se persisten en base de datos. Las llamadas posteriores a `GET /api/insights` sirven el caché sin consumir créditos de API. El endpoint `POST /api/insights/refresh` permite regenerarlos bajo demanda.

**Modelo utilizado:** GPT-5.4 Mini, temperatura 0.1 (resultados reproducibles, selección estable).

### 3.6 Motor de sugerencias

El motor de sugerencias opera en dos modos:

- **Sugerencias iniciales** (`GET /api/suggestions`): genera seis preguntas específicas basadas en los KPIs del portafolio. Se cachean en base de datos y se regeneran junto con los insights al hacer refresh.
- **Sugerencias de seguimiento** (`POST /api/suggestions/followup`): genera tres preguntas contextuales basadas en el historial de la conversación activa (hasta 10 mensajes). No se cachean.

**Modelo utilizado:** GPT-5.4 Nano, temperatura 0.7 (mayor diversidad, evita repetición).

### 3.7 Módulo de feedback

El módulo de feedback permite a los usuarios valorar cada respuesta del agente con thumbs up/down. Las valoraciones negativas pueden incluir un comentario libre mediante un modal emergente. Cada registro almacena:

- Identificador del mensaje
- Valoración (+1 / -1)
- Comentario opcional
- Contenido íntegro del mensaje evaluado
- Historial de los últimos 10 mensajes de la conversación

Este registro permite auditar la calidad de las respuestas y detectar patrones de insatisfacción.

### 3.8 Frontend

La interfaz de usuario es una SPA (Single Page Application) servida como fichero estático por FastAPI. Está construida con Alpine.js v3 para la reactividad, Tailwind CSS para los estilos y Marked.js para el renderizado de markdown en las respuestas del agente.

La ausencia de proceso de build y el uso de CDN para todas las dependencias frontend hace que el sistema sea completamente ejecutable con un único comando de Python, sin herramientas de compilación adicionales.

### 3.9 Observabilidad

Langfuse registra automáticamente todas las llamadas a los modelos LLM: trazas completas, latencias, tokens consumidos y coste estimado por módulo. La integración es opcional; si no se configura, el sistema opera sin ella.

### 3.10 Selección de modelos LLM

La configuración final de modelos responde a una estrategia de eficiencia por tarea:

| Módulo | Modelo | Temperatura | Justificación |
|---|---|---|---|
| Agente | GPT-5.4 Mini | 0.1 | Razonamiento y tool calling; máxima consistencia |
| Insights | GPT-5.4 Mini | 0.1 | Tarea estructurada; resultados reproducibles |
| Sugerencias | GPT-5.4 Nano | 0.7 | Generación de texto corto; prioridad al coste |
| Juez UAT | GPT-5.4 Mini | 0.0 | Evaluación; máximo determinismo |

El punto de partida del proyecto utilizaba GPT-4.1 en todos los módulos. La migración a modelos de la familia 5.4 redujo la latencia de forma perceptible y el coste por sesión de forma significativa, sin pérdida de calidad funcional medible.

### 3.11 Framework de evaluaciones UAT

Se diseñó e implementó un framework de evaluación autónomo (`evaluations/`) completamente desacoplado de la API. Utiliza el patrón LLM-as-judge: un segundo modelo evalúa las respuestas del sistema frente a criterios definidos en lenguaje natural.

El framework incluye una CLI con cinco comandos (`run`, `report`, `benchmark`, `show`, `list-cases`, `list-runs`), persistencia de resultados en SQLite y generación de reportes en markdown y HTML.

---

## 4. Pruebas y resultados

### 4.1 Estrategia de evaluación

Las evaluaciones implementadas son pruebas de aceptación de extremo a extremo (UAT) que validan el comportamiento observable del sistema completo: desde el input del usuario hasta la respuesta generada por el agente. No se realizaron tests unitarios sobre componentes aislados, dado que la calidad del sistema depende de la integración entre la capa de datos, el razonamiento del agente y el formato de salida.

La elección del patrón LLM-as-judge responde a una limitación fundamental de los sistemas generativos: sus respuestas no son deterministas ni exactas en su forma textual. Dos respuestas semánticamente equivalentes —"El RevPAR de 2025 fue $177" y "En 2025, el RevPAR alcanzó los $177.03"— son distintas como strings pero equivalentes como información. El juez LLM entiende esa equivalencia; las comparaciones exactas de texto no.

### 4.2 Casos de prueba definidos

Se definieron 13 casos de prueba distribuidos en tres módulos:

| Módulo | Casos | Dimensiones evaluadas |
|---|---|---|
| **Agente** | 9 | Consulta directa de KPI, rechazo fuera de dominio, respuesta en español, comparación temporal, desviación vs presupuesto, desglose departamental, tendencia mensual, coherencia multi-turno, consulta ambigua |
| **Insights** | 2 | Estructura de campos, contenido bilingüe |
| **Sugerencias** | 2 | Estructura y cantidad, relevancia contextual de seguimiento |

Cada caso define entre 3 y 4 criterios observables desde el texto de la respuesta, sin necesidad de datos externos.

### 4.3 Problemas detectados y correcciones aplicadas

Las evaluaciones detectaron cuatro categorías de problemas, todos resueltos durante el proceso de testing:

#### Problema 1: El agente devolvía €0.0 como RevPAR

**Síntoma:** El caso `agent_kpi_directo` fallaba con score 25%. La respuesta del agente indicaba "Overall RevPAR for 2025 was €0.0" y reconocía no haber podido extraer el valor.

**Causa raíz:** Los métodos del `KpiService` devolvían objetos `pd.DataFrame`. Al ser convertidos a string por LangChain, producían tablas extremadamente anchas que pandas truncaba. El agente no podía parsear la salida y alucinaba el valor.

**Solución:** Se refactorizaron todos los métodos públicos del `KpiService` para devolver tablas markdown formateadas en lugar de DataFrames crudos. Se extrajeron los conjuntos `PCT_BASES` y `MILLIONS_BASES` como atributos de clase para un formateo consistente. Se corrigió además un bug preexistente en la función de formato que producía columnas de ocupación (OCC) en formato dólar en lugar de porcentaje.

#### Problema 2: El agente pedía clarificación en lugar de responder

**Síntoma:** Los casos `agent_consulta_ambigua` y `agent_multiturn` fallaban porque el agente pedía al usuario que especificara el período o los hoteles en cuestión, en lugar de inferirlos del contexto.

**Causa raíz:** El system prompt incluía la instrucción "always ask one clarifying question before answering" y "never assume scope when the question could mean multiple things".

**Solución:** Se reescribió la sección de ambigüedad del system prompt adoptando una política de defaults: sin período especificado → usar el año más reciente disponible (2025); sin hotel especificado → usar el portafolio completo; con historial de conversación → inferir contexto sin pedir confirmación. Solo se permite pedir clarificación cuando la pregunta es genuinamente irresoluble.

#### Problema 3: Criterios no verificables por el juez

**Síntoma:** Criterios como "no inventa datos" o "está basado en datos reales" fallaban sistemáticamente porque el juez LLM no tiene acceso a los datos reales del sistema y no puede verificar la veracidad de los valores.

**Causa raíz:** Error de diseño en los criterios de evaluación. El juez solo puede evaluar lo observable en el texto de la respuesta.

**Solución:** Se reformularon todos los criterios afectados en términos verificables desde el texto: "el valor está en un rango razonable para RevPAR hotelero (entre $30 y $600)", "menciona el año al que corresponde el dato", "los valores están expresados como porcentajes".

#### Problema 4: El endpoint de sugerencias de seguimiento devolvía 422

**Síntoma:** El caso `suggestions_followup` fallaba con error HTTP 422 Unprocessable Entity.

**Causa raíz:** El campo `last_response` del modelo `FollowupRequest` era obligatorio (sin valor por defecto), pero el caso de prueba solo enviaba el campo `messages`, que es el que se usa cuando hay conversación disponible. La lógica del router no utiliza `last_response` cuando `messages` está presente.

**Solución:** Se declaró `last_response` como campo opcional con valor por defecto de cadena vacía.

### 4.4 Resultados finales

Tras aplicar todas las correcciones, la suite completa de 13 casos alcanzó un **100% de pass rate** con un score medio del **98%**.

| Módulo | Casos | Pasados | Score medio |
|---|---|---|---|
| Agent | 9 | 9 | 97% |
| Insights | 2 | 2 | 100% |
| Suggestions | 2 | 2 | 100% |
| **Total** | **13** | **13** | **98%** |

La evolución del score a lo largo del proceso de desarrollo refleja el impacto directo de cada corrección:

| Ejecución | Casos | Pass rate | Score medio | Contexto |
|---|---|---|---|---|
| Run `02fac82c` | 1 | 0% | 25% | Primera prueba — agente devuelve €0.0 |
| Run `e282b439` | 9 | 78% | 73% | Tras formatear herramientas — quedan 2 fallos de comportamiento |
| Run `af8271cf` | 9 | 100% | 97% | Tras corregir system prompt |
| Run `f0b305d9` | 13 | 100% | 98% | Suite completa incluyendo insights y sugerencias |

### 4.5 Contribuciones del proyecto

El sistema demuestra la viabilidad de tres contribuciones principales:

**1. Automatización del análisis financiero hotelero**
Los insights se generan automáticamente a partir de datos tabulares sin intervención humana. Un analista que previamente necesitaba horas revisando un reporting package obtiene los hallazgos más relevantes en segundos.

**2. Interfaz conversacional sobre datos estructurados**
El agente permite consultar cualquier KPI, comparación o desglose en lenguaje natural, en inglés o español, con y sin historial de conversación. Las herramientas departamentales añadidas durante el proyecto amplían el nivel de detalle disponible hasta el desglose por departamento operativo.

**3. Framework de evaluación replicable para sistemas LLM**
El patrón LLM-as-judge implementado, con criterios verificables desde el texto y persistencia de resultados, es directamente aplicable a cualquier sistema conversacional basado en LLMs. El framework detectó cuatro categorías de problemas reales que no habrían sido detectables con tests unitarios convencionales.

### 4.6 Entregable final

El entregable funcional del proyecto es el sistema completo ejecutable localmente con un único comando:

```bash
uvicorn app.main:app --reload
```

El sistema incluye:
- API REST con cinco endpoints documentados
- Interfaz web accesible en `http://localhost:8000`
- Suite de evaluaciones UAT ejecutable con `python evaluations/cli.py run`
- Generación de reportes en markdown y HTML con `python evaluations/cli.py report`
- Observabilidad completa vía Langfuse (opcional)

La documentación técnica del proyecto está organizada en `docs/`:

| Documento | Contenido |
|---|---|
| `ARCHITECTURE.md` | Diagrama de módulos y flujos de datos |
| `TECH_STACK.md` | Stack tecnológico completo con versiones |
| `LLM_SELECTION.md` | Justificación de modelos y evolución desde GPT-4.1 |
| `UAT.md` | Framework de evaluación, criterios y uso de la CLI |

### 4.7 Análisis de costos — migración de modelos

Análisis cuantitativo sobre trazas de experimentación (23–30 abril 2026) que valida la decisión de migrar de la familia `gpt-4.1` a `gpt-5.4`. Reporte completo en `reports/llm-cost-latency-analysis.md`.

#### Reducción de costo por engine (post-migración)

| Engine | Modelo anterior | Modelo nuevo | Costo avg/llamada | Reducción |
|--------|----------------|--------------|-------------------|-----------|
| Chat | gpt-4.1 | gpt-5.4-mini | $0.0038 | -22% |
| Insights | gpt-4.1-2025-04-14 | gpt-5.4-mini | $0.0102 | -55% |
| Suggestions | gpt-4.1-2025-04-14 | gpt-5.4-nano | $0.0004 | -79% |

Insights es el engine de mayor costo por llamada. Suggestions resulta marginal a cualquier escala ($0.0004/llamada). El ahorro en Chat (-22%) se produce a pesar de procesar 8× más tokens por llamada, lo que confirma la brecha de precio por token entre generaciones de modelos.

#### Estimación de costo por usuario/mes (escenario real)

| Perfil | Uso típico | Costo/mes |
|--------|-----------|-----------|
| Ligero | 3 conv/semana, 1 insight/semana | ~$0.15 |
| Moderado | 5 conv/día, 1 insight/día | ~$1.06 |
| Intensivo | 15 conv/día, 3 insights/día | ~$3.18 |

Con distribución 60/30/10: **~$0.47/usuario/mes**. A 100 usuarios activos, el costo operativo LLM estimado es $47/mes (~$564/año).
