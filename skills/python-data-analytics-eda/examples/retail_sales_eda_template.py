"""
Plantilla Completa de Informe EDA para Negocio Retail
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Programa: Talento Tech - Especialización en Data Analytics
"""

import pandas as pd
import numpy as np

def ejecutar_eda_retail(ruta_csv: str = None) -> pd.DataFrame:
    print("=" * 65)
    print("   INFORME EJECUTIVO EDA: RETAIL STORE PERFORMANCE")
    print("=" * 65)

    # 1. Carga de datos (con fallback a dataset simulado si no se pasa archivo)
    if ruta_csv:
        df = pd.read_csv(ruta_csv)
    else:
        np.random.seed(42)
        n = 500
        fechas = pd.date_range(start="2026-01-01", periods=n, freq="D")
        df = pd.DataFrame({
            "fecha": fechas,
            "region": np.random.choice(["CABA", "GBA Norte", "GBA Sur", "Córdoba", "Rosario"], size=n),
            "categoria": np.random.choice(["Electro", "Moda", "Alimentos", "Hogar"], size=n),
            "unidades": np.random.randint(1, 15, size=n),
            "ticket_monto": np.random.exponential(scale=120, size=n) + 20,
            "satisfaccion_cliente": np.random.choice([3, 4, 5, np.nan], size=n, p=[0.1, 0.4, 0.45, 0.05])
        })

    # 2. Resumen Univariado
    print(f"\n[1] Muestra Total: {len(df)} transacciones analizadas.")
    print(f"    - Ticket Medio:    ${df['ticket_monto'].mean():.2f}")
    print(f"    - Ticket Mediano:  ${df['ticket_monto'].median():.2f}")
    print(f"    - Asimetría Skew:   {df['ticket_monto'].skew():.2f} (Sesgo positivo notable)")

    # 3. Agrupación Bivariada: Rendimiento por Región y Categoría
    agrupado = df.groupby("region").agg(
        ventas_totales=("ticket_monto", "sum"),
        ticket_promedio=("ticket_monto", "mean"),
        unidades_totales=("unidades", "sum")
    ).sort_values(by="ventas_totales", ascending=False)

    print("\n[2] Ranking de Ventas por Región:")
    print(agrupado.to_string())

    # 4. Tabla Pivote de Ventas Totales ($)
    pivote = pd.pivot_table(
        df,
        values="ticket_monto",
        index="region",
        columns="categoria",
        aggfunc="sum",
        fill_value=0
    )
    print("\n[3] Matriz de Facturación (Región x Categoría):")
    print(pivote.to_string())

    print("\n[OK] Análisis EDA ejecutado con éxito.")
    return df

if __name__ == "__main__":
    ejecutar_eda_retail()
