#!/usr/bin/env python3
"""
Perfilador Estadístico Descriptivo para Consultoría de BI
---------------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Programa: Talento Tech - Consultoría en Business Intelligence
Propósito: Calcular medidas de tendencia central, dispersión, percentiles
y detectar anomalías/outliers con la regla de Tukey para validar calidad
de datos antes de visualizarlos en Looker Studio o presentarlos a directivos.
"""

import math
from typing import List, Dict, Any, Tuple

def calcular_estadisticas_descriptivas(valores: List[float]) -> Dict[str, Any]:
    """Calcula el perfil estadístico completo sin dependencias externas pesadas."""
    n = len(valores)
    if n == 0:
        return {"error": "Lista vacía"}

    datos = sorted(valores)

    # 1. Medidas de Tendencia Central
    media = sum(datos) / n
    if n % 2 == 1:
        mediana = datos[n // 2]
    else:
        mediana = (datos[n // 2 - 1] + datos[n // 2]) / 2.0

    # 2. Medidas de Dispersión
    varianza = sum((x - media) ** 2 for x in datos) / (n - 1) if n > 1 else 0.0
    desv_estandar = math.sqrt(varianza)
    cv = (desv_estandar / media * 100) if media != 0 else 0.0

    # 3. Percentiles y Rango Intercuartílico (IQR)
    def percentil(p: float) -> float:
        k = (n - 1) * p
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return datos[int(k)]
        d0 = datos[int(f)] * (c - k)
        d1 = datos[int(c)] * (k - f)
        return d0 + d1

    q1 = percentil(0.25)
    q3 = percentil(0.75)
    iqr = q3 - q1
    p90 = percentil(0.90)

    # 4. Detección de Outliers (Regla de Tukey)
    lim_inferior = q1 - 1.5 * iqr
    lim_superior = q3 + 1.5 * iqr
    outliers = [x for x in datos if x < lim_inferior or x > lim_superior]

    # 5. Sesgo cualitativo (Asimetría)
    diferencia_media_mediana = media - mediana
    if abs(diferencia_media_mediana) < 0.05 * desv_estandar:
        sesgo = "Simétrica / Distribución normal aproximada"
    elif media > mediana:
        sesgo = "Asimetría Positiva (Sesgo a la derecha - Ojo con la media, usar Mediana)"
    else:
        sesgo = "Asimetría Negativa (Sesgo a la izquierda - Ojo con la media, usar Mediana)"

    return {
        "conteo_registros": n,
        "minimo": datos[0],
        "maximo": datos[-1],
        "media": round(media, 2),
        "mediana": round(mediana, 2),
        "desviacion_estandar": round(desv_estandar, 2),
        "coeficiente_variacion_pct": round(cv, 2),
        "cuartil_1_p25": round(q1, 2),
        "cuartil_3_p75": round(q3, 2),
        "iqr": round(iqr, 2),
        "percentil_90": round(p90, 2),
        "limite_outlier_inferior": round(lim_inferior, 2),
        "limite_outlier_superior": round(lim_superior, 2),
        "total_outliers": len(outliers),
        "outliers_detectados": [round(x, 2) for x in outliers],
        "diagnostico_distribucion": sesgo
    }

def imprimir_informe_consultoria(metric_name: str, stats: Dict[str, Any]):
    print("=" * 65)
    print(f"   INFORME DE PROFILING ESTADÍSTICO: {metric_name.upper()}")
    print("=" * 65)
    print(f" Registros Analizados:        {stats['conteo_registros']}")
    print(f" Mínimo / Máximo:             ${stats['minimo']} / ${stats['maximo']}")
    print(f" Media Aritmética:            ${stats['media']}")
    print(f" Mediana (Métrica Robusta):   ${stats['mediana']}")
    print(f" Desviación Estándar (Sigma): ${stats['desviacion_estandar']}")
    print(f" Coeficiente de Variación:    {stats['coeficiente_variacion_pct']}%")
    print(f" Rango Intercuartílico (IQR): ${stats['iqr']} (Q1: ${stats['cuartil_1_p25']} - Q3: ${stats['cuartil_3_p75']})")
    print(f" Diagnóstico Distribución:    {stats['diagnostico_distribucion']}")
    print(f" Outliers Detectados:         {stats['total_outliers']} registros {stats['outliers_detectados']}")
    print("=" * 65)

if __name__ == "__main__":
    # Simulación de tickets de venta con sesgo positivo y outliers
    datos_muestra = [25.0, 30.0, 28.5, 32.0, 35.0, 27.0, 31.0, 33.0, 29.0, 34.0, 185.0, 420.0]
    reporte = calcular_estadisticas_descriptivas(datos_muestra)
    imprimir_informe_consultoria("Ticket de Venta", reporte)

