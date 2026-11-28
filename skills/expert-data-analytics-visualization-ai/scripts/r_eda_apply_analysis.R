# ==============================================================================
# Script de Análisis Estadístico y Exploratorio en R (Vectores, DataFrames y apply)
# Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
# Certificación: Experto en Análisis y Visualización de Datos + IA (DataBoosters)
# ==============================================================================

# 1. Creación de Vectores y DataFrame Analítico
id_transaccion <- 1:12
categoria <- factor(c(
  "Tecnología", "Mobiliario", "Oficina", "Tecnología",
  "Oficina", "Mobiliario", "Tecnología", "Oficina",
  "Mobiliario", "Tecnología", "Oficina", "Tecnología"
))
ventas_usd <- c(1450.0, 620.5, 130.0, 2100.0, 95.0, 840.0, 1780.0, 210.0, 510.0, 3200.0, 165.0, 1950.0)
costo_usd  <- c(870.0,  430.0, 78.0,  1200.0, 60.0, 590.0, 1050.0, 125.0, 360.0, 1850.0, 98.0,  1150.0)
dias_envio <- c(2, 4, 3, 1, 5, 4, 2, 3, 6, 1, 3, 2)

df_ventas <- data.frame(
  id_transaccion = id_transaccion,
  categoria      = categoria,
  ventas_usd     = ventas_usd,
  costo_usd      = costo_usd,
  dias_envio     = dias_envio
)

# Cálculo vectorial de Utilidad y Margen %
df_ventas$utilidad_usd <- df_ventas$ventas_usd - df_ventas$costo_usd
df_ventas$margen_pct   <- round((df_ventas$utilidad_usd / df_ventas$ventas_usd) * 100, 2)

# 2. Uso de la Familia apply (apply, lapply, sapply, tapply)
metricas_mat <- df_ventas[, c("ventas_usd", "costo_usd", "utilidad_usd", "margen_pct", "dias_envio")]

# Media y Desviación Estándar por columna con apply()
medias_columnas  <- apply(metricas_mat, MARGIN = 2, FUN = mean)
desvios_columnas <- apply(metricas_mat, MARGIN = 2, FUN = sd)

# Verificación de tipos y nulos con sapply()
estructura_tipos <- sapply(df_ventas, class)
conteo_nulos     <- sapply(df_ventas, function(x) sum(is.na(x)))

# Agregación por categoría con tapply() (equivalente a GROUP BY en SQL)
ventas_por_cat   <- tapply(df_ventas$ventas_usd, df_ventas$categoria, sum)
margen_medio_cat <- tapply(df_ventas$margen_pct, df_ventas$categoria, mean)

cat("=== RESUMEN ESTADÍSTICO EN R (FAMILIA APPLY) ===\n")
print(round(medias_columnas, 2))
cat("\n=== VENTAS TOTALES POR CATEGORÍA (TAPPLY) ===\n")
print(ventas_por_cat)

# 3. Generación de Gráficos Personalizados (Histograma y Boxplot)
png("r_eda_distribucion_ventas.png", width = 1200, height = 600, res = 120)
par(mfrow = c(1, 2), mar = c(5, 4, 4, 2) + 0.1)

hist(
  df_ventas$ventas_usd,
  breaks = 6,
  col    = "#1D3557",
  border = "white",
  main   = "Histograma de Ventas (USD)",
  xlab   = "Monto de Venta (USD)",
  ylab   = "Frecuencia de Órdenes"
)
abline(v = mean(df_ventas$ventas_usd), col = "#E63946", lwd = 2, lty = 2)

boxplot(
  ventas_usd ~ categoria,
  data = df_ventas,
  col  = c("#A8DADC", "#457B9D", "#1D3557"),
  main = "Boxplot de Ventas por Categoría",
  xlab = "Categoría de Producto",
  ylab = "Ventas (USD)"
)
dev.off()
