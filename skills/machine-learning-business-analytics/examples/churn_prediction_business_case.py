"""
Caso de Negocio: Predicción de Abandono de Clientes (Churn) y ROI Empresarial
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Programa: Talento Tech - Machine Learning para Negocios
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report

def simular_impacto_financiero_churn():
    print("=" * 65)
    print("   MODELO DE IMPACTO ECONÓMICO: RETENCIÓN PREDICTIVA (CHURN)")
    print("=" * 65)

    # Parámetros del Negocio
    costo_campana_retencion = 25.0   # Costo de contactar y ofrecer descuento ($ USD)
    lrv_cliente_salvado = 300.0       # Valor de vida residual salvado por cliente retenido
    tasa_exito_retencion = 0.60       # 60% de los clientes en riesgo aceptan la oferta y se quedan

    # Generación de datos sintéticos
    np.random.seed(42)
    n = 1000
    X = np.random.randn(n, 5)
    # Target: 1 = Churn (15% tasa base), 0 = Permanece
    prob = 1 / (1 + np.exp(-(X[:, 0] * 1.2 - X[:, 1] * 0.8 - 1.5)))
    y = (prob > 0.5).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

    modelo = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    # Cálculo del ROI
    # Casos contactados = Predichos como Churn (TP + FP)
    total_contactados = tp + fp
    costo_total_campana = total_contactados * costo_campana_retencion

    # Clientes efectivamente retenidos = TP * tasa_exito
    clientes_salvados = tp * tasa_exito_retencion
    ingreso_bruto_salvado = clientes_salvados * lrv_cliente_salvado
    beneficio_neto = ingreso_bruto_salvado - costo_total_campana
    roi = (beneficio_neto / costo_total_campana * 100) if costo_total_campana > 0 else 0

    print(f"\n[1] Métricas de Matriz de Confusión en Test ({len(y_test)} clientes):")
    print(f"    - Clientes en riesgo detectados (TP): {tp}")
    print(f"    - Falsas alarmas / Ineficiencia (FP): {fp}")
    print(f"    - Fugas no detectadas (FN crítico):   {fn}")
    print(f"    - Clientes fieles correctos (TN):     {tn}")

    print("\n[2] Impacto Financiero Proyectado:")
    print(f"    - Costo de la Campaña de Retención: ${costo_total_campana:,.2f} USD")
    print(f"    - Clientes Rescatados Estimados:    {clientes_salvados:.1f} clientes")
    print(f"    - Ingresos Brutos Salvados:         ${ingreso_bruto_salvado:,.2f} USD")
    print(f"    - Beneficio Neto de la Campaña:     ${beneficio_neto:,.2f} USD")
    print(f"    - Retorno de Inversión (ROI):       {roi:.1f}%")
    print("\n[OK] Simulación de impacto comercial completada.")

if __name__ == "__main__":
    simular_impacto_financiero_churn()

