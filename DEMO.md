# Guión de Demo — Hotel Financial Insights

Secuencia de 7 capturas en español que cubre todos los módulos del sistema en un flujo narrativo coherente.

---

## Preparación previa

```bash
uvicorn app.main:app --reload
```

- Abrir `http://localhost:8000` en Chrome o Safari
- Zoom del navegador: **90%**
- Ventana maximizada
- Verificar que insights y sugerencias estén cargados (sin spinner)
- Seleccionar idioma **Español** en la interfaz antes de comenzar

---

## Capturas

### 1 — Vista inicial

**Acción:** Ninguna. Capturar la pantalla tal como carga.

Muestra el sistema listo: panel de insights activo, sugerencias visibles, chat vacío.

---

### 2 — Insights automáticos

**Acción:** Foco en la sección de insights.

Capturar los 3 insight cards con texto, valor numérico y recomendación visibles.

---

### 3 — Visión general del portafolio

**Mensaje:**
```
¿Cómo está rindiendo el portafolio?
```

Capturar la respuesta completa. Debe mostrar al menos 2 KPIs con valores concretos.

---

### 4 — Análisis con tabla de datos

**Mensaje:**
```
Muéstrame la evolución mensual del RevPAR en 2025 e identifica el mejor y peor mes
```

Capturar la respuesta con la tabla markdown renderizada, incluyendo los meses extremos.

---

### 5 — Desglose departamental

**Mensaje:**
```
Desglosa el GOP de 2025 por departamento: Rooms, F&B y costes no distribuidos
```

Capturar la respuesta con los valores de los tres departamentos visibles.

---

### 6 — Conversación multi-turno

**Mensaje** (sin borrar el historial de la captura anterior):
```
¿Y cómo se compara eso con el presupuesto? ¿Qué departamento tuvo mayor desviación?
```

Capturar la respuesta que continúa el contexto departamental sin que el usuario lo repita.

---

### 7 — Rechazo fuera de dominio

**Mensaje:**
```
Cuéntame un chiste sobre piratas
```

Capturar la respuesta de rechazo en español.

---

## Orden y notas

| # | Módulo | Mensaje |
|---|--------|---------|
| 1 | — | *(sin acción)* |
| 2 | Insights | *(sin acción)* |
| 3 | Agente | "¿Cómo está rindiendo el portafolio?" |
| 4 | Agente | "Muéstrame la evolución mensual del RevPAR en 2025..." |
| 5 | Agente | "Desglosa el GOP de 2025 por departamento..." |
| 6 | Agente | "¿Y cómo se compara eso con el presupuesto?..." |
| 7 | Agente | "Cuéntame un chiste sobre piratas" |

Las capturas 3–7 deben hacerse en **secuencia continua sin limpiar el chat**, para que la captura 6 demuestre el multi-turno de forma auténtica.
