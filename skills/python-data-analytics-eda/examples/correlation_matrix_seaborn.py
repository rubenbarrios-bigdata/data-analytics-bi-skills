"""
Ejemplo de Matriz de Correlación Triangular con Seaborn y Matplotlib
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def graficar_matriz_correlacion(df: pd.DataFrame, titulo: str = "Matriz de Correlación de Pearson"):
    cols_num = df.select_dtypes(include=[np.number]).columns
    matriz_corr = df[cols_num].corr(method="pearson")

    # Máscara booleana para ocultar el triángulo superior redundante
    mascara = np.triu(np.ones_like(matriz_corr, dtype=bool))

    plt.figure(figsize=(9, 7), dpi=120)
    sns.set_theme(style="white")

    # Mapa de calor divergente centrado en cero
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    sns.heatmap(
        matriz_corr,
        mask=mascara,
        cmap=cmap,
        vmax=1.0,
        vmin=-1.0,
        center=0,
        square=True,
        linewidths=.5,
        cbar_kws={"shrink": .8, "label": "Coeficiente r"},
        annot=True,
        fmt=".2f"
    )

    plt.title(titulo, fontsize=14, weight="bold", pad=15)
    plt.tight_layout()
    # Guardar en disco sin bloquear la consola
    plt.savefig("correlacion_triangular.png")
    plt.close()
    print("[OK] Gráfico de correlación guardado exitosamente como 'correlacion_triangular.png'.")

if __name__ == "__main__":
    np.random.seed(101)
    df_ejemplo = pd.DataFrame({
        "ventas": np.random.normal(1000, 200, 100),
        "gasto_marketing": np.random.normal(300, 50, 100),
        "descuento_pct": np.random.uniform(5, 30, 100),
        "margen_neto": np.random.normal(250, 40, 100)
    })
    # Forzar relación positiva
    df_ejemplo["ventas"] += df_ejemplo["gasto_marketing"] * 2.5
    graficar_matriz_correlacion(df_ejemplo)

