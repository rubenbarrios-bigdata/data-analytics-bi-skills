# Guía Técnica: Proceso ETL Multi-Herramienta y Optimización SQL (Índices y Caché)

Basado en el programa **Experto en Análisis y Visualización de Datos + IA** (*DataBoosters Academy*).

---

## 1. Matriz de Funciones ETL (Excel, SQL y Power Query)

Antes de construir cualquier visualización, los datos deben pasar por las 4 fases de transformación: **Texto, Fecha, Búsqueda y Lógica**.

| Operación ETL | Excel (Fórmulas / Tablas) | SQL / MySQL | Power Query (M) / Tableau |
| :--- | :--- | :--- | :--- |
| **Limpieza de Espacios y Formato** | `=ESPACIOS(NOMPROPIO(A2))` / `=TRIM(PROPER(A2))` | `TRIM( CONCAT(UPPER(LEFT(col,1)), LOWER(SUBSTRING(col,2))) )` | `Text.Proper(Text.Trim([Columna]))` |
| **Extracción de Subcadenas** | `=IZQUIERDA(A2, 3)`, `=EXTRAE(A2, 4, 5)` | `LEFT(col, 3)`, `SUBSTRING(col, 4, 5)` | `Text.Start([Col], 3)`, `SPLIT([Col], '-', 1)` |
| **Cálculo de Diferencia de Fechas** | `=SIFECHA(A2, B2, "d")` / `=DIAS(B2, A2)` | `DATEDIFF(fecha_entrega, fecha_pedido)` | `Duration.Days([Entrega] - [Pedido])` / `DATEDIFF('day', [Inicio], [Fin])` |
| **Extracción Temporal** | `=AÑO(A2)`, `=MES(A2)`, `=TEXTO(A2, "mmmm")` | `YEAR(fecha)`, `MONTH(fecha)`, `DATE_FORMAT(fecha, '%Y-%m')` | `Date.Year([Fecha])`, `Date.MonthName([Fecha])` |
| **Búsqueda y Enriquecimiento** | `=BUSCARX(A2, Cat!A:A, Cat!B:B, "Sin Datos")` | `LEFT JOIN catalogo c ON f.id_cat = c.id_cat` | `Table.NestedJoin` + `Table.ExpandTableColumn` |
| **Lógica Condicional de Negocio** | `=SI.CONJUNTO(C2>=1000, "VIP", C2>=500, "Regular", VERDADERO, "Básico")` | `CASE WHEN ventas >= 1000 THEN 'VIP' WHEN ventas >= 500 THEN 'Regular' ELSE 'Básico' END` | `if [Ventas] >= 1000 then "VIP" else ...` |

---

## 2. Optimización de Consultas SQL: Índices, SARGability y Caché

### A. Reglas de Indexación Estratégica (`CREATE INDEX`)
1. **Claves Foráneas y Columnas de `JOIN`:** Toda columna usada en `ON a.customer_id = b.customer_id` debe poseer un índice para transformar un *Nested Loop Scan* costoso en un *Index Seek*.
2. **Índices Compuestos (Orden de Selectividad):**
   - Colocar primero las columnas con filtros de igualdad (`=`) y luego las columnas de rango (`BETWEEN`, `>`, `<`) o agrupación (`GROUP BY`).
   ```sql
   CREATE INDEX idx_ventas_estado_fecha_cliente
   ON fact_ventas (estado_orden, fecha_venta, id_cliente);
   ```

### B. Consultas SARGable (*Search ARGument ABLE*)
Una consulta es *SARGable* cuando el motor SQL puede usar el árbol B-Tree del índice sin escanear toda la tabla:
- ❌ **Anti-patrón (Invalida el índice):**
  ```sql
  SELECT id_cliente, SUM(monto_total)
  FROM fact_ventas
  WHERE YEAR(fecha_venta) = 2026
  GROUP BY id_cliente;
  ```
- ✅ **Patrón Optimizado (Usa Range Scan sobre el índice):**
  ```sql
  SELECT id_cliente, SUM(monto_total)
  FROM fact_ventas
  WHERE fecha_venta >= '2026-01-01'
    AND fecha_venta <  '2027-01-01'
  GROUP BY id_cliente;
  ```

### C. Uso de `HAVING` vs `WHERE` y Caché
- **`WHERE` filtra filas antes de agrupar** (reduce el uso de memoria y aprovecha índices).
- **`HAVING` filtra grupos después de `GROUP BY`** (reservar exclusivamente para condiciones sobre funciones de agregación como `HAVING SUM(monto_total) > 5000`).
- **Aprovechamiento de Caché:** Mantener consultas deterministas (evitar `NOW()` o `RAND()` dentro del `SELECT` cuando se consulta un período fijo) para permitir el reuso del buffer pool y caché de resultados.
