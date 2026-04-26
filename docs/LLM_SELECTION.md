# Justificación de Modelos LLM

## Configuración seleccionada

| Módulo      | Modelo       | Temperatura |
| ----------- | ------------ | ----------- |
| Agente      | GPT-5.4 Mini | 0.1         |
| Insights    | GPT-5.4 Mini | 0.1         |
| Sugerencias | GPT-5.4 Nano | 0.7         |

---

## Migración de modelos (GPT-4.1 → familia GPT-5.4)

El sistema ha evolucionado desde el uso inicial de GPT-4.1 hacia la familia GPT-5.4 (Mini y Nano). Este cambio no solo ha supuesto una mejora en la calidad del razonamiento y la consistencia en tareas de tool calling, sino también una optimización significativa en **coste y latencia**.

En particular, los modelos GPT-5.4 Mini y Nano están diseñados para ofrecer una mejor relación rendimiento/coste que generaciones anteriores, permitiendo reducir el coste por token manteniendo o mejorando la calidad en tareas estructuradas. Además, su menor tamaño operativo se traduce en **menor tiempo de inferencia**, lo que mejora la respuesta del sistema en escenarios interactivos como el agente conversacional.

Como resultado, la migración desde GPT-4.1 ha permitido:

- Mayor eficiencia económica por consulta
- Reducción de latencia en respuestas en tiempo real
- Mejor adecuación del modelo a tareas específicas (routing por complejidad)
- Mantenimiento o mejora de la calidad en análisis financieros estructurados

Este ajuste refuerza la estrategia general del sistema de asignar modelos en función de la complejidad de la tarea, optimizando recursos sin comprometer la fiabilidad analítica.

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
