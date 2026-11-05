# Guía de Métricas de Evaluación en Machine Learning Empresarial

La selección de la métrica de evaluación debe alinearse con el impacto financiero de cada tipo de error.

---

## 1. Métricas de Clasificación y Matriz de Confusión

```
                   PREDICCIÓN POSITIVA (1)      PREDICCIÓN NEGATIVA (0)
REAL POSITIVO (1)       Verdadero Positivo (TP)       Falso Negativo (FN - Error Tipo II)
REAL NEGATIVO (0)       Falso Positivo (FP - Tipo I)  Verdadero Negativo (TN)
```

### Fórmulas Matemáticas y Connotación de Negocio

1. **Accuracy (Exactitud Global):**
   $$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$
   - *Cuándo usar:* Únicamente con clases 50/50 equilibradas.
   - *Peligro:* Inútil en detección de fraude o churn (donde la clase positiva suele ser < 5%).

2. **Precision (Precisión):**
   $$\text{Precision} = \frac{TP}{TP + FP}$$
   - *Pregunta clave:* De todos los casos que el modelo predijo como positivos, ¿cuántos lo fueron realmente?
   - *Prioridad de negocio:* Cuando un Falso Positivo es muy costoso (ej. marcar a un cliente VIP como estafador o enviar ofertas exclusivas de alto costo).

3. **Recall / Sensibilidad:**
   $$\text{Recall} = \frac{TP}{TP + FN}$$
   - *Pregunta clave:* De todos los casos positivos reales que existían, ¿cuántos logró capturar el modelo?
   - *Prioridad de negocio:* Cuando un Falso Negativo es inaceptable (ej. dejar escapar un cliente a punto de cancelar o no detectar una enfermedad crítica).

4. **F1-Score (Media Armónica):**
   $$\text{F1} = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
   - Métrica balanceada ideal cuando se busca equilibrio entre no alertar en falso y no dejar escapar positivos.

5. **ROC-AUC (Área bajo la curva ROC):**
   - Mide la capacidad de discriminación del modelo a través de todos los umbrales de probabilidad posibles ($0.5$ a $1.0$). Un valor de $0.5$ equivale al azar, y $1.0$ a una separación perfecta.

---

## 2. Métricas de Regresión

1. **$R^2$ (Coeficiente de Determinación):**
   - Proporción de la varianza de la variable objetivo explicada por el modelo (de 0 a 1).
2. **MAE (Mean Absolute Error):**
   $$\text{MAE} = \frac{1}{n}\sum |y_i - \hat{y}_i|$$
   - En la misma unidad de medida que la variable original. No penaliza desproporcionadamente los errores grandes.
3. **RMSE (Root Mean Squared Error):**
   $$\text{RMSE} = \sqrt{\frac{1}{n}\sum (y_i - \hat{y}_i)^2}$$
   - Penaliza severamente los errores grandes al elevarlos al cuadrado. Ideal cuando una desviación grande es destructiva para el negocio.

---

## 3. Métricas de Agrupamiento (Clustering No Supervisado)

1. **Inercia (Within-Cluster Sum of Squares - WCSS):**
   - Suma de distancias euclidianas al cuadrado de cada punto al centroide de su clúster. Disminuye monótonamente conforme $k$ aumenta. Se busca el "punto de inflexión" o codo.
2. **Coeficiente de Silueta (Silhouette Score):**
   $$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$
   - $a(i)$: Distancia intra-clúster promedio.
   - $b(i)$: Distancia más cercana al siguiente clúster vecino.
   - Rango $[-1, 1]$: Valores $> 0.5$ indican clústeres densos y bien separados.

