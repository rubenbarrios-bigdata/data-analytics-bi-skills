# Cheatsheet de Validación Cruzada y Optimización de Hiperparámetros

Estrategias para optimizar estimadores evitando el sobreajuste y evaluando rendimiento fuera de muestra.

---

## 1. Validación Cruzada Estratificada (`StratifiedKFold`)

Garantiza que la distribución porcentual de clases se mantenga idéntica en cada partición (*fold*).

```python
from sklearn.model_selection import StratifiedKFold, cross_val_score

cv_estratificado = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Evaluación con F1-score ponderado
scores = cross_val_score(
    modelo_pipeline,
    X_train,
    y_train,
    cv=cv_estratificado,
    scoring="f1"
)

print(f"F1 Promedio: {scores.mean():.3f} (+/- {scores.std():.3f})")
```

---

## 2. Ajuste Exhaustivo con `GridSearchCV`

Evalúa todas las combinaciones posibles en una cuadrícula discreta de parámetros:

```python
from sklearn.model_selection import GridSearchCV

# Definición de la grilla (usando el prefijo del paso del pipeline)
param_grid = {
    "classifier__n_estimators": [100, 200],
    "classifier__max_depth": [4, 6, 8],
    "classifier__min_samples_leaf": [2, 5]
}

grid_search = GridSearchCV(
    estimator=modelo_pipeline,
    param_grid=param_grid,
    cv=cv_estratificado,
    scoring="roc_auc",
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train, y_train)
print(f"Mejores Parámetros: {grid_search.best_params_}")
print(f"Mejor ROC-AUC en CV: {grid_search.best_score_:.3f}")
```

---

## 3. Búsqueda Aleatoria con `RandomizedSearchCV`

Ideal para espacios de búsqueda grandes con distribuciones continuas:

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint

param_dist = {
    "classifier__n_estimators": randint(50, 300),
    "classifier__max_depth": randint(3, 10),
    "classifier__min_samples_split": randint(2, 11)
}

random_search = RandomizedSearchCV(
    estimator=modelo_pipeline,
    param_distributions=param_dist,
    n_iter=20,
    cv=cv_estratificado,
    scoring="recall",
    random_state=42,
    n_jobs=-1
)

random_search.fit(X_train, y_train)
```

