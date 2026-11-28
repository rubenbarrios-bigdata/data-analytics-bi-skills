-- =============================================================================
-- Colección de Consultas SQL Analíticas y Optimización con Índices y Caché
-- Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
-- Certificación: Experto en Análisis y Visualización de Datos + IA (DataBoosters)
-- =============================================================================

-- 1. CREACIÓN DE ÍNDICES COMPUESTOS PARA OPTIMIZACIÓN DE RENDIMIENTO
-- Acelera predicados WHERE por rango de fecha/estado y JOINs con clientes/productos
CREATE INDEX idx_ordenes_fecha_estado
    ON fact_ordenes (estado_orden, fecha_orden, id_cliente);

CREATE INDEX idx_detalle_orden_producto
    ON fact_detalle_orden (id_orden, id_producto);

-- 2. CONSULTA ANALÍTICA CON JOINS, GROUP BY, HAVING Y PREDICADO SARGABLE
-- Objetivo: Identificar clientes activos con compras superiores a $2,500 en 2026
SELECT
    c.id_cliente,
    c.nombre_cliente,
    c.segmento,
    r.nombre_region,
    COUNT(DISTINCT o.id_orden) AS total_ordenes,
    ROUND(SUM(d.cantidad * d.precio_unitario * (1 - d.descuento)), 2) AS venta_neta_total,
    ROUND(AVG(d.cantidad * d.precio_unitario * (1 - d.descuento)), 2) AS ticket_promedio_item
FROM fact_ordenes AS o
INNER JOIN dim_clientes AS c
    ON o.id_cliente = c.id_cliente
INNER JOIN dim_regiones AS r
    ON c.id_region = r.id_region
INNER JOIN fact_detalle_orden AS d
    ON o.id_orden = d.id_orden
WHERE o.estado_orden = 'COMPLETADA'
  -- Predicado SARGable: usa el índice idx_ordenes_fecha_estado sin escanear toda la tabla
  AND o.fecha_orden >= '2026-01-01'
  AND o.fecha_orden <  '2027-01-01'
GROUP BY
    c.id_cliente,
    c.nombre_cliente,
    c.segmento,
    r.nombre_region
HAVING SUM(d.cantidad * d.precio_unitario * (1 - d.descuento)) > 2500.00
ORDER BY venta_neta_total DESC;

-- 3. SUBCONSULTA CORRELACIONADA PARA DETECTAR PRODUCTOS SOBRE EL PROMEDIO DE SU CATEGORÍA
SELECT
    p.id_producto,
    p.nombre_producto,
    p.categoria,
    p.precio_lista
FROM dim_productos AS p
WHERE p.precio_lista > (
    SELECT AVG(p2.precio_lista)
    FROM dim_productos AS p2
    WHERE p2.categoria = p.categoria
)
ORDER BY p.categoria, p.precio_lista DESC;
