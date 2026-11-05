"""
Plantilla de Modelado de Regresión con Scikit-Learn
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Programa: Talento Tech - Machine Learning para Negocios
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

def comparar_modelos_regresion():
    print("=" * 65)
    print("   COMPARATIVA DE MODELOS DE REGRESIÓN (PRECIOS)")
    print("=" * 65)

    np.random.seed(42)
    n = 400
    # Features: m2, dormitorios, antiguedad, distancia_centro_km
    m2 = np.random.uniform(40, 250, size=n)
    dormitorios = np.random.choice([1, 2, 3, 4], size=n)
    antiguedad = np.random.uniform(0, 50, size=n)
    distancia = np.random.uniform(1, 25, size=n)

    # Precio con relaciones lineales y no lineales
    precio = (
        1200 * m2 
        + 15000 * dormitorios 
        - 800 * antiguedad 
        - 2500 * distancia 
        + 50000 
        + np.random.normal(0, 15000, size=n)
    )

    X = pd.DataFrame({
        "m2": m2,
        "dormitorios": dormitorios,
        "antiguedad": antiguedad,
        "distancia_km": distancia
    })
    y = precio

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    # 1. Regresión Lineal con Escalado
    pipe_lr = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LinearRegression())
    ])
    pipe_lr.fit(X_train, y_train)
    y_pred_lr = pipe_lr.predict(X_test)

    # 2. Random Forest Regressor
    pipe_rf = Pipeline([
        ("model", RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42))
    ])
    pipe_rf.fit(X_train, y_train)
    y_pred_rf = pipe_rf.predict(X_test)

    def calcular_metricas(y_real, y_pred, nombre):
        r2 = r2_score(y_real, y_pred)
        mae = mean_absolute_error(y_real, y_pred)
        rmse = np.sqrt(mean_squared_error(y_real, y_pred))
        print(f"\n[+] Rendimiento: {nombre}")
        print(f"    - R² Score:              {r2:.4f}")
        print(f"    - Error Medio Abs (MAE): ${mae:,.2f}")
        print(f"    - Raíz Error Cuad (RMSE): ${rmse:,.2f}")

    calcular_metricas(y_test, y_pred_lr, "Regresión Lineal")
    calcular_metricas(y_test, y_pred_rf, "Random Forest Regressor")
    print("\n[OK] Modelos de regresión evaluados exitosamente.")

if __name__ == "__main__":
    comparar_modelos_regresion()

