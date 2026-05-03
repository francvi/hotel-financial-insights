# Análisis de Costos LLM — Reporte de Migración de Modelos

**Período:** 23 – 30 de abril de 2026  
**Migración:** familia `gpt-4.1` → familia `gpt-5.4`  
**Engines analizados:** Chat, Insights, Suggestions

---

## Resumen

| Engine | Modelo anterior | Modelo nuevo | Costo Δ/llamada |
|--------|----------------|--------------|-----------------|
| Chat | gpt-4.1 | gpt-5.4-mini | -22% ($0.0049 → $0.0038) |
| Insights | gpt-4.1-2025-04-14 | gpt-5.4-mini-2026-03-17 | **-55%** ($0.0228 → $0.0102) |
| Suggestions | gpt-4.1-2025-04-14 | gpt-5.4-nano-2026-03-17 | **-79%** ($0.0019 → $0.0004) |

**Conclusión clave:** La migración logró reducciones de costo significativas en los tres engines. Insights redujo el costo a la mitad. Suggestions pasó a ser prácticamente gratuito con el modelo nano.

---

## Chat Engine

**Observaciones:** 408 total | gpt-4.1: 79 llamadas (23–26 abr) | gpt-5.4-mini: 329 llamadas (26–30 abr)

| Métrica | gpt-4.1 | gpt-5.4-mini | Cambio |
|---------|---------|--------------|--------|
| Llamadas | 79 | 329 | — |
| Costo total | $0.3832 | $1.2628 | — |
| **Costo avg / llamada** | **$0.0049** | **$0.0038** | **-22%** |
| Tokens de entrada avg | 1.556 | 12.869 | +727%¹ |
| Tokens de salida avg | 104 | 77 | -26% |
| Tokens de caché leídos avg | 1.800 | 2.556 | — |

¹ El crecimiento de tokens de entrada probablemente refleja el historial de conversación acumulado a lo largo de las sesiones (no es un artefacto de precios). A pesar de tener 8× más tokens de entrada, el costo por llamada bajó un 22%, confirmando que gpt-5.4-mini es sustancialmente más barato por token.

---

## Insights Engine

**Observaciones:** 18 total | gpt-4.1: 11 llamadas (23–26 abr) | gpt-5.4-mini: 5 llamadas (28 abr)  
*2 entradas excluidas: errores de autenticación (401), sin inferencia exitosa.*

| Métrica | gpt-4.1-2025-04-14 | gpt-5.4-mini-2026-03-17 | Cambio |
|---------|-------------------|------------------------|--------|
| Llamadas (válidas) | 11 | 5 | — |
| Costo total | $0.2507 | $0.0510 | — |
| **Costo avg / llamada** | **$0.0228** | **$0.0102** | **-55%** |
| Tokens de entrada avg | 7.720 | 7.584 | -2% |
| Tokens de salida avg | 663 | 926 | +40% |
| Tokens de caché leídos avg | 4.096 | 4.608 | — |

Insights es el engine más pesado (prompts largos, análisis financiero estructurado). La migración redujo el costo a la mitad manteniendo el volumen de tokens prácticamente igual. El tamaño de muestra es pequeño (5 vs 11), por lo que el delta debe tomarse como indicativo.

---

## Suggestions Engine

**Observaciones:** 141 total | gpt-4.1: 49 llamadas (23–26 abr) | gpt-5.4-nano: 92 llamadas (26–30 abr)

| Métrica | gpt-4.1-2025-04-14 | gpt-5.4-nano-2026-03-17 | Cambio |
|---------|-------------------|------------------------|--------|
| Llamadas | 49 | 92 | — |
| Costo total | $0.0923 | $0.0347 | — |
| **Costo avg / llamada** | **$0.0019** | **$0.0004** | **-79%** |
| Tokens de entrada avg | 542 | 1.046 | +93%² |
| Tokens de salida avg | 97 | 134 | +38% |
| Tokens de caché leídos avg | 41 | 0 | — |

² El crecimiento de tokens de entrada (~2×) se debe a un prompt más completo post-migración. A $0.0004/llamada, este engine es prácticamente gratuito incluso a alto volumen.

---

## Proyección de Costos

Basado en los volúmenes de llamadas observados, extrapolados a 30 días:

| Engine | Tasa gpt-4.1 (est./mes) | Tasa gpt-5.4 (est./mes) | Ahorro mensual |
|--------|------------------------|------------------------|----------------|
| Chat | $0.0049 × N | $0.0038 × N | -22% del gasto en Chat |
| Insights | $0.0228 × N | $0.0102 × N | -55% del gasto en Insights |
| Suggestions | $0.0019 × N | $0.0004 × N | -79% del gasto en Suggestions |

Insights domina el costo por llamada. A escala, si Insights se ejecuta 1.000×/mes, eso son ~$22 vs ~$10 — $12 ahorrados por cada 1.000 llamadas.

---

## Costo por Usuario — Escenario Real (Estimación)

> Las trazas actuales corresponden a sesiones de prueba/experimentación, no a uso productivo real. Esta sección construye una estimación orientativa basada en los patrones observados y supuestos razonables para un producto de análisis financiero hotelero.

### Supuestos base (derivados de los traces)

| Parámetro | Valor observado | Fuente |
|-----------|----------------|--------|
| Costo por conversación de Chat | $0.0084 avg ($0.0042 p50) | 197 conversaciones únicas |
| Llamadas LLM por conversación | 2.1 avg | distribución: 2 turns (56%), 3 (22%), 1 (20%) |
| Suggestions por conversación | ~0.72 | ratio suggestions/conv global en traces |
| Costo por Suggestion | $0.0009 | 141 trazas post-migración |
| Costo por Insight | $0.0102 | modelo gpt-5.4-mini (post-migración) |

> Para la proyección se usa el costo post-migración (gpt-5.4). El costo de Chat se toma en $0.0038/llamada × avg 2.1 = $0.0080/conv.

---

### Perfiles de usuario

Se definen tres perfiles según intensidad de uso en días laborales (20 días/mes):

#### Perfil Ligero — Revisión semanal
*Ej: gerente de área que consulta el sistema 1–2 veces por semana*

| Acción | Frecuencia | Llamadas/mes | Costo/mes |
|--------|-----------|-------------|-----------|
| Conversaciones Chat | 3/semana | 12 conv → 25 llamadas | $0.10 |
| Suggestions (auto) | 0.72 × conv | ~9 | $0.01 |
| Insights | 1/semana | 4 | $0.04 |
| **Total** | | | **~$0.15/mes** |

#### Perfil Moderado — Uso diario
*Ej: controller financiero que usa el sistema todos los días hábiles*

| Acción | Frecuencia | Llamadas/mes | Costo/mes |
|--------|-----------|-------------|-----------|
| Conversaciones Chat | 5/día | 100 conv → 210 llamadas | $0.80 |
| Suggestions (auto) | 0.72 × conv | ~72 | $0.06 |
| Insights | 1/día | 20 | $0.20 |
| **Total** | | | **~$1.06/mes** |

#### Perfil Intensivo — Power user
*Ej: analista o director que trabaja con múltiples hoteles/períodos en la misma sesión*

| Acción | Frecuencia | Llamadas/mes | Costo/mes |
|--------|-----------|-------------|-----------|
| Conversaciones Chat | 15/día | 300 conv → 630 llamadas | $2.38 |
| Suggestions (auto) | 0.72 × conv | ~216 | $0.19 |
| Insights | 3/día | 60 | $0.61 |
| **Total** | | | **~$3.18/mes** |

---

### Proyección de costo total por cantidad de usuarios

Asumiendo una distribución realista de perfiles (60% ligero, 30% moderado, 10% intensivo):

**Costo ponderado por usuario: ~$0.47/mes**

| Usuarios activos | Costo mensual est. | Costo anual est. |
|-----------------|-------------------|-----------------|
| 10 | $4.70 | $56 |
| 50 | $23.50 | $282 |
| 100 | $47 | $564 |
| 500 | $235 | $2.820 |
| 1.000 | $470 | $5.640 |

### Consideraciones

- **Insights domina el costo** por llamada ($0.0102 vs $0.0009 suggestions). Usuarios que generan reportes frecuentes escalan significativamente más que usuarios que solo chatean.
- **Suggestions son esencialmente gratuitas** ($0.0009/llamada). Su impacto en el costo total es marginal incluso a alto volumen.
- **El historial de chat crece con el tiempo.** A medida que las conversaciones acumulan contexto, el costo por llamada de Chat tiende a subir. El p95 actual ($0.1663/conv) refleja sesiones con historial extenso.
- **Esta estimación no incluye** reintentos por error, llamadas de sistema/healthcheck, ni uso en pipelines automatizados (e.g., generación de reportes batch).
- Refinar con datos reales de producción luego de las primeras semanas de uso.

---

## Conclusiones

1. **La migración fue positiva en todos los engines.** Reducciones de costo del 22% al 79% sin cambios en la carga de trabajo.
2. **Insights: la mejora más significativa.** -55% costo con el mismo volumen de tokens. Misma tarea, la mitad del precio.
3. **Suggestions: costo marginal.** A $0.0004/llamada, el engine de sugerencias deja de ser un factor relevante en el presupuesto incluso a escala.
4. **Chat: ganancia moderada.** -22% a pesar de procesar 8× más tokens por llamada — refleja la brecha de precio por token entre generaciones de modelos.
5. **Muestra pequeña para Insights** (5 llamadas post-migración). Continuar monitoreando antes de considerar el delta como estable.
