# Reglas de Sintaxis y Compilación TMDL (Tabular Model Definition Language)

TMDL es el lenguaje declarativo y legible por humanos diseñado por Microsoft para definir modelos tabulares de Analysis Services y Power BI.

---

## 1. La Regla de Oro: Codificación UTF-8 sin BOM

- **El Problema:** Muchos editores en Windows (como Bloc de notas antiguo o PowerShell al usar `Out-File` sin flags) agregan automáticamente un encabezado de 3 bytes conocido como **BOM** (`0xEF, 0xBB, 0xBF`).
- **El Síntoma:** Power BI Desktop arroja un error genérico de compilación al cargar el modelo semántico: `The input stream is not a valid TMDL document`.
- **La Solución:** Asegurarse de que el archivo sea guardado estrictamente en **UTF-8 sin BOM** (en Python: `open(filepath, 'w', encoding='utf-8')`).

---

## 2. Delimitación de Expresiones Multilínea con Triple Backtick

En TMDL, las expresiones DAX de una sola línea pueden escribirse directamente:
```tmdl
measure 'Total Ventas' = SUM(Ventas[Importe])
    formatString: "$ #,##0.00"
```

Sin embargo, cuando la medida tiene **múltiples líneas, variables (`VAR`/`RETURN`) o código HTML/SVG**, debe delimitarse obligatoriamente con **exactamente tres comillas invertidas**:

```tmdl
measure 'KPI Venta y Diagnóstico' = ```
    VAR _VentaActual = SUM(Ventas[ImporteNeto])
    VAR _VentaPrevia = CALCULATE(SUM(Ventas[ImporteNeto]), DATEADD(Calendario[Fecha], -1, MONTH))
    VAR _VarPct = DIVIDE(_VentaActual - _VentaPrevia, _VentaPrevia)
    RETURN
        "<div class='kpi-card'>" & FORMAT(_VentaActual, "$ #,##0") & "</div>"
    ```
    formatString: ""
    displayFolder: "Tarjetas Ejecutivas"
```

---

## 3. Jerarquía e Indentación por Tabulaciones

- TMDL utiliza **tabulaciones reales (`\t`)**, no espacios sueltos, para denotar anidamiento.
- Ejemplo de jerarquía de tabla:
```tmdl
table Clientes
	lineageTag: a1b2c3d4-e5f6-7890

	column ClienteID
		dataType: int64
		sourceColumn: customer_id
		summarizeBy: none

	column NombreCompleto
		dataType: string
		sourceColumn: full_name
		summarizeBy: none

	measure 'Total Clientes' = DISTINCTCOUNT(Clientes[ClienteID])
		formatString: "#,##0"
```

