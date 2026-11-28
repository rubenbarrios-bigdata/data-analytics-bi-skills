# Playbook de IA Aplicada al Análisis de Datos: Microsoft Copilot (Power BI) y Claude AI (Python)

Basado en las secciones exclusivas de **Inteligencia Artificial** del curso **Experto en Análisis y Visualización de Datos + IA** (*DataBoosters Academy*).

---

## 1. Microsoft Copilot para Power BI (Generación de DAX y Reportes)

Para obtener medidas DAX libres de errores y páginas de reporte coherentes con el negocio, los prompts enviados a Microsoft Copilot dentro de Power BI deben seguir la estructura **Contexto del Modelo + Regla Matemática + Filtros + Formato**.

### A. Estructura de Prompt para Medidas DAX en Copilot
1. **Especificar tablas y columnas exactas** del modelo semántico (ej. `'FactVentas'[MontoVenta]`, `'Calendario'[Fecha]`).
2. **Definir el manejo de divisiones por cero y valores en blanco** (`DIVIDE(..., ..., 0)`, `COALESCE`).
3. **Indicar el contexto de filtro** (`CALCULATE`, `ALLSELECTED`, `SAMEPERIODLASTYEAR`).

#### Ejemplo de Prompt DAX de Alta Precisión para Copilot:
> *"Crea una medida DAX llamada `Variación YoY Ventas %` en la tabla `_Medidas` que calcule el crecimiento porcentual de `[Ventas Netas]` respecto al mismo período del año anterior usando `'Calendario'[Fecha]`. Si no hay ventas en el año anterior, debe devolver BLANK() para no mostrar -100% en meses futuros. Utiliza `DIVIDE`."*

#### Medida DAX Generada y Auditada:
```dax
Variación YoY Ventas % = 
VAR _VentasActuales = [Ventas Netas]
VAR _VentasAnioAnterior = 
    CALCULATE(
        [Ventas Netas],
        SAMEPERIODLASTYEAR('Calendario'[Fecha])
    )
RETURN
    IF(
        NOT ISBLANK(_VentasActuales) && NOT ISBLANK(_VentasAnioAnterior),
        DIVIDE(_VentasActuales - _VentasAnioAnterior, _VentasAnioAnterior)
    )
```

### B. Prompts de Copilot para Creación de Páginas e Insights Visuales
- **Creación de Página Ejecutiva:** *"Crea una página de resumen comercial con 4 tarjetas KPI para Ventas Netas, Margen Bruto %, Ticket Promedio y Total Clientes; un gráfico de líneas de tendencia mensual con línea de pronóstico; y un mapa geográfico de ventas por país/estado."*
- **Extracción de Insights Narrativos:** *"Analiza las principales causas de caída del margen en el último trimestre desglosado por categoría de producto y descuento aplicado."*

---

## 2. Claude AI como Asistente de Desarrollo y Depuración en Python

Claude se utiliza en el flujo analítico para acelerar la escritura de código Python (incluyendo **Programación Orientada a Objetos - POO**), explicar bloques complejos y depurar errores sin fricción.

### A. Protocolo de 4 Pasos con Claude AI para Python Analítico
1. **Definición de Esquema y Ejemplo de Datos:** Proporcionar a Claude los nombres de columnas, tipos de datos y 3 filas de muestra (sin enviar datos sensibles/PII reales).
2. **Solicitud de Arquitectura POO Modular:** Pedir clases con responsabilidades claras (ej. `DataLoader`, `DataCleaner`, `KPICalculator`) con *type hints* y *docstrings*.
3. **Depuración Guiada por Traceback:** Ante un error, pasar el *traceback* completo junto con la línea exacta y pedir:
   - Causa raíz del error.
   - Solución defensiva (manejo de excepciones `try/except` y validación de bordes).
4. **Verificación Cruzada:** Ejecutar un bloque de aserciones (`assert`) que valide que el conteo de filas y la suma de columnas numéricas antes y después de la transformación sean consistentes.
