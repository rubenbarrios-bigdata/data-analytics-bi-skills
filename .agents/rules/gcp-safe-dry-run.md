# Regla Mandatoria de Seguridad en Google Cloud Platform (GCP Safe Operations & FinOps)

Esta regla es de cumplimiento **OBLIGATORIO** en todas las sesiones y proyectos que interactúen con Google Cloud Platform (`gcloud`, `bq`, `gsutil`, Terraform, Dataform, dbt, BigQuery MCP o ADK / Cloud Run):

## 1. Verificación Previa Obligatoria (`--dry-run` / `--validate-only`)
- **En `gcloud` CLI e Infraestructura:** Antes de ejecutar cualquier comando que cree, modifique, despliegue o elimine recursos en Google Cloud, el agente **DEBE**:
  1. Validar la sintaxis exacta del subcomando hoja con `gcloud help <comando>` (prohibido inventar flags).
  2. Ejecutar o proponer primero la operación con `--dry-run` o `--validate-only` siempre que el comando lo soporte.
  3. Especificar explícitamente `--project=<PROJECT_ID>` y la bandera de región/ubicación (`--region` o `--location`) para evitar afectar cuentas compartidas equivocadas.
- **En BigQuery (`bq` y SQL):**
  1. Antes de ejecutar consultas sobre tablas grandes o de producción, realizar una estimación de bytes escaneados (`bq query --dry_run --use_legacy_sql=false "<SQL>"`) o verificar filtros de partición (`WHERE`) y clustering.
  2. **Prohibido hacer `SELECT *` sin límite o sin filtro de partición** en tablas particionadas.

## 2. Prevención de Pérdida de Datos (`STOP AND VERIFY`)
- **Bloqueo de Operaciones Destructivas:** El agente **NUNCA** debe ejecutar de forma autónoma:
  - SQL: `DROP TABLE`, `DROP VIEW`, `DROP SCHEMA`, `DROP DATABASE`, `TRUNCATE TABLE`, ni `DELETE` sin cláusula `WHERE` específica.
  - Cloud Storage: `gcloud storage rm` o `gsutil rm` sobre buckets o rutas de datos.
  - Infraestructura e IAM: `gcloud * delete`, modificaciones de políticas IAM (`add-iam-policy-binding`, `remove-iam-policy-binding`), `gcloud billing *`, `gcloud kms *` o `terraform destroy`.
- Ante cualquiera de estas operaciones, el agente debe **DETENERSE**, mostrar el comando exacto y su impacto, y esperar confirmación explícita del usuario.

## 3. Despliegue Seguro de Agentes (ADK & Cloud Run)
- Todo despliegue de agentes o servicios a Cloud Run debe utilizar cuentas de servicio dedicadas y aisladas (`--service-account`) con el principio de mínimo privilegio (least privilege), nunca la cuenta de servicio predeterminada de Compute Engine con permisos de Editor.
