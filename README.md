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

## ☁️ Stack Oficial de Google Cloud & Agent Development Kit (ADK)

Este repositorio integra y respalda también el stack oficial de **Google Cloud Skills & Plugins para Antigravity**:

1. **Catálogo Oficial de Google Cloud (`google/skills`)**:
   - **Skills Core activas en `skills/`**: BigQuery (`bigquery-basics`, `bigquery-udfs`, `bigquery-migration-*`, `datalineage-*`, `dbt-sf-to-bq-translator`), Cloud Run (`cloud-run-basics`, `cloud-run-alert-configuration`), Bases de Datos (`cloud-sql-basics`, `alloydb-basics`, `spanner-basics`, `bigtable-basics`, `firebase-basics`), GKE (`gke-basics`), CI/CD & Terraform (`cloud-build-basics`, `google-cicd-deploy`, `google-cicd-pipeline-design`, `google-cicd-terraform`), IAM (`iam-helper-*`), Cloud Composer (`managed-airflow-*`), Gemini API (`gemini-api`), Google Analytics 4 APIs (`google-analytics-admin-api-basics`, `google-analytics-data-api-basics`) y los 6 pilares del **Google Cloud Well-Architected Framework** (`google-cloud-waf-*`).
   - **Catálogo Completo (196 skills de GCP)**: Respaldado íntegramente en `google-cloud-catalog/cloud/` para consulta local o carga bajo demanda con `finding-google-skills`.
2. **Google Cloud Developer + MCP de Documentación en Vivo**:
   - Validación estricta de sintaxis `gcloud`, autenticación IAM / Application Default Credentials (ADC), descubrimiento bajo demanda (`finding-google-skills`) y conexión en tiempo real con **Google Developer Knowledge MCP**.
3. **Data Agent Kit (35 Skills de Ingeniería de Datos en GCP)**:
   - Suite activa para BigQuery, Dataform, dbt, Dataproc / Managed Spark, Dataflow, Cloud Storage, Dataplex Knowledge Catalog y prevención de pérdida de datos (`accidental-data-loss-prevention`).
4. **Google Agents CLI (`google/agents-cli` — ADK & Cloud Run)**:
   - Las 7 skills oficiales del ciclo de vida de agentes en producción (`google-agents-cli-workflow`, `google-agents-cli-scaffold`, `google-agents-cli-adk-code`, `google-agents-cli-eval`, `google-agents-cli-deploy`, `google-agents-cli-publish`, `google-agents-cli-observability`) más `google-agents-cli-onboarding`.
5. **Regla Mandatoria de Seguridad GCP (`--dry-run` primero)**:
   - Definida en [`AGENTS.md`](./AGENTS.md) y [`.agents/rules/gcp-safe-dry-run.md`](./.agents/rules/gcp-safe-dry-run.md) (además de la configuración global `~/.gemini/config/AGENTS.md`), exigiendo validación de flags, ejecución previa con `--dry-run` / `--validate-only`, estimación de escaneo en BigQuery y bloqueo de operaciones destructivas (`DROP TABLE`, `TRUNCATE`, `delete`) sin confirmación humana.

---

## 📂 Organización del Repositorio

- `docs/`: Certificaciones oficiales, programas de estudio y evidencia de formación.
- `MASTER_SKILLS_MANIFEST.md`: Manifiesto técnico detallado y trazabilidad curricular.
- `AGENTS.md` y `.agents/rules/gcp-safe-dry-run.md`: Reglas mandatorias de seguridad en Google Cloud (`--dry-run` y FinOps).
- `skills/`: Habilidades VIP de carga inmediata (las **8 skills certificadas de Data & BI** + las **8 skills de Google Agents CLI ADK** + las **2 skills de GA4 API** + las **14 skills principales de Google Cloud**), sincronizadas 1 a 1 con `C:\Users\ismar\.gemini\config\skills\` y calibradas para que ninguna quede fuera del presupuesto de contexto (junto con las 36 del plugin `Data Agent Kit` y las 5 de `Google Cloud Developer`).
- `google-cloud-catalog/`: Respaldo completo de las **250 skills oficiales de Google**:
  - `google-cloud-catalog/cloud/`: Las **196 skills** completas de `google/skills/tree/main/skills/cloud`.
  - `google-cloud-catalog/data-agent-kit/`: Las **45 skills** completas del `Data Agent Kit` y Data Apps (`GoogleCloudPlatform/data-agent-kit-plugin`).
  - `google-cloud-catalog/agents-cli/`: Las **7 skills** completas de `google/agents-cli` (ADK).
  - `google-cloud-catalog/analytics/`: Las **2 skills** oficiales de Google Analytics 4 API.
