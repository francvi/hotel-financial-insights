# Documento de Casos de Prueba

## Proyecto: Dashboard de Insights Financieros Hoteleros

---

## 1. Introducción

El presente documento define los casos de prueba diseñados para validar el correcto funcionamiento del sistema basado en modelos de lenguaje (LLMs).

Dado que el sistema combina razonamiento automático con acceso a datos estructurados (SQLite), los tests se enfocan en verificar:

- Corrección del análisis financiero
- Uso adecuado de herramientas (tool calling)
- Coherencia semántica de las respuestas
- Cumplimiento de formato en salidas estructuradas
- Robustez ante entradas ambiguas o fuera de dominio

---

## 2. Estrategia de Testing

Se han definido tres categorías de pruebas:

### 2.1 Tests deterministas

Validan casos donde existe una respuesta esperada clara (ej. valores KPI).

### 2.2 Tests de razonamiento

Evalúan el comportamiento del modelo sin exigir coincidencia exacta de texto.

### 2.3 Tests de robustez

Comprueban la capacidad del sistema para manejar:

- ambigüedad
- errores
- inputs fuera de alcance

---

## 3. Casos de prueba – Agente Conversacional

---

### Caso 1: Consulta directa de KPI

**Entrada:**

> "What is the RevPAR in 2023?"

**Comportamiento esperado:**

- Selección de herramienta: consulta anual de KPIs
- Extracción correcta del valor
- Respuesta clara y directa

**Criterios de éxito:**

- El valor coincide con la base de datos
- No se inventan datos
- Respuesta coherente

---

### Caso 2: Comparación temporal

**Entrada:**

> "Compare occupancy between 2022 and 2023"

**Comportamiento esperado:**

- Consulta de ambos periodos
- Identificación de tendencia (incremento/disminución)
- Explicación clara

**Criterios de éxito:**

- Comparación correcta
- Uso adecuado de datos
- Interpretación coherente

---

### Caso 3: Desglose mensual

**Entrada:**

> "Show monthly revenue for 2023"

**Comportamiento esperado:**

- Uso de herramienta de datos mensuales
- Presentación estructurada de resultados

**Criterios de éxito:**

- Datos completos
- Formato legible
- Sin omisiones

---

### Caso 4: Consulta ambigua

**Entrada:**

> "How is the hotel performing?"

**Comportamiento esperado:**

- Interpretación como análisis general
- Uso de múltiples KPIs relevantes
- Generación de resumen

**Criterios de éxito:**

- No responde de forma vacía
- Incluye métricas clave
- Explicación coherente

---

### Caso 5: Consulta multi-herramienta

**Entrada:**

> "Compare budget vs actual and explain variance"

**Comportamiento esperado:**

- Uso de múltiples consultas
- Cálculo o interpretación de desviaciones
- Explicación del impacto

**Criterios de éxito:**

- Comparación correcta
- Explicación razonada
- Sin errores numéricos

---

### Caso 6: Consulta en español

**Entrada:**

> "¿Cuál fue la ocupación en 2023?"

**Comportamiento esperado:**

- Respuesta en español
- Uso correcto de terminología financiera

**Criterios de éxito:**

- Idioma correcto
- Precisión del dato

---

### Caso 7: Consulta fuera de alcance

**Entrada:**

> "Tell me a joke"

**Comportamiento esperado:**

- Rechazo de la solicitud

**Criterios de éxito:**

- No responde a la petición
- Indica limitación del sistema

---

## 4. Casos de prueba – Generador de Insights

---

### Caso 8: Detección de KPI dominante

**Entrada:**

- Tabla KPI con caída significativa de revenue

**Comportamiento esperado:**

- Identificación del revenue como insight principal

**Criterios de éxito:**

- Insight relevante seleccionado
- Explicación coherente

---

### Caso 9: Selección de múltiples insights

**Entrada:**

- Tabla con múltiples variaciones relevantes

**Comportamiento esperado:**

- Selección de los 3 insights más importantes

**Criterios de éxito:**

- Priorización correcta
- No incluye métricas irrelevantes

---

### Caso 10: Consistencia

**Entrada:**

- Mismo dataset ejecutado múltiples veces

**Comportamiento esperado:**

- Resultados similares o idénticos

**Criterios de éxito:**

- Baja variabilidad
- Estabilidad del output

---

## 5. Casos de prueba – Generador de Sugerencias

---

### Caso 11: Formato de salida

**Entrada:**

- Datos KPI

**Comportamiento esperado:**

- Generación de 6 preguntas

**Criterios de éxito:**

- Máximo 10 palabras por pregunta
- Formato correcto

---

### Caso 12: Soporte bilingüe

**Entrada:**

- Datos KPI

**Comportamiento esperado:**

- Preguntas en inglés y español

**Criterios de éxito:**

- Ambos idiomas presentes
- Traducción coherente

---

### Caso 13: Diversidad

**Entrada:**

- Datos KPI

**Comportamiento esperado:**

- Preguntas variadas

**Criterios de éxito:**

- No repetición
- Diferentes enfoques

---

## 6. Criterios de Evaluación

Se utilizan tres tipos de validación:

### 6.1 Validación estructural

- Formato correcto (JSON, schema)
- Campos completos

### 6.2 Validación numérica

- Coincidencia con datos reales
- Ausencia de valores inventados

### 6.3 Validación semántica

- Interpretación correcta
- Coherencia en explicaciones

---

## 7. Limitaciones

Los sistemas basados en LLM presentan ciertas limitaciones:

- No determinismo en respuestas
- Sensibilidad a variaciones en prompts
- Evaluación subjetiva en algunos casos

Por ello, los tests combinan validaciones estrictas y heurísticas.

---

## 8. Conclusión

Los casos de prueba definidos permiten:

- validar el comportamiento del sistema
- asegurar la calidad del análisis financiero
- detectar errores en razonamiento o integración

El enfoque adoptado es adecuado para sistemas híbridos LLM + datos estructurados en un entorno académico.
