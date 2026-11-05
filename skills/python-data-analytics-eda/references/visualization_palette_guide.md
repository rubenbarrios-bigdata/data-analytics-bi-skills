# Guía de Visualización y Paletas Cromáticas: Seaborn, Matplotlib & Plotly

Reglas de diseño para producir gráficos analíticos legibles, accesibles y con nivel de publicación ejecutiva.

---

## 1. Configuración Estética Global en Seaborn y Matplotlib

Para evitar gráficos toscos con fuentes pequeñas o bordes innecesarios, inicializar siempre el entorno con este estándar:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración corporativa limpia
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
sns.set_theme(
    style="whitegrid",
    font="sans-serif",
    rc={
        "figure.figsize": (10, 6),
        "figure.dpi": 150,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 12,
        "axes.edgecolor": "#CCCCCC",
        "grid.color": "#E5E5E5"
    }
)
```

---

## 2. Paletas de Colores Accesibles (Colorblind-Friendly)

Evitar combinaciones rojo-verde puro sin distinción de saturación para no excluir a personas con daltonismo.

1. **Paletas Secuenciales (Para magnitudes de menor a mayor):**
   - `viridis` (Perceptualmente uniforme, la mejor opción científica).
   - `Blues`, `mako`.
2. **Paletas Divergentes (Para valores centrados en cero o desviaciones):**
   - `coolwarm`, `vlag`, `Spectral`.
3. **Paletas Cualitativas (Para categorías discretas):**
   - `Set2`, `tab10`, `colorblind`.

---

## 3. Matriz de Selección de Gráficos

| Tipo de Variable(s) | Gráfico Recomendado | Código Rápido (Seaborn / Plotly) |
| :--- | :--- | :--- |
| **1 Numérica** | Histograma con KDE + Boxplot | `sns.histplot(df['col'], kde=True)` / `sns.boxplot(x=df['col'])` |
| **1 Categórica** | Gráfico de Barras horizontales | `sns.countplot(y='cat', data=df, order=df['cat'].value_counts().index)` |
| **2 Numéricas** | Dispersión (Scatter) | `sns.scatterplot(x='col1', y='col2', hue='cat', data=df)` |
| **1 Categórica + 1 Numérica** | Boxplot o Violin Plot | `sns.boxplot(x='cat', y='num', data=df, palette='Set2')` |
| **Múltiples Numéricas** | Heatmap Triangular | `sns.heatmap(df.corr(), mask=np.triu(np.ones_like(...)), annot=True)` |
| **Exploración Interactiva** | Scatter Plotly con Hover | `px.scatter(df, x='col1', y='col2', color='cat', hover_data=['id'])` |

