# Reporte UAT — run `f0b305d9`

**Fecha:** 2026-04-26 20:48:24  
**Resultado:** 13/13 casos pasados (100%)  
**Score medio:** 98%

---

## Resumen por módulo

| Módulo | Casos | Pasados | Fallidos | Score medio |
|---|---|---|---|---|
| agent | 9 | 9 | 0 | 97% |
| insights | 2 | 2 | 0 | 100% |
| suggestions | 2 | 2 | 0 | 100% |

---

## Detalle de casos

### Agent

#### ✅ PASS `agent_comparacion_temporal` — Comparación de un KPI entre dos años distintos

**Score:** 100%  |  **Latencia:** 3883ms

- ✓ 1. Menciona explícitamente tanto 2025 como 2026
- ✓ 2. Incluye valores numéricos o porcentajes de GOP margin para ambos años
- ✓ 3. Identifica cuál año tuvo mejor margen y lo justifica
- ✓ 4. Los valores de GOP margin para ambos años están expresados como porcentajes (entre 0% y 100%)

#### ✅ PASS `agent_consulta_ambigua` — Manejo de consulta vaga con interpretación útil

**Score:** 100%  |  **Latencia:** 6324ms

- ✓ No devuelve una respuesta vacía ni pide que se reformule la pregunta
- ✓ Presenta un resumen con al menos 2 KPIs distintos con valores numéricos concretos
- ✓ Menciona al menos un año específico (2025 o 2026) al que corresponden los datos

#### ✅ PASS `agent_desglose_departamental` — Desglose del GOP por departamento usando las nuevas herramientas

**Score:** 75%  |  **Latencia:** 4676ms

- ✓ 1. Menciona el departamento de Rooms (habitaciones) con valores numéricos
- ✓ 2. Menciona el departamento de F&B (alimentos y bebidas) con valores numéricos
- ✓ 3. Menciona los costes Undistributed (no distribuidos)
- ✗ 4. Los valores son coherentes entre sí y con el GOP total
  - *Aunque se reporta un total GOP, las cifras de Rooms, F&B y Undistributed no cuadran claramente entre sí con el total presentado, y además aparecen inconsistencias internas en los signos de las desviaciones.*

#### ✅ PASS `agent_desviacion_presupuesto` — Análisis de desviación real vs presupuesto por hotel

**Score:** 100%  |  **Latencia:** 4266ms

- ✓ Menciona al menos un nombre de hotel específico del portafolio
- ✓ Compara valores REAL vs BUDGET de RevPAR
- ✓ Cuantifica o describe la magnitud de la desviación

#### ✅ PASS `agent_fuera_de_alcance` — Rechazo de consulta fuera del dominio financiero hotelero

**Score:** 100%  |  **Latencia:** 1285ms

- ✓ La respuesta rechaza la solicitud sin cumplirla
- ✓ No cuenta ningún chiste ni proporciona contenido de entretenimiento
- ✓ Indica que solo puede ayudar con análisis financiero hotelero

#### ✅ PASS `agent_idioma_español` — Respuesta completa en español cuando se solicita

**Score:** 100%  |  **Latencia:** 2180ms

- ✓ La respuesta está completamente en español
- ✓ Incluye un valor de ocupación expresado como porcentaje
- ✓ Usa terminología financiera hotelera correcta en español

#### ✅ PASS `agent_kpi_directo` — Consulta directa de un KPI anual

**Score:** 100%  |  **Latencia:** 2445ms

- ✓ La respuesta incluye un valor numérico de RevPAR
- ✓ El valor está en un rango razonable para RevPAR hotelero (entre $30 y $600)
- ✓ La respuesta especifica el año o período al que corresponde el dato (2025)

#### ✅ PASS `agent_multiturn` — Coherencia contextual en conversación de múltiples turnos

**Score:** 100%  |  **Latencia:** 2852ms

- ✓ La respuesta mantiene el contexto de los hoteles mencionados anteriormente
- ✓ Compara tasas de ocupación entre al menos dos hoteles
- ✓ No pide clarificación innecesaria sobre a qué hoteles se refiere

#### ✅ PASS `agent_tendencia_mensual` — Identificación de mejor y peor mes a partir de datos mensuales

**Score:** 100%  |  **Latencia:** 3816ms

- ✓ Presenta datos de RevPAR para múltiples meses de 2025
- ✓ Identifica el mes con mejor RevPAR con su valor numérico
- ✓ Identifica el mes con peor RevPAR con su valor numérico
- ✓ Los valores de RevPAR mencionados están en un rango razonable (entre $30 y $600)


### Insights

#### ✅ PASS `insights_bilingue` — Los insights están correctamente traducidos al español

**Score:** 100%  |  **Latencia:** 14ms

- ✓ El campo text_es de cada insight está en español
- ✓ El campo recommendation_es de cada insight está en español
- ✓ Las traducciones son coherentes con su versión en inglés

#### ✅ PASS `insights_estructura` — Los insights devueltos tienen estructura completa y correcta

**Score:** 100%  |  **Latencia:** 14ms

- ✓ La respuesta contiene exactamente 3 insights
- ✓ Cada insight tiene los campos text_en, text_es, value, recommendation_en y recommendation_es
- ✓ Ningún campo está vacío o es nulo
- ✓ Los valores numéricos en el campo 'value' son coherentes (porcentajes, importes)


### Suggestions

#### ✅ PASS `suggestions_estructura` — Las sugerencias iniciales tienen estructura y cantidad correctas

**Score:** 100%  |  **Latencia:** 12ms

- ✓ La respuesta contiene exactamente 6 sugerencias
- ✓ Cada sugerencia tiene los campos text_en y text_es
- ✓ Las preguntas en inglés tienen un máximo de 10 palabras
- ✓ Las preguntas en español son traducciones coherentes del inglés

#### ✅ PASS `suggestions_followup` — Las sugerencias de seguimiento son contextuales a la conversación

**Score:** 100%  |  **Latencia:** 2049ms

- ✓ La respuesta contiene exactamente 3 preguntas de seguimiento
- ✓ Las preguntas son relevantes para la conversación sobre RevPAR y presupuesto
- ✓ No repiten la pregunta ya realizada en el historial
- ✓ Cada pregunta está en inglés y español

---

*Generado el 2026-04-26 22:53*
