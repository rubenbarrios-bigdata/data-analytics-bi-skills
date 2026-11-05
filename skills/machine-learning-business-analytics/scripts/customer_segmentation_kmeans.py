#!/usr/bin/env python3
"""
Segmentación de Clientes con K-Means Clustering
------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Programa: Talento Tech - Machine Learning para Negocios
Propósito: Segmentación no supervisada evaluando el Método del Codo
y Coeficiente de Silueta, aplicando StandardScaler mandatorio.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def segmentar_clientes_kmeans(
    df: pd.DataFrame,
    features: List[str],
    k_rango: range = range(2, 7)
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Estandariza datos, evalúa k óptimo y asigna etiquetas de clúster."""
    X = df[features].copy()

    # 1. Escalado Obligatorio (distancias euclidianas K-Means)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 2. Evaluación de Inercia y Silhouette Score
    metricas_k = []
    mejor_k = 2
    mejor_silueta = -1.0

    for k in k_rango:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        sil = silhouette_score(X_scaled, labels)
        inercia = km.inertia_
        metricas_k.append({"k": k, "inercia": round(inercia, 2), "silhouette": round(sil, 4)})

        if sil > mejor_silueta:
            mejor_silueta = sil
            mejor_k = k

    # 3. Modelo Final con el mejor k detectado
    modelo_final = KMeans(n_clusters=mejor_k, random_state=42, n_init=10)
    df_resultado = df.copy()
    df_resultado["cluster"] = modelo_final.fit_predict(X_scaled)

    # 4. Perfilado de Clústeres (Centroides y Medias de Negocio)
    perfiles = df_resultado.groupby("cluster")[features].mean().round(2).to_dict(orient="index")

    resumen = {
        "k_optimo_seleccionado": mejor_k,
        "mejor_silhouette_score": round(mejor_silueta, 4),
        "metricas_evaluacion_k": metricas_k,
        "perfiles_cluster": perfiles
    }

    return df_resultado, resumen

if __name__ == "__main__":
    np.random.seed(42)
    n = 300
    df_clientes = pd.DataFrame({
        "recencia_dias": np.random.randint(5, 120, size=n),
        "frecuencia_compras": np.random.poisson(lam=8, size=n) + 1,
        "monto_total_gastado": np.random.exponential(scale=350, size=n) + 50
    })

    _, resumen = segmentar_clientes_kmeans(
        df_clientes,
        features=["recencia_dias", "frecuencia_compras", "monto_total_gastado"]
    )

    print("=" * 65)
    print("   RESULTADOS DE SEGMENTACIÓN K-MEANS")
    print("=" * 65)
    print(f" Número óptimo de Clústeres (k): {resumen['k_optimo_seleccionado']}")
    print(f" Coeficiente de Silueta:        {resumen['mejor_silhouette_score']}")
    print("\n[+] Métricas por cada valor de k evaluado:")
    for m in resumen["metricas_evaluacion_k"]:
        print(f"  * k={m['k']} | Inercia: {m['inercia']:<10} | Silueta: {m['silhouette']}")

    print("\n[+] Perfiles de Negocio por Clúster:")
    for cl, valores in resumen["perfiles_cluster"].items():
        print(f"  * Clúster {cl}: Recencia {valores['recencia_dias']}d | Frecuencia {valores['frecuencia_compras']} | Gasto ${valores['monto_total_gastado']}")
    print("=" * 65)

