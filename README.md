# 📊 Data Analytics & BI Skills Suite

Suite profesional de metodologías, arquitecturas de datos, scripts y directrices técnicas desarrollada por **Rubén David Barrios Bello** (Data Analyst & BI Developer).

Este repositorio centraliza las habilidades técnicas, árboles de decisión operativa, scripts utilitarios y estándares de implementación derivados de mis certificaciones oficiales y de proyectos reales de analítica empresarial y Business Intelligence.

---

## 📚 Inventario de Skills

1. **`digital-analytics-ga4-gtm`** (Certificación Analytics Way):
   - Arquitectura y plan de medición corporativo (Measurement Plan).
   - Implementación de Google Analytics 4 (GA4) y Google Tag Manager (Web y Server-Side).
   - DataLayer para E-commerce, eventos de conversión y privacidad con **Consent Mode v2** (Básico vs Avanzado).
   - Visualización y cuadros de mando en Looker Studio.

2. **`python-sql-data-automation`** (Certificación Talento Tech):
   - Fundamentos avanzados de Python, colecciones estructuradas y programación modular por capas.
   - Persistencia transaccional ACID con **SQLite3** y prevención estricta de Inyección SQL mediante consultas parametrizadas obligatorias.
   - Ingesta, validación y exportación de archivos tabulares (CSV) e interfaces de consola (CLI).

3. **`bi-consulting-looker-studio`** (Certificación Talento Tech):
   - Consultoría estratégica de BI: alineación de objetivos de negocio con métricas SMART y auditoría de calidad de datos.
   - Modelado analítico avanzado en Google Sheets (`QUERY`, `INDEX/MATCH`, `ARRAYFORMULA`).
   - Estadística descriptiva aplicada al negocio (medidas robustas de tendencia central, dispersión y detección de outliers).
   - Diseño ergonómico de dashboards en **Looker Studio** bajo principios **Gestalt** y Storytelling con datos orientado a comités directivos.

4. **`python-data-analytics-eda`** (Certificación Talento Tech):
   - Análisis Exploratorio de Datos (EDA) univariado, bivariado y multivariado.
   - Computación matricial vectorizada con **NumPy** y manipulación analítica con **Pandas** (`groupby`, `pivot_table`, joins).
   - Curación de calidad: tratamiento de nulos, consistencia de tipos y correlaciones (Pearson vs Spearman).
   - Visualización científica y exploratoria con **Matplotlib**, **Seaborn** y **Plotly Express**.

5. **`machine-learning-business-analytics`** (Certificación Talento Tech):
   - Modelado predictivo supervisado (Regresión Lineal, Regresión Logística, Random Forest) enfocado en impacto comercial (Churn y retención).
   - Prevención absoluta de **Data Leakage** mediante `Pipeline` y `ColumnTransformer` en Scikit-Learn.
   - Segmentación de clientes no supervisada con **K-Means**, Método del Codo y Coeficiente de Silueta.
   - Validación cruzada estratificada (`StratifiedKFold`) y optimización con `GridSearchCV`.

6. **`powerbi-devops-fabric`**:
   - Adopción del formato **Power BI Project (`.pbip`)** y desacoplamiento de capas (`.SemanticModel` y `.Report`).
   - Estrategia de ramificación con **Git Flow** para Business Intelligence y políticas de Pull Request con code review.
   - Automatización de canalizaciones CI/CD con **Azure Pipelines** y **GitHub Actions** autenticadas con **Service Principals** en Microsoft Entra ID.
   - Integración nativa de Git en Workspaces de **Microsoft Fabric** y Deployment Pipelines (DEV $\rightarrow$ TEST $\rightarrow$ PROD).

7. **`dbt-bi-data-modeling`** (Proyecto Empresarial Retail Analytics):
   - Modelado dimensional Kimball para Data Warehouse: Tablas de Hechos (`fct_*`) y Dimensiones (`dim_*`).
   - Arquitectura modular de capas dbt: `staging`, `intermediate` y `marts`.
   - Optimización FinOps en **Google BigQuery**: particionamiento por fecha y clustering multivariable para reducción de costos de escaneo.
   - Pruebas de calidad automáticas: tests genéricos (`unique`, `not_null`, `relationships`) y pruebas singulares de reconciliación contable.

8. **`powerbi-developer-pbip`** (Proyecto Empresarial Retail Analytics):
   - Arquitectura de bajo nivel de **TMDL** con codificación obligatoria en **UTF-8 sin BOM** y delimitación multilínea.
   - Diseño de lienzo panorámico HD **1920x1080** con grilla milimétrica y márgenes estructurados.
   - Motor visual DAX con HTML, CSS puro y SVG nativo para tarjetas KPI con efecto **3D Dual Flip** interactivo (frente visual con sparkline y reverso con diagnóstico narrativo).
   - Diagnóstico y testing en vivo conectando al motor local de Analysis Services (`msmdsrv.exe`).

---

## 📂 Organización del Repositorio

- `docs/`: Certificaciones oficiales, programas de estudio y evidencia de formación.
- `MASTER_SKILLS_MANIFEST.md`: Manifiesto técnico detallado y trazabilidad curricular.
- `skills/`: Código fuente de cada habilidad con directrices (`SKILL.md`), guías técnicas (`references/`), scripts ejecutables (`scripts/`) y plantillas (`examples/`).
