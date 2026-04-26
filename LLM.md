# Justificación de Modelos LLM

## Configuración seleccionada

| Módulo      | Modelo       | Temperatura |
| ----------- | ------------ | ----------- |
| Agente      | GPT-5.4 Mini | 0.1         |
| Insights    | GPT-5.4 Mini | 0.1         |
| Sugerencias | GPT-5.4 Nano | 0.7         |

---

## Justificación

### Agente

Requiere razonamiento, uso de herramientas y análisis financiero.  
Se usa GPT-5.4 Mini por su buen equilibrio coste/capacidad.

Temperatura baja (0.1):

- mayor precisión
- respuestas consistentes
- mejor tool calling

---

### Insights

Tarea estructurada sin ambigüedad.  
GPT-5.4 Mini es suficiente.

Temperatura baja (0.1):

- resultados reproducibles
- selección estable de insights

---

### Sugerencias

Generación simple de texto corto.  
GPT-5.4 Nano minimiza costes.

Temperatura alta (0.7):

- mayor diversidad
- evita repetición

---

## Conclusión

Se adopta una estrategia eficiente:

- modelos más potentes solo donde aportan valor
- control de temperatura según tipo de tarea
- minimización de costes sin perder calidad funcional
