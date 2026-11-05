#!/usr/bin/env python3
"""
Perfilador Automatizado de EDA (Exploratory Data Analysis)
---------------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Programa: Talento Tech - Especialización en Data Analytics
Propósito: Ejecutar una auditoría estadística exploratoria exhaustiva
sobre cualquier dataset en formato CSV o DataFrame de Pandas.
"""

import sys
import pandas as pd
import numpy as np
from typing import Dict, Any

def auditar_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Genera un diagnóstico integral univariado, de nulos y correlación."""
    total_filas, total_columnas = df.shape

    # 1. Auditoría de Valores Nulos
    nulos = df.isnull().sum()
    pct_nulos = (nulos / total_filas * 100).round(2)
    reporte_nulos = pd.DataFrame({"nulos": nulos, "porcentaje": pct_nulos})
    columnas_con_nulos = reporte_nulos[reporte_nulos["nulos"] > 0].to_dict(orient="index")

    # 2. Duplicados
    total_duplicados = int(df.duplicated().sum())

    # 3. Resumen Numérico Extendido (con Asimetría)
    cols_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    resumen_numerico = {}
    if cols_numericas:
        desc = df[cols_numericas].describe().T
        skew = df[cols_numericas].skew().round(2)
        desc["skewness"] = skew
        resumen_numerico = desc[["mean", "std", "min", "50%", "max", "skewness"]].to_dict(orient="index")

    # 4. Resumen Categórico
    cols_categoricas = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    resumen_categorico = {}
    for col in cols_categoricas:
        resumen_categorico[col] = {
            "valores_unicos": int(df[col].nunique()),
            "top_valor": df[col].mode().iloc[0] if not df[col].empty else None
        }

    # 5. Matriz de Correlación de Pearson
    correlaciones = {}
    if len(cols_numericas) > 1:
        correlaciones = df[cols_numericas].corr(method="pearson").round(3).to_dict()

    return {
        "dimensiones": {"filas": total_filas, "columnas": total_columnas},
        "duplicados": total_duplicados,
        "columnas_con_nulos": columnas_con_nulos,
        "resumen_numerico": resumen_numerico,
        "resumen_categorico": resumen_categorico,
        "matriz_correlacion": correlaciones
    }

def imprimir_reporte_eda(resultados: Dict[str, Any]):
    print("=" * 65)
    print("   REPORTE DE AUDITORÍA EXPLORATORIA (EDA)")
    print("=" * 65)
    dims = resultados["dimensiones"]
    print(f" Dimensiones del Dataset:    {dims['filas']} filas x {dims['columnas']} columnas")
    print(f" Registros Duplicados:       {resultados['duplicados']}")
    
    print("\n[+] Columnas con Valores Faltantes:")
    if resultados["columnas_con_nulos"]:
        for col, info in resultados["columnas_con_nulos"].items():
            print(f"  * {col}: {info['nulos']} nulos ({info['porcentaje']}%)")
    else:
        print("  * Ninguna (Dataset 100% completo).")

    print("\n[+] Resumen Estadístico de Variables Numéricas:")
    for col, metricas in resultados["resumen_numerico"].items():
        print(f"  * {col:<18} | Media: {metricas['mean']:<8.2f} | Mediana: {metricas['50%']:<8.2f} | Skew: {metricas['skewness']:<5}")

    print("\n[+] Resumen de Variables Categóricas:")
    for col, info in resultados["resumen_categorico"].items():
        print(f"  * {col:<18} | Únicos: {info['valores_unicos']:<4} | Moda: {info['top_valor']}")
    print("=" * 65)

if __name__ == "__main__":
    # Generación de dataset sintético de prueba
    np.random.seed(42)
    n = 100
    df_prueba = pd.DataFrame({
        "id": range(1, n + 1),
        "categoria": np.random.choice(["Electrónica", "Indumentaria", "Hogar"], size=n),
        "precio": np.random.exponential(scale=50, size=n) + 10,
        "ventas_unidades": np.random.randint(1, 20, size=n),
        "satisfaccion_score": np.random.uniform(1.0, 5.0, size=n)
    })
    # Introducir algunos nulos para probar la detección
    df_prueba.loc[5:8, "precio"] = np.nan

    resultado = auditar_dataframe(df_prueba)
    imprimir_reporte_eda(resultado)
