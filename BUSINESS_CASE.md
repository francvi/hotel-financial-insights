# Business Case: Ecosistema de Insights Automatizados mediante IA Agéntica

## Proyecto: Estandarización de Análisis Financiero 

### 1. Objetivos y antecedentes
El objetivo es implementar una infraestructura analítica donde la interpretación de datos no dependa de la subjetividad de un analista humano, sino de un **Agente de IA con lógica de negocio estandarizada**. Esto garantiza que cada hotel del grupo hable el mismo "idioma financiero" y reaccione en tiempo real a las oportunidades del mercado.

---

### 2. Taxonomía de Métricas de Desempeño
A continuación, se detallan los indicadores clave que el sistema procesará automáticamente. Estas métricas siguen los estándares globales de la industria para asegurar la comparabilidad (**Benchmarking**).

| KPI | Definición | Fórmula | Aplicación | Tipo métrica |
| :--- | :--- | :--- | :----- | :--- |
| **CPOR** | Coste operativo departamental por habitación ocupada. | $CPOR = \frac{ROOMS\_OPEX}{RN}$ | Eficiencia de costes variables en pisos y recepción. | EFICIENCIA OPERATIVA |
| **CPH** | Coste operativo por habitación física disponible. | $CPH = \frac{ROOMS\_OPEX}{HABITACIONES}$ | Impacto de los costes fijos de mantenimiento del inventario. | EFICIENCIA OPERATIVA |
| **LBC** | Ratio de coste laboral sobre la producción de alojamiento. | $LBC = \frac{ROOMS\_PERSONNEL}{ROOMS\_REVENUE}$ | Productividad de la plantilla del departamento de Rooms. | EFICIENCIA OPERATIVA |
| **LPC_TOTAL** | Coste laboral total (Habitaciones y F&B) sobre ingresos totales. | $LPC\_TOTAL = \frac{ROOMS\_PERSONNEL + FB\_PERSONNEL}{OPERATING\_REVENUE}$ | Peso de la nómina operativa sobre el volumen de negocio. | EFICIENCIA OPERATIVA |
| **UNDISTRIB_OPEX_Pct** | Ratio de gastos no distribuidos (Admin, Ventas, Mant.) | $UNDISTRIB\_OPEX\_Pct = \frac{UNDISTRIB\_OPEX}{OPERATING\_REVENUE}$ | Eficiencia de los costes de estructura y soporte. | EFICIENCIA OPERATIVA |
| **F&B_CPOR** | Coste operativo de Alimentos y Bebidas por habitación ocupada. | $F\&B\_CPOR = \frac{FB\_OPEX}{RN}$ | Impacto del gasto de restauración por cliente alojado. | EFICIENCIA OPERATIVA |
| **F&B_CPH** | Coste operativo de Restauración por inventario total. | $F\&B\_CPH = \frac{FB\_OPEX}{HABITACIONES}$ | Coste estructural del departamento de F&B. | EFICIENCIA OPERATIVA |
| **F&B_LBC** | Ratio de coste laboral de F&B sobre sus propios ingresos. | $F\&B\_LBC = \frac{FB\_PERSONNEL}{FB\_REVENUE}$ | Control de productividad en cocina y sala. | EFICIENCIA OPERATIVA |
| **Food_Cost_Pct** | Porcentaje de consumo de alimentos (Food Cost). | $Food\_Cost\_Pct = \frac{FOOD\_COST}{FOOD\_REVENUE}$ | Control de escandallos, mermas y gestión de compras. | ANÁLISIS F&B |
| **Beverage_Cost_Pct** | Porcentaje de consumo de bebidas (Beverage Cost). | $Beverage\_Cost\_Pct = \frac{BEVERAGE\_COST}{BEVERAGE\_REVENUE}$ | Control de rentabilidad de bodega y barras. | ANÁLISIS F&B |
| **F&B_GOP_MARGIN** | Margen de beneficio operativo del departamento de F&B. | $F\&B\_GOP\_MARGIN = \frac{FB\_PROFIT}{FB\_REVENUE}$ | Eficiencia operativa neta de la explotación de restauración. | ANÁLISIS F&B |
| **F&B_REVPAR** | Ingreso de restauración por habitación disponible. | $F\&B\_REVPAR = \frac{FB\_REVENUE}{HABITACIONES}$ | Capacidad de captura de ingresos de F&B por activo físico. | ANÁLISIS F&B |
| **F&B_GOPPAR** | Beneficio de restauración por habitación disponible. | $F\&B\_GOPPAR = \frac{FB\_PROFIT}{HABITACIONES}$ | Contribución neta de F&B al beneficio por habitación. | ANÁLISIS F&B |
| **BANQUETS_CONTRIBUTION** | Peso de banquetes y eventos sobre el total de F&B. | $BANQUETS\_CONTRIBUTION = \frac{BANQUETS\_REVENUE}{FB\_REVENUE}$ | Dependencia y éxito del segmento MICE/Eventos. | ANÁLISIS F&B |
| **FB_PENSION_PCT** | Ratio de ingresos por regímenes (MP/PC) en el mix de F&B. | $FB\_PENSION\_PCT = \frac{FB\_PENSION}{FB\_REVENUE}$ | Análisis de venta de paquetes vs venta directa/carta. | ANÁLISIS F&B |
| **OCC** | Grado de ocupación del inventario de habitaciones. | $OCC = \frac{RN}{HABITACIONES}$ | Nivel de utilización de la capacidad del hotel. | REVENUE MGMT |
| **ADR** | Tarifa media diaria por habitación vendida. | $ADR = \frac{ROOMS\_REVENUE}{RN}$ | Valoración del posicionamiento de precio y demanda. | REVENUE MGMT |
| **REVPAR** | Ingresos de habitaciones por habitación disponible. | $REVPAR = \frac{ROOMS\_REVENUE}{HABITACIONES}$ | Indicador principal de rendimiento hotelero (Rev. Management). | REVENUE MGMT |
| **TRevPAR** | Ingresos totales por habitación disponible. | $TRevPAR = \frac{OPERATING\_REVENUE}{HABITACIONES}$ | Capacidad de monetización integral del activo físico. | REVENUE MGMT |
| **RevPOR** | Ingresos totales generados por cada habitación ocupada. | $RevPOR = \frac{OPERATING\_REVENUE}{RN}$ | Gasto medio total del huésped durante su estancia. | REVENUE MGMT |
| **AR** | Ingreso promedio por noche ocupada (Average Revenue). | $AR = \frac{OPERATING\_REVENUE}{RN}$ | Captura de ingresos totales por cliente alojado. | REVENUE MGMT |
| **UPGRADE_PEN** | Penetración de ingresos por mejoras de categoría. | $UPGRADE\_PEN = \frac{ROOMS\_REV\_UPGRADES}{ROOMS\_REV\_ALOJAMIENTO}$ | Eficiencia de las estrategias de venta incremental (Upselling). | REVENUE MGMT |
| **NON_ROOMS_REVENUE_PCT** | Peso de ingresos extra-habitación sobre el total. | $NON\_ROOMS\_REVENUE\_PCT = \frac{OPERATING\_REVENUE - ROOMS\_REVENUE}{OPERATING\_REVENUE}$ | Capacidad de diversificación del negocio hotelero. | REVENUE MGMT |
| **ANCILLARY_REV_POR** | Ingresos auxiliares por habitación ocupada. | $ANCILLARY\_REV\_POR = \frac{DAY\_PASS + OTHER\_DEPT\_REVENUE}{RN}$ | Rentabilidad de servicios complementarios por estancia. | REVENUE MGMT |
| **OTHER_REV_POR** | Ingresos de otros departamentos por habitación ocupada. | $OTHER\_REV\_POR = \frac{OTHER\_DEPT\_REVENUE}{RN}$ | Rendimiento de servicios periféricos (Spa, Parking, etc). | REVENUE MGMT |
| **GOP** | Beneficio Operativo Bruto (Gross Operating Profit). | $GOP = GOP$ | Resultado de la gestión operativa del hotel antes de fijos. | RENTABILIDAD |
| **GOPPAR** | Beneficio operativo por habitación disponible. | $GOPPAR = \frac{GOP}{HABITACIONES}$ | Medición de la rentabilidad final por activo físico. | RENTABILIDAD |
| **GOP_MARGIN** | Margen de beneficio sobre los ingresos totales. | $GOP\_MARGIN = \frac{GOP}{OPERATING\_REVENUE}$ | Eficiencia en la conversión de ventas a beneficio bruto. | RENTABILIDAD |
| **PROFIT_POR** | Beneficio operativo por habitación ocupada. | $PROFIT\_POR = \frac{GOP}{RN}$ | Ganancia neta generada por cada estancia vendida. | RENTABILIDAD |

### Guía de Referencia de Métricas Hoteleras (Estándar USALI)

Esta guía define los pilares terminológicos para el análisis de rendimiento hotelero, diferenciando entre eficiencia operativa y rendimiento del activo.

---

## 1. Dimensiones de Cálculo (PAR vs. POR)

| Sufijo | Término Completo | Base de Cálculo | Significado de Negocio |
| :--- | :--- | :--- | :--- |
| **PAR** | Per Available Room | Habitaciones Totales | Mide el **rendimiento del activo**. Evalúa el éxito del hotel independientemente de si las habitaciones están ocupadas o vacías. |
| **POR** | Per Occupied Room | Room Nights (RN) | Mide la **eficiencia operativa**. Evalúa cuánto se gasta o se ingresa por cada cliente real alojado. |

---

## 2. Definiciones de Negocio

### Restauración (F&B - Food & Beverage)
* **F&B Revenue:** Ingresos totales de puntos de venta (Restaurantes, Bares, Room Service, Banquetes).
* **Food/Beverage Cost:** Coste de la materia prima (escandallo). Se expresa habitualmente en porcentaje sobre su propia venta.
* **MICE / Banquetes:** Segmento de grupos y eventos. Se analiza su contribución para entender la dependencia de eventos sociales o corporativos.

### Regímenes Alimenticios (Pension Mix)
* **AD (Alojamiento y Desayuno):** Solo pernoctación y desayuno.
* **MP (Media Pensión):** Desayuno + 1 comida principal.
* **PC (Pensión Completa):** Desayuno + Almuerzo + Cena.
* **Lógica:** El análisis de estos porcentajes permite identificar si el ingreso de F&B es cautivo (incluido en reserva) o incremental (venta directa en el hotel).

### Rentabilidad Operativa
* **GOP (Gross Operating Profit):** Beneficio Bruto Operativo. Es el resultado de: `Ingresos Totales - Gastos Operativos`. Es la métrica clave para evaluar la gestión del Director del Hotel.
* **Labor Cost:** Coste de personal. Es el gasto más crítico en hotelería; se mide su ratio sobre ingresos para evaluar la productividad.

---

## 3. Glosario de Variables Comunes
* **RN (Room Nights):** Suma de habitaciones vendidas cada noche.
* **HABITACIONES:** Inventario físico total disponible del hotel.
* **OPERATING_REVENUE:** Suma de todos los ingresos de todos los departamentos operativos.
* **OPEX:** Gastos de explotación (suministros, reparaciones, limpieza, etc.).
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
