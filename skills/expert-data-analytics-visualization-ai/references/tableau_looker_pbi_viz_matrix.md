# Matriz de Implementación Visual: Tableau, Power BI y Looker Studio

Guía comparativa para diseñar reportes ejecutivos consistentes a través de las tres principales plataformas de Business Intelligence del curso **Experto en Análisis y Visualización de Datos + IA**.

---

## 1. Equivalencia de Conceptos Técnicos entre Plataformas

| Capacidad Analítica | Power BI Desktop | Tableau Public / Desktop | Looker Studio (Data Studio) |
| :--- | :--- | :--- | :--- |
| **Motor de Preparación (ETL)** | Power Query (Lenguaje M) | Panel de Fuente de Datos / Tableau Prep (Split, Pivot) | Conectores nativos + **Data Blending** (hasta 5 fuentes) |
| **Lenguaje de Fórmulas / KPIs** | **DAX** (`CALCULATE`, `SUMX`, `DIVIDE`) | Campos Calculados de Tableau + **Expresiones LOD** (`FIXED`, `INCLUDE`) | Campos Calculados (`CASE WHEN`, `SUM()`, `COUNT_DISTINCT()`) |
| **Clasificación de Campos** | Columnas, Medidas (`∑`) y Jerarquías | **Dimensiones** (Píldoras Azules / Discretas) y **Medidas** (Píldoras Verdes / Continuas) | Dimensiones (Verdes) y Métricas (Azules) |
| **Mapas Geográficos** | Mapa Coroplético, Mapa de Burbujas, Azure Maps | **Mapa de Símbolos y Polígonos** mediante Roles Geográficos (`Latitud`/`Longitud` autogeneradas) | Google Maps integrado (Burbujas, Áreas rellenas, Mapa de calor) |
| **Líneas de Tendencia y Analítica** | Pestaña **Análisis** (Línea de tendencia, Promedio, Pronóstico) | Pestaña **Análisis** (*Drag & Drop*: Línea de tendencia lineal/exponencial, Banda de confianza) | Propiedades de Estilo -> **Línea de tendencia** (Lineal, Exponencial, Polinómica) |
| **Interactividad y Filtros** | Segmentadores (*Slicers*), Cross-filtering nativo y Drill-through | **Tarjetas de Filtro**, Filtros de Contexto y **Acciones de Dashboard** (*Filter / Highlight Actions*) | Controles de filtro desplegables, Filtro de período y **Aplicar filtro** en gráficos |

---

## 2. Reglas de Elección del Gráfico Correcto para Comunicar Resultados

1. **Comparación de Categorías y Rankings:**
   - **Gráfico de Barras Horizontales ordenadas de mayor a menor:** Ideal cuando las etiquetas de categoría son largas (ej. `Sub-Categoría`, `Nombre de Producto`, `Campaña de Marketing`).
2. **Evolución Temporal y Estacionalidad:**
   - **Gráfico de Líneas Continuas + Línea de Tendencia:** Exclusivo para ejes de tiempo continuos (Día, Mes, Trimestre, Año). Permite evaluar la pendiente de crecimiento y proyectar tendencias.
3. **Distribución Geográfica y Regional:**
   - **Mapas Coropléticos (Regiones) o de Burbujas Proporcionales:** Acompañar siempre el mapa con una tabla o barra lateral Top N para facilitar la lectura exacta de cifras.
4. **Distribución Estadística y Detección de Anomalías:**
   - **Histogramas y Boxplots (R / Python / Visuales Estadísticos):** Indispensables antes de reportar "promedios", para identificar si la media está distorsionada por valores extremos (*outliers*).
5. **Tarjetas de KPI Ejecutivas:**
   - Todo KPI principal debe mostrar 3 elementos: **Valor Actual**, **Comparativa contra Objetivo o Período Anterior ($\Delta\%$)** y **Contexto Temporal**.
