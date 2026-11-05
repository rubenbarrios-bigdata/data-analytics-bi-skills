# Arquitectura de Scikit-Learn Pipelines y Prevención de Data Leakage

El **Data Leakage** (fuga de datos) ocurre cuando información del conjunto de prueba o del futuro se introduce inadvertidamente en el entrenamiento del modelo. Genera modelos que parecen tener un 95% de precisión en los tests locales, pero colapsan en producción.

---

## 1. El Peligro del Flujo Tradicional sin Pipeline

```
❌ FLUJO VULNERABLE:
Dataset Completo ---> [SimpleImputer / StandardScaler] ---> train_test_split ---> Model.fit()
                        ^
      ¡PELIGRO! La media y desviación estándar de TEST
      fueron calculadas y filtradas dentro de TRAIN.
```

```
 FLUJO INMUNE CON PIPELINE:
Dataset Completo ---> train_test_split(X, y)
                            |
           +----------------+----------------+
           |                                 |
       [X_train]                         [X_test]
           |                                 |
           v                                 v
   Pipeline.fit(X_train)            Pipeline.predict(X_test)
           |                                 |
(Aprende medias de TRAIN)           (Aplica medias de TRAIN sin tocar TEST)
```

---

## 2. Patrón Estándar con `ColumnTransformer`

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier

# 1. Definición de columnas por tipo
num_cols = ["edad", "antiguedad_meses", "monto_facturado", "score_credito"]
cat_cols = ["pais", "tipo_cuenta", "canal_adquisicion"]

# 2. Pipeline para variables numéricas
num_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

# 3. Pipeline para variables categóricas
cat_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
])

# 4. Ensamble de transformadores con ColumnTransformer
preprocessor = ColumnTransformer(transformers=[
    ("num", num_transformer, num_cols),
    ("cat", cat_transformer, cat_cols)
])

# 5. Pipeline final completo (Preprocesamiento + Estimador)
modelo_completo = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42))
])

# 6. Ajuste seguro: el pipeline se encarga de aislar train de test
modelo_completo.fit(X_train, y_train)
predicciones = modelo_completo.predict(X_test)
```

