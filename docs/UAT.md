# Evaluaciones UAT

## Enfoque: LLM-as-judge

Las evaluaciones validan el comportamiento real del sistema — no tests unitarios, sino comprobaciones de extremo a extremo contra la API en ejecución.

### Por qué no tests convencionales

Los sistemas LLM no producen salidas deterministas. "El RevPAR de 2025 fue $177" y "En 2025, el RevPAR alcanzó los $177.03" son semánticamente equivalentes pero distintos como strings. Un `assertEqual` fallaría; una comparación semántica no.

### Cómo funciona

Cada caso de prueba define un input (mensaje, historial, idioma) y una lista de criterios en lenguaje natural. Un segundo LLM — el **juez** — recibe la pregunta original, la respuesta del sistema y los criterios, y evalúa cada uno independientemente devolviendo un veredicto (`passed: true/false`) con una frase de razonamiento.

```
cases.yaml → CLI runner → API real → LLM juez → pass/fail + score → SQLite
```

Un caso pasa si al menos el 70% de sus criterios se cumplen.

El juez en este proyecto es **GPT-5.4 Mini con temperatura 0** para maximizar la consistencia entre ejecuciones.

### Cómo escribir buenos criterios

La calidad del juicio depende directamente de la calidad del criterio. Cada criterio debe ser evaluable **únicamente a partir del texto de la respuesta**, sin acceso a datos externos.

| Criterio malo | Criterio bueno |
|---|---|
| "No inventa datos" | "El valor de RevPAR está entre $30 y $600" |
| "Está basado en datos reales" | "Menciona el año 2025 al que corresponde el dato" |
| "La respuesta es correcta" | "Incluye valores numéricos para Rooms, F&B y Undistributed" |

Los criterios malos producen falsos negativos: el juez no tiene forma de verificarlos y tiende a fallar con razonamientos como "no puedo confirmar que el dato no sea inventado".

### Limitaciones

- El juez no tiene acceso a los datos reales — no puede verificar exactitud numérica, solo coherencia y formato.
- No es determinista — una respuesta borderline puede pasar o fallar entre ejecuciones. Usar para detectar tendencias, no como gate binario de CI.
- Añade latencia y coste: una llamada LLM extra por caso evaluado.
- El servidor debe estar activo durante la ejecución.

---

## Módulos cubiertos

| Módulo | Casos | Qué se valida |
|---|---|---|
| **Agent** | 9 | KPIs correctos, rechazo fuera de dominio, idioma, comparaciones temporales, desglose departamental, coherencia multi-turno, consultas vagas |
| **Insights** | 2 | Estructura completa, contenido bilingüe |
| **Suggestions** | 2 | Cantidad, formato, límite de palabras, relevancia contextual |

Los casos están definidos en [`evaluations/cases.yaml`](../evaluations/cases.yaml).

---

## Ejecución

El servidor debe estar corriendo antes de ejecutar evaluaciones.

```bash
# Todos los casos
python evaluations/cli.py run

# Por módulo
python evaluations/cli.py run --module agent
python evaluations/cli.py run --module insights
python evaluations/cli.py run --module suggestions

# Un caso concreto
python evaluations/cli.py run --case agent_kpi_directo

# Servidor alternativo
python evaluations/cli.py run --base-url http://localhost:8001
```

---

## Inspección y benchmark

```bash
# Ver la respuesta y criterios de la última ejecución de un caso
python evaluations/cli.py show agent_kpi_directo

# Historial de ejecuciones
python evaluations/cli.py list-runs
python evaluations/cli.py benchmark
python evaluations/cli.py benchmark --last 5

# Comparar dos runs (detecta mejoras y regresiones caso a caso)
python evaluations/cli.py benchmark --run-a <run_id> --run-b <run_id>

# Listar todos los casos disponibles
python evaluations/cli.py list-cases
```

Los resultados se persisten en la tabla `evaluations` del fichero SQLite del proyecto, junto con la respuesta completa del sistema y el razonamiento del juez por criterio.

---

## Añadir un caso nuevo

Editar `evaluations/cases.yaml` siguiendo esta estructura:

```yaml
- id: agent_mi_nuevo_caso          # único, snake_case
  module: agent                    # agent | insights | suggestions
  description: Descripción breve
  endpoint: POST /api/chat         # o GET /api/insights, etc.
  input:
    message: "Pregunta al agente"
    history: []
    language: en
    insights: []
  criteria:
    - Criterio observable desde el texto de la respuesta
    - Otro criterio verificable sin datos externos
```

El caso se carga automáticamente en la próxima ejecución de `cli.py run`.

**Regla para criterios:** cada criterio debe ser evaluable únicamente a partir del texto de la respuesta. Criterios como "no inventa datos" o "está basado en datos reales" no son verificables por el juez — reemplazarlos por criterios observables como "el valor está en el rango X–Y" o "menciona el año al que corresponde el dato".

