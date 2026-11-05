#!/usr/bin/env python3
"""
Auditor de Costos y Estimador FinOps para BigQuery y dbt
--------------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Propósito: Calcular el costo monetario en USD de consultas en BigQuery
a partir de bytes procesados, proyectando ahorros por particionado/clustering.
"""

from typing import Dict, Any

# Tarifa estándar de BigQuery On-Demand por Terabyte procesado
PRECIO_POR_TB_USD = 6.25
BYTES_EN_TB = 1024 ** 4

def calcular_costo_consulta_bigquery(bytes_escaneados: int) -> Dict[str, Any]:
    """Calcula el costo en USD y gigabytes a partir de los bytes reportados."""
    gigabytes = bytes_escaneados / (1024 ** 3)
    terabytes = bytes_escaneados / BYTES_EN_TB
    costo_usd = terabytes * PRECIO_POR_TB_USD

    return {
        "bytes_totales": bytes_escaneados,
        "gigabytes_escaneados": round(gigabytes, 3),
        "terabytes_escaneados": round(terabytes, 6),
        "costo_estimado_usd": round(costo_usd, 4)
    }

def simular_ahorro_particionado(
    bytes_sin_particion: int,
    pct_poda_particion: float = 0.90,
    consultas_mensuales: int = 300
) -> Dict[str, Any]:
    """Simula el impacto de FinOps al aplicar partition_by y cluster_by en dbt."""
    costo_query_full = calcular_costo_consulta_bigquery(bytes_sin_particion)["costo_estimado_usd"]
    bytes_optimizados = int(bytes_sin_particion * (1 - pct_poda_particion))
    costo_query_opt = calcular_costo_consulta_bigquery(bytes_optimizados)["costo_estimado_usd"]

    gasto_mensual_sin_opt = costo_query_full * consultas_mensuales
    gasto_mensual_opt = costo_query_opt * consultas_mensuales
    ahorro_mensual_usd = gasto_mensual_sin_opt - gasto_mensual_opt

    return {
        "costo_por_query_sin_opt_usd": costo_query_full,
        "costo_por_query_opt_usd": costo_query_opt,
        "gasto_mensual_sin_opt_usd": round(gasto_mensual_sin_opt, 2),
        "gasto_mensual_opt_usd": round(gasto_mensual_opt, 2),
        "ahorro_mensual_usd": round(ahorro_mensual_usd, 2),
        "porcentaje_ahorro": round(pct_poda_particion * 100, 1)
    }

if __name__ == "__main__":
    print("=" * 65)
    print("   SIMULADOR FINOPS BIGQUERY: TABLA DE HECHOS RETAIL")
    print("=" * 65)
    # Simulación de tabla histórica de retail de 250 GB
    bytes_tabla_completa = 250 * (1024 ** 3)
    res = simular_ahorro_particionado(bytes_tabla_completa, pct_poda_particion=0.92, consultas_mensuales=450)

    print(f" Tamaño de la Tabla Escaneada: 250.0 GB")
    print(f" Costo por Query Sin Partición: ${res['costo_por_query_sin_opt_usd']} USD")
    print(f" Costo por Query con Partition + Cluster: ${res['costo_por_query_opt_usd']} USD")
    print(f"\n[+] Proyección Mensual (450 refrescos de dashboards Power BI):")
    print(f"  * Gasto sin optimizar: ${res['gasto_mensual_sin_opt_usd']} USD / mes")
    print(f"  * Gasto optimizado:     ${res['gasto_mensual_opt_usd']} USD / mes")
    print(f"  * Ahorro neto FinOps:   ${res['ahorro_mensual_usd']} USD / mes ({res['porcentaje_ahorro']}% reducción)")
    print("=" * 65)

