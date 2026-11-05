#!/usr/bin/env python3
"""
Generador y Validador de Sintaxis de Campos Calculados para Looker Studio
------------------------------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Propósito: Construir expresiones SQL/Calculadas compatibles con Looker Studio,
garantizando manejo seguro de división por cero y categorizaciones con CASE WHEN.
"""

from typing import List, Tuple

def generar_case_tier_segmentacion(
    nombre_campo_numerico: str,
    umbrales_etiquetas: List[Tuple[float, str]],
    etiqueta_default: str = "Base"
) -> str:
    """Genera una sentencia CASE WHEN para segmentación en Looker Studio."""
    lineas = ["CASE"]
    for umbral, etiqueta in sorted(umbrales_etiquetas, key=lambda x: x[0], reverse=True):
        lineas.append(f"  WHEN {nombre_campo_numerico} >= {umbral} THEN '{etiqueta}'")
    lineas.append(f"  ELSE '{etiqueta_default}'")
    lineas.append("END")
    return "\n".join(lineas)

def generar_ratio_seguro(
    numerador: str,
    denominador: str,
    formato_porcentaje: bool = True
) -> str:
    """Evita errores de división por cero en Looker Studio."""
    multiplicador = " * 100" if formato_porcentaje else ""
    return f"CASE WHEN {denominador} IS NULL OR {denominador} = 0 THEN 0 ELSE ({numerador} / {denominador}){multiplicador} END"

if __name__ == "__main__":
    print("=== Ejemplos de Campos Calculados para Looker Studio ===")
    
    # Ejemplo 1: Segmentación de Clientes por Ticket Promedio
    umbrales = [(1000.0, "Tier 1 - VIP / Alto Valor"), (500.0, "Tier 2 - Medio"), (100.0, "Tier 3 - Ocasional")]
    print("\n1. Campo: 'Segmento Cliente':")
    print(generar_case_tier_segmentacion("Monto_Venta", umbrales, "Tier 4 - Micro"))

    # Ejemplo 2: Tasa de Margen Seguro
    print("\n2. Campo: 'Margen Bruto Pct':")
    print(generar_ratio_seguro("SUM(Ingreso_Neto - Costo_Total)", "SUM(Ingreso_Neto)"))

