# Guía de Análisis Estadístico y Exploratorio con Lenguaje R

Basado en el módulo de **Lenguaje R** del curso **Experto en Análisis y Visualización de Datos + IA** (*DataBoosters Academy*).

---

## 1. Estructuras Fundamentales en R

1. **Vectores (`c()`, `seq()`, indexación lógica):**
   ```r
   ventas <- c(1250.5, 980.0, 3400.75, 450.0, 2100.20, 5800.0)
   meses  <- c("Ene", "Feb", "Mar", "Abr", "May", "Jun")
   names(ventas) <- meses

   # Filtrado vectorial sin bucles (Ventas superiores a la media)
   ventas_altas <- ventas[ventas > mean(ventas)]
   ```

2. **DataFrames (`data.frame`) y Factores (`factor`):**
   ```r
   df_transacciones <- data.frame(
     id_orden  = 101:106,
     segmento  = factor(c("Corporativo", "Consumo", "Corporativo", "PyME", "Consumo", "Corporativo")),
     ventas    = ventas,
     descuento = c(0.05, 0.00, 0.10, 0.00, 0.08, 0.12),
     stringsAsFactors = FALSE
   )
   df_transacciones$venta_neta <- df_transacciones$ventas * (1 - df_transacciones$descuento)
   ```

---

## 2. Programación Funcional con la Familia `apply`

En R, el uso de la familia `apply` es el estándar profesional para transformar y resumir estructuras de datos de manera limpia y eficiente:

| Función | Entrada (`X`) | Salida | Caso de Uso Principal |
| :--- | :--- | :--- | :--- |
| **`apply(X, MARGIN, FUN)`** | Matriz o DataFrame numérico | Vector o Matriz | Calcular métricas por fila (`MARGIN = 1`) o por columna (`MARGIN = 2`). |
| **`lapply(X, FUN)`** | Lista o DataFrame (columnas) | Lista (`list`) | Aplicar una transformación o resumen a cada columna conservando estructura de lista. |
| **`sapply(X, FUN)`** | Lista o DataFrame (columnas) | Vector o Matriz nombrada | Igual que `lapply`, pero simplifica automáticamente el resultado a un vector o tabla. |
| **`tapply(X, INDEX, FUN)`** | Vector numérico + Factor(es) | Array / Tabla por grupo | Calcular promedios, sumas o cuantiles agrupados por categoría (equivalente a `GROUP BY`). |

### Ejemplos Prácticos de la Familia `apply`:
```r
# 1. apply: Resumen por columna de las variables numéricas
cols_numericas <- df_transacciones[, c("ventas", "descuento", "venta_neta")]
promedios_col  <- apply(cols_numericas, MARGIN = 2, FUN = mean, na.rm = TRUE)
desvios_col    <- apply(cols_numericas, MARGIN = 2, FUN = sd, na.rm = TRUE)

# 2. sapply: Verificar clase y cantidad de valores nulos por columna
tipos_datos <- sapply(df_transacciones, class)
conteo_na   <- sapply(df_transacciones, function(col) sum(is.na(col)))

# 3. tapply: Venta neta total y promedio agrupado por Segmento de Cliente
total_por_segmento <- tapply(df_transacciones$venta_neta, df_transacciones$segmento, sum)
media_por_segmento <- tapply(df_transacciones$venta_neta, df_transacciones$segmento, mean)
```

---

## 3. Visualización Exploratoria Personalizada en R (`hist` y `boxplot`)

```r
# Configurar lienzo de 1 fila y 2 columnas
par(mfrow = c(1, 2), mar = c(5, 4, 4, 2) + 0.1)

# 1. Histograma personalizado con línea de media y mediana
hist(
  df_transacciones$venta_neta,
  breaks = 10,
  col    = "#2B5B84",
  border = "white",
  main   = "Distribución de Ventas Netas",
  xlab   = "Venta Neta (USD)",
  ylab   = "Frecuencia"
)
abline(v = mean(df_transacciones$venta_neta), col = "#E63946", lwd = 2, lty = 2)

# 2. Boxplot comparativo por Segmento para detección de Outliers
boxplot(
  venta_neta ~ segmento,
  data   = df_transacciones,
  col    = c("#457B9D", "#A8DADC", "#1D3557"),
  main   = "Dispersión y Outliers por Segmento",
  xlab   = "Segmento de Cliente",
  ylab   = "Venta Neta (USD)",
  notch  = FALSE
)
```
