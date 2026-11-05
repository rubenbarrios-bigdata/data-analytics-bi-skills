# Modelado Avanzado de Datos en Google Sheets para Business Intelligence

Google Sheets es frecuentemente la fuente primaria o capa de staging en proyectos de consultoría BI. Dominar sus fórmulas analíticas garantiza que los datos lleguen limpios y normalizados a Looker Studio.

---

## 1. Reglas Estrictas de Preparación Tabular (Tidy Data)
Para que los conectores de Looker Studio y BigQuery consuman una hoja sin errores:
1. **Fila 1 exclusiva para nombres de campos:** En minúsculas o formato PascalCase, sin tildes ni caracteres extraños (`fecha`, `cliente_id`, `monto_neto`).
2. **Prohibición de Celdas Combinadas (Merged Cells):** Rompen la cardinalidad de las filas.
3. **Consistencia de Tipos por Columna:** Si una columna es `Fecha`, ninguna celda puede contener texto como "Pendiente" o "N/A" (usar celdas vacías o fechas centinela coherentes).

---

## 2. Fórmulas Analíticas Clave

### A. Cruces de Datos Seguros (`INDEX/MATCH` & `XLOOKUP`)
*Reemplazo superior a `VLOOKUP` porque no se rompe si se insertan nuevas columnas en la tabla de búsqueda:*

```excel
=INDEX(MaestroClientes!B:B, MATCH(A2, MaestroClientes!A:A, 0))
```

*Sintaxis con `XLOOKUP` (si está habilitado en la hoja):*
```excel
=XLOOKUP(A2, MaestroClientes!A:A, MaestroClientes!B:B, "No encontrado", 0)
```

### B. El Poder de la Función `QUERY` (Pseudo-SQL en Sheets)
Permite filtrar, agrupar y ordenar datos directamente con sintaxis SQL:

```excel
=QUERY(
  Ventas!A1:H5000,
  "SELECT C, SUM(F), AVG(F), COUNT(A) 
   WHERE H = 'Completado' AND F > 0 
   GROUP BY C 
   ORDER BY SUM(F) DESC 
   LABEL C 'Categoría', SUM(F) 'Venta Total', AVG(F) 'Ticket Promedio', COUNT(A) 'Cant. Pedidos'",
  1
)
```

### C. Vectorización con `ARRAYFORMULA`
Aplica una lógica a toda la columna sin necesidad de arrastrar manualmente la fórmula, reduciendo peso y errores de mantenimiento:

```excel
=ARRAYFORMULA(IF(ROW(A:A)=1, "Margen Bruto", IF(ISBLANK(A:A), "", D:D - E:E)))
```

### D. Agregaciones Condicionales con Múltiples Criterios
```excel
=SUMIFS(Ventas!F:F, Ventas!B:B, "Buenos Aires", Ventas!A:A, ">=2026-01-01")
```

