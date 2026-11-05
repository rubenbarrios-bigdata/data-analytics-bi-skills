# Estrategias FinOps en BigQuery: Particionado, Clustering y Control de Costos

Google BigQuery bajo el modelo On-Demand cobra aproximadamente \$6.25 USD por cada Terabyte (TB) de datos escaneados. Un diseño ineficiente en las tablas de hechos de dbt puede disparar los costos de facturación innecesariamente.

---

## 1. Particionamiento: División Física por Tiempo

El particionamiento divide la tabla en segmentos basados en una columna temporal (o rango de enteros). BigQuery aplica *Partition Pruning* (poda de particiones), leyendo únicamente las particiones involucradas en el filtro `WHERE`.

```sql
{{ config(
    materialized = 'table',
    partition_by = {
      "field": "fecha_evento",
      "data_type": "date",
      "granularity": "day"
    }
) }}
```

### Reglas Críticas para Consultas:
- **Evitar envolver la columna particionada en funciones:**
  - ❌ `WHERE DATE(fecha_evento) = '2026-11-04'` $\rightarrow$ Puede deshabilitar la poda y forzar escaneo completo.
  -  `WHERE fecha_evento = '2026-11-04'` $\rightarrow$ Poda eficiente de una única partición diaria.
- **Forzar filtro de partición:**
  - En tablas de escala multimillonaria, se puede configurar `require_partition_filter = true` para rechazar cualquier consulta que no filtre por la columna de partición.

---

## 2. Clustering: Ordenación Física Multivariable

Dentro de cada partición (o en tablas completas), el *Clustering* ordena los bloques de almacenamiento según los valores de hasta 4 columnas especificadas:

```sql
{{ config(
    materialized = 'table',
    partition_by = {"field": "fecha_evento", "data_type": "date", "granularity": "day"},
    cluster_by = ["sucursal_id", "cliente_id", "sku"]
) }}
```

### Cómo Elegir las Columnas de Clustering:
1. **Posición 1:** La columna de mayor cardinalidad más filtrada en los dashboards de BI (ej. `sucursal_id` o `canal_venta`).
2. **Posición 2 y 3:** Columnas utilizadas en cláusulas `GROUP BY` o filtros secundarios.
3. **BigQuery salta bloques completos** de almacenamiento que no coincidan con el valor buscado (*Block Skipping*), reduciendo los bytes leídos hasta en un 90%.

---

## 3. Comparativa: Sin Optimización vs Particionado + Clustering

| Escenario de Consulta en Power BI | Tabla No Optimizada | Tabla con Partition + Cluster | Ahorro FinOps |
| :--- | :--- | :--- | :--- |
| *Ventas del mes actual para Sucursal 101* | Escaneo de **toda la tabla** (ej. 150 GB = \$0.94 USD por query) | Escaneo de **1 mes + bloques de sucursal** (ej. 3.5 GB = \$0.02 USD) | **> 97% de reducción de costo** |
| *Refresco diario de tablero directivo (10 visuales)* | \$9.40 USD diarios | \$0.20 USD diarios | **\$276 USD de ahorro mensual** |

