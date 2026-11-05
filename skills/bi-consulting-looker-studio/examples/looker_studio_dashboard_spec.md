# Especificación Técnica de Dashboard Ejecutivo en Looker Studio

## 1. Parámetros del Lienzo (Canvas Settings)
- **Resolución:** 1366 x 900 px (Formato panorámico estándar de monitores y laptops ejecutivas).
- **Tema y Paleta:**
  - Fondo de lienzo: `#F8F9FA` (Gris claro de descanso visual).
  - Fondo de contenedores / tarjetas: `#FFFFFF` (Blanco puro con radio de borde de 8px y borde `#E0E0E0`).
  - Color Primario (Datos principales): `#1A73E8` (Azul corporativo Google).
  - Color Secundario (Comparativas): `#5F6368` (Gris medio).
  - Acentos semánticos: Verde `#0D8A56` (Incremento favorable) y Rojo `#D93025` (Desviación desfavorable).
  - Tipografía: Roboto / Inter (Sans-Serif ejecutiva).

---

## 2. Distribución y Grilla (Layout por Cuadrantes)

```
+-------------------------------------------------------------------------------+
| HEADER (Logo corporativo, Título del Dashboard, Filtro Fecha, Filtro Región)  |
+-------------------------------------------------------------------------------+
| [ KPI 1: Ingresos ]   [ KPI 2: Ticket Medio ]   [ KPI 3: Clientes ]  [ KPI 4: CR ] |
+-------------------------------------------------------------------------------+
|                                       |                                       |
|  GRÁFICO DE TENDENCIA TEMPORAL        |  PARETO DE PRODUCTOS (BARRAS HORIZ.)   |
|  (Evolución Ingresos Mensuales vs AA) |  (Top 10 SKUs por Facturación)        |
|                                       |                                       |
+-------------------------------------------------------------------------------+
|                                       |                                       |
|  DISTRIBUCIÓN POR CANAL (DONUT 3 CAT) |  TABLA DETALLADA CON BARRAS DE MAPA   |
|  (Orgánico vs Pago vs Directo)        |  (Rendimiento por Sucursal / Vendedor)|
|                                       |                                       |
+-------------------------------------------------------------------------------+
```

---

## 3. Especificación de Objetos Visuales

### Cuadrante 1: Fila Superior de KPIs (Scorecards con Variación)
1. **KPI 1 - Ingresos Totales:**
   - Métrica: `SUM(Monto_Neto)`
   - Período de comparación: Año anterior (Mismo período).
2. **KPI 2 - Ticket Promedio:**
   - Métrica: `AVG(Monto_Neto)` o `SUM(Monto_Neto) / COUNT_DISTINCT(Orden_ID)`
3. **KPI 3 - Total Clientes Únicos:**
   - Métrica: `COUNT_DISTINCT(Cliente_ID)`
4. **KPI 4 - Margen Operativo %:**
   - Campo Calculado: `(SUM(Monto_Neto) - SUM(Costo_Total)) / SUM(Monto_Neto)`

### Cuadrante 2: Análisis Temporal y Comparativo
- **Gráfico de Líneas:** Eje X `Fecha (Año-Mes)`, Métrica `Ingresos`, Dimensión de desglose: Ninguna (mantener limpia la línea), Métrica secundaria: `Período anterior`.
- **Gráfico de Barras Horizontales:** Dimensión `Nombre_Producto`, Métrica `Ingresos`, Ordenar descendente, Mostrar máximo 10 filas.

