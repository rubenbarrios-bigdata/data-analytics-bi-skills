#!/usr/bin/env python3
"""
Pipeline de Entrenamiento de Clasificación Supervisada con Scikit-Learn
-----------------------------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Programa: Talento Tech - Machine Learning para Negocios
Propósito: Entrenar un modelo de clasificación con ColumnTransformer,
aislamiento estricto contra Data Leakage, validación cruzada y métricas de negocio.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score

def construir_y_evaluar_clasificador(
    df: pd.DataFrame,
    target_col: str,
    num_cols: list,
    cat_cols: list
) -> Tuple[Pipeline, Dict[str, Any]]:
    """Construye un pipeline anti-leakage y evalúa el rendimiento sobre test."""
    X = df[num_cols + cat_cols]
    y = df[target_col]

    # 1. Split Estratificado Train / Test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # 2. Preprocesamiento desacoplado con ColumnTransformer
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer([
        ("num", num_pipeline, num_cols),
        ("cat", cat_pipeline, cat_cols)
    ])

    # 3. Pipeline Integral (Preprocesador + Estimador)
    full_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42))
    ])

    # 4. Validación Cruzada Estratificada en Train
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(full_pipeline, X_train, y_train, cv=cv, scoring="roc_auc")

    # 5. Ajuste en Train y Evaluación Final en Test
    full_pipeline.fit(X_train, y_train)
    y_pred = full_pipeline.predict(X_test)
    y_proba = full_pipeline.predict_proba(X_test)[:, 1]

    metricas = {
        "cv_roc_auc_mean": round(float(cv_scores.mean()), 4),
        "cv_roc_auc_std": round(float(cv_scores.std()), 4),
        "test_f1_score": round(float(f1_score(y_test, y_pred)), 4),
        "test_roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, output_dict=True)
    }

    return full_pipeline, metricas

if __name__ == "__main__":
    # Simulación de dataset de abandono de clientes (Churn)
    np.random.seed(42)
    n = 600
    df_sim = pd.DataFrame({
        "edad": np.random.randint(20, 70, size=n),
        "antiguedad_meses": np.random.randint(1, 60, size=n),
        "monto_mensual": np.random.uniform(20.0, 150.0, size=n),
        "reclamos_soporte": np.random.poisson(lam=1.5, size=n),
        "tipo_contrato": np.random.choice(["Mensual", "Anual", "Dos Años"], size=n),
        "metodo_pago": np.random.choice(["Tarjeta", "Transferencia", "Efectivo"], size=n)
    })
    # Generar target sintético con correlación lógica
    score = (
        0.8 * (df_sim["tipo_contrato"] == "Mensual") 
        + 0.4 * df_sim["reclamos_soporte"] 
        - 0.03 * df_sim["antiguedad_meses"]
        + (df_sim["monto_mensual"] > 100) * 0.5
    )
    df_sim["churn"] = (score > score.quantile(0.75)).astype(int)

    pipeline, res = construir_y_evaluar_clasificador(
        df_sim,
        target_col="churn",
        num_cols=["edad", "antiguedad_meses", "monto_mensual", "reclamos_soporte"],
        cat_cols=["tipo_contrato", "metodo_pago"]
    )

    print("=" * 65)
    print("   EVALUACIÓN DEL PIPELINE DE CLASIFICACIÓN (CHURN)")
    print("=" * 65)
    print(f" ROC-AUC en Validación Cruzada: {res['cv_roc_auc_mean']} (+/- {res['cv_roc_auc_std']})")
    print(f" ROC-AUC en Test Out-of-Sample:  {res['test_roc_auc']}")
    print(f" F1-Score en Test:               {res['test_f1_score']}")
    print(f" Matriz de Confusión [[TN, FP], [FN, TP]]: {res['confusion_matrix']}")
    print("=" * 65)
