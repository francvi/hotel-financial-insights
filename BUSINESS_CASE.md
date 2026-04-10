# Business Case: Ecosistema de Insights Automatizados mediante IA Agéntica

## Proyecto: Estandarización de Análisis Financiero 

### 1. Objetivos y antecedentes
El objetivo es implementar una infraestructura analítica donde la interpretación de datos no dependa de la subjetividad de un analista humano, sino de un **Agente de IA con lógica de negocio estandarizada**. Esto garantiza que cada hotel del grupo hable el mismo "idioma financiero" y reaccione en tiempo real a las oportunidades del mercado.

---

### 2. Taxonomía de Métricas de Desempeño
A continuación, se detallan los indicadores clave que el sistema procesará automáticamente. Estas métricas siguen los estándares globales de la industria para asegurar la comparabilidad (**Benchmarking**).

| Métrica | Definición | Fórmula  | Aplicación / ISO |
| :--- | :---| :----- | :--- |
| **ADR** | Precio promedio pagado por habitación ocupada. | $ADR = \frac{\text{Ingresos de Habitaciones}}{\text{Habitaciones Vendidas}}$ | Posicionamiento de marca y elasticidad. |
| **RevPAR** | Ingreso por habitación disponible. | $RevPAR = ADR \times \text{Ocupación}$ | Eficiencia de ventas e inventario. |
| **RevPAM** | Ingreso por metro cuadrado. | $RevPAM = \frac{\text{Ingresos Totales}}{\text{m}^2 \text{ Totales del Establecimiento}}$ | Eficiencia del activo inmobiliario. |
| **NRevPAR** | Ingreso neto por hab. disponible. | $NRevPAR = \frac{\text{Ingr. Hab} - \text{Costos Adquisición}}{\text{Total Hab. Disponibles}}$ | Rentabilidad real de canales (Neto). |
| **GOPPAR** | Beneficio operativo bruto por hab. disponible. | $GOPPAR = \frac{\text{Gross Operating Profit}}{\text{Total Habitaciones Disponibles}}$ | Rentabilidad real del negocio (Bottom-line). |
| **TRevPAR** | Ingreso total por habitación disponible. | $TRevPAR = \frac{\text{Ingresos Totales}}{\text{Total Habitaciones Disponibles}}$ | Capacidad de monetización cruzada. |
| **TRevPEC** | Ingreso total por huésped. | $TRevPEC = \frac{\text{Ingresos Totales}}{\text{Total Huéspedes}}$ | Gasto promedio por cliente. |
| **ALOS** | Duración media de la estancia. | $ALOS = \frac{\text{Pernoctaciones}}{\text{Total de Reservas}}$ | Optimización de costos operativos. |
| **CPOR** | Costo por habitación ocupada. | $CPOR = \frac{\text{Costos Operativos}}{\text{Habitaciones Ocupadas}}$ | Eficiencia de mantenimiento y personal. |
| **RevPOR** | Ingreso por habitación ocupada. | $RevPOR = \frac{\text{Ingresos Totales}}{\text{Total Hab. Ocupadas}}$ | Rendimiento por reserva efectiva. |
| **RGI** | Índice de generación de ingresos vs mercado. | $RGI = \frac{\text{RevPAR Propio}}{\text{RevPAR Market CompSet}} \times 100$ | Cuota de mercado y competitividad. |
| **ARI** | Índice de tarifa media frente a competencia. | $ARI = \frac{\text{ADR Propio}}{\text{ADR Market CompSet}} \times 100$ | Poder de fijación de precios (Pricing Power). |
| **MPI** | Índice de penetración de mercado (Ocupación). | \( MPI = \frac{\text{Ocupación Propia}}{\text{Ocupación Market CompSet}} \times 100 \) | Eficacia en la captura de la demanda

### 3. Problemas que Resuelve la IA Agéntica

##### 3.1 Eliminación del Sesgo Interpretativo

La interpretación humana es inherentemente variable. Un analista puede priorizar el ADR por sobre el RevPAR debido a su experiencia previa, o pasar por alto anomalías menores durante un cierre de mes bajo presión.

**Lógica Determinista:** El agente de IA aplica un marco de razonamiento idéntico (basado en el prompt de experto en insights_generator.py) eliminando el "sesgo de confirmación" donde el analista solo busca datos que respalden su intuición previa.

**Disponibilidad y Consistencia:** A diferencia de un equipo humano que sufre de fatiga analítica, el agente mantiene el mismo rigor crítico en el insight número 1 que en el número 1,000, operando 24/7 sin degradación de calidad.

##### 3.2 Capacidad de agente multimodal <span style="color:red">(TO BE REVIEWED)</span> 

El agente tiene la capacidad de producir visualizaciones interactivas (gráficos de líneas para pickup, mapas de calor de ocupación o barras comparativas de RGI) de forma automática. Esto permite que el insight no sea solo texto, sino una experiencia visual que facilita la toma de decisiones inmediata.

Lectura y Digitalización de Documentos: Capacidad para razonar sobre reportes en PDF, contratos de grupos o folletos de eventos locales, integrando esta "visión" con la lógica numérica para predecir afluencia.

### 4. ROI Estimado <span style="color:red">(TO BE REVIEWED)</span> 

La estandarización mediante IA garantiza escalabilidad sin aumentar proporcionalmente la nómina administrativa.

Ahorro de tiempo: Reducción del 85% en el tiempo de "preparación de datos", moviendo al equipo hacia la "toma de decisiones".

Incremento de Ingresos: Se proyecta un aumento del 8% al 12% en el RevPAR al capturar ventanas de reserva que el análisis manual suele detectar demasiado tarde.
