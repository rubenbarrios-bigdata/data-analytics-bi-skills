# Cheatsheet de Manipulación y Wrangling: NumPy & Pandas

Guía de referencia rápida con las operaciones analíticas más comunes y eficientes para ingeniería y análisis de datos en Python.

---

## 1. NumPy: Vectorización y Operaciones Matriciales

```python
import numpy as np

# 1. Creación y filtrado condicional rápido
arr = np.array([10, 25, 40, 55, 70])
mascara = arr > 30
filtrados = arr[mascara]

# 2. Asignación condicional vectorizada (reemplazo de if/else)
# Sintaxis: np.where(condicion, valor_si_verdadero, valor_si_falso)
etiquetas = np.where(arr >= 50, "Alto", "Bajo")

# 3. Broadcasting (operación escalar sobre matriz)
matriz = np.array([[1, 2, 3], [4, 5, 6]])
matriz_normalizada = (matriz - np.mean(matriz)) / np.std(matriz)
```

---

## 2. Pandas: Indexación Segura y Selección

```python
import pandas as pd

# 1. Regla de oro para evitar SettingWithCopyWarning
# ❌ INCORRECTO: df[df['edad'] > 30]['salario'] = 50000
#  CORRECTO:
df.loc[df['edad'] > 30, 'salario'] = 50000

# 2. Selección combinada con operadores bit a bit (&, |, ~)
filtro_complejo = (df['categoria'] == 'Tecnología') & (df['monto'] >= 1000)
df_sub = df.loc[filtro_complejo, ['id', 'producto', 'monto']].copy()
```

---

## 3. Limpieza y Curación de Datos

```python
# 1. Diagnóstico de valores nulos
nulos_resumen = pd.DataFrame({
    'nulos_total': df.isnull().sum(),
    'porcentaje_nulos': (df.isnull().sum() / len(df) * 100).round(2)
})

# 2. Imputación robusta con mediana
mediana_precio = df['precio'].median()
df['precio'] = df['precio'].fillna(mediana_precio)

# 3. Parseo estricto de fechas
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
df['año'] = df['fecha'].dt.year
df['mes'] = df['fecha'].dt.month
df['dia_semana'] = df['fecha'].dt.day_name()
```

---

## 4. Agrupaciones y Tablas Pivote (Pivot Tables)

```python
# 1. Agrupación múltiple nombrada (Named Aggregations)
resumen_ventas = df.groupby(['region', 'categoria']).agg(
    ingresos_totales=('monto', 'sum'),
    ticket_promedio=('monto', 'mean'),
    desv_estandar=('monto', 'std'),
    total_operaciones=('id', 'count')
).reset_index()

# 2. Pivot Table con totales marginales
tabla_cruzada = pd.pivot_table(
    df,
    values='monto',
    index='region',
    columns='categoria',
    aggfunc='sum',
    fill_value=0,
    margins=True,
    margins_name='Total General'
)
```

