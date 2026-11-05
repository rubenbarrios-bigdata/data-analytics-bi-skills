# Arquitectura del Motor Gráfico DAX: Tarjetas KPI con Efecto 3D Dual Flip

Integrar HTML, CSS puro y SVG nativo dentro de medidas DAX permite superar las limitaciones de formato de Power BI Desktop y entregar experiencias ejecutivas interactivas.

---

## 1. Concepto del Efecto 3D Dual Flip

```
+---------------------------+         +---------------------------+
|        FRENTE (FRONT)     |         |       REVERSO (BACK)      |
|  [KPI Actual]   [+14.2%]  |  Giro   |  [DIAGNÓSTICO EJECUTIVO]  |
|  $ 1,450,200 USD          | ====>   |  "El crecimiento fue      |
|                           |  180°   |  impulsado en un 78% por  |
|  [--- SVG SPARKLINE ---]  |         |  la apertura de la tienda |
|  (Línea continua 12 meses)|         |  Norte."                  |
+---------------------------+         +---------------------------+
```

---

## 2. Estructura CSS Obligatoria para Giro 3D

Para lograr una rotación realista sin distorsión gráfica:

1. **`perspective: 1000px;`** en el contenedor exterior para dar profundidad tridimensional a la escena.
2. **`transform-style: preserve-3d;`** en el elemento que rota (`.card-inner`), con transición suave: `transition: transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1);`.
3. **`backface-visibility: hidden;`** en ambas caras (frente y reverso), para que la cara posterior permanezca oculta cuando apunta hacia atrás.
4. **`transform: rotateY(180deg);`** preestablecido en el reverso, de modo que al rotar el contenedor 180°, el reverso quede orientado al usuario.

---

## 3. Generación de Gráficos Sparkline en SVG con DAX

DAX puede construir cadenas SVG interpolando coordenadas matemáticas directamente sobre las métricas:

- **Encabezado SVG:** `<svg viewBox='0 0 200 50' preserveAspectRatio='none'>`
- **Trazado de la Línea (`<polyline>` o `<path>`):** Las coordenadas `(x, y)` se calculan normalizando los meses al ancho ($X \in [0, 200]$) y los valores de venta al alto invertido ($Y \in [5, 45]$).
- **Escape de Caracteres Hexadecimales:**
  - El símbolo `#` en códigos de color CSS (ej. `#1A73E8`) debe escribirse como `%231A73E8` si el SVG se inyecta mediante `data:image/svg+xml;utf8,...` o como texto plano directo en visuales HTML.

