#!/usr/bin/env python3
"""
Pipeline de Limpieza y Curación de Datos con Pandas
---------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Propósito: Aplicar transformaciones analíticas reproducibles: tipado,
imputación robusta, tratamiento de outliers y deduplicación.
"""

import pandas as pd
import numpy as np
from typing import List, Optional

def limpiar_y_curar_dataset(
    df: pd.DataFrame,
    cols_fechas: Optional[List[str]] = None,
    cols_imputar_mediana: Optional[List[str]] = None,
    cols_imputar_moda: Optional[List[str]] = None,
    limitar_outliers_iqr: Optional[List[str]] = None
) -> pd.DataFrame:
    """Aplica transformaciones de limpieza retornando una copia curada."""
    df_clean = df.copy()

    # 1. Eliminación de Duplicados
    df_clean = df_clean.drop_duplicates()

    # 2. Parseo y tipado de Fechas
    if cols_fechas:
        for c in cols_fechas:
            if c in df_clean.columns:
                df_clean[c] = pd.to_datetime(df_clean[c], errors="coerce")

    # 3. Imputación con Mediana (para variables numéricas sesgadas)
    if cols_imputar_mediana:
        for c in cols_imputar_mediana:
            if c in df_clean.columns and df_clean[c].isnull().any():
                mediana = df_clean[c].median()
                df_clean[c] = df_clean[c].fillna(mediana)

    # 4. Imputación con Moda (para variables categóricas)
    if cols_imputar_moda:
        for c in cols_imputar_moda:
            if c in df_clean.columns and df_clean[c].isnull().any():
                moda = df_clean[c].mode().iloc[0]
                df_clean[c] = df_clean[c].fillna(moda)

    # 5. Capping de Outliers con IQR (Winsorización de Tukey)
    if limitar_outliers_iqr:
        for c in limitar_outliers_iqr:
            if c in df_clean.columns:
                q1 = df_clean[c].quantile(0.25)
                q3 = df_clean[c].quantile(0.75)
                iqr = q3 - q1
                lim_inf = q1 - 1.5 * iqr
                lim_sup = q3 + 1.5 * iqr
                df_clean[c] = df_clean[c].clip(lower=lim_inf, upper=lim_sup)

    return df_clean

if __name__ == "__main__":
    df_raw = pd.DataFrame({
        "fecha": ["2026-01-01", "2026-01-02", "invalido", "2026-01-04"],
        "precio": [10.0, np.nan, 15.0, 500.0],  # 500 es un outlier
        "sucursal": ["Centro", "Centro", None, "Norte"]
    })
    df_curado = limpiar_y_curar_dataset(
        df_raw,
        cols_fechas=["fecha"],
        cols_imputar_mediana=["precio"],
        cols_imputar_moda=["sucursal"],
        limitar_outliers_iqr=["precio"]
    )
    print("Dataset Curado Exitosamente:")
    print(df_curado)

