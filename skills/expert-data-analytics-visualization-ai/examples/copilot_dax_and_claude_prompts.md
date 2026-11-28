# Catálogo de Prompts y Soluciones con IA: Microsoft Copilot (Power BI) y Claude (Python)

Plantillas listas para producción basadas en la certificación **Experto en Análisis y Visualización de Datos + IA** (*DataBoosters Academy*).

---

## 1. Prompts para Microsoft Copilot en Power BI (Generación de Medidas DAX)

### Caso A: Participación Porcentual sobre el Total Respetando Slicers (`% Share of Sales`)
- **Prompt para Copilot:**
  > *"Genera una medida DAX llamada `% Participación Ventas` que divida la medida `[Ventas Netas]` entre el total de `[Ventas Netas]` respetando los filtros externos seleccionados en la página (`ALLSELECTED` sobre la tabla `'DimProductos'`). Usa `DIVIDE` con resultado alternativo 0."*
- **Código DAX Validado:**
  ```dax
  % Participación Ventas = 
  VAR _VentasActuales = [Ventas Netas]
  VAR _VentasTotalesSeleccion = 
      CALCULATE(
          [Ventas Netas],
          ALLSELECTED('DimProductos')
      )
  RETURN
      DIVIDE(_VentasActuales, _VentasTotalesSeleccion, 0)
  ```

### Caso B: Clientes Nuevos vs Recurrentes con DAX
- **Prompt para Copilot:**
  > *"Crea una medida DAX llamada `Clientes Nuevos` que cuente cuántos `id_cliente` distintos en `'FactVentas'` realizaron su primera compra histórica dentro del período seleccionado en `'Calendario'[Fecha]`."*
- **Código DAX Validado:**
  ```dax
  Clientes Nuevos = 
  VAR _ClientesPeriodo = VALUES('FactVentas'[id_cliente])
  VAR _FechaMinimaFiltro = MIN('Calendario'[Fecha])
  RETURN
      COUNTROWS(
          FILTER(
              _ClientesPeriodo,
              CALCULATE(
                  MIN('FactVentas'[fecha_orden]),
                  ALLEXCEPT('FactVentas', 'FactVentas'[id_cliente])
              ) >= _FechaMinimaFiltro
          )
      )
  ```

---

## 2. Prompts para Claude AI (Desarrollo y Optimización de Python para Datos)

### Caso A: Generación de Clase Validadora de Calidad de Datos (POO)
- **Prompt para Claude:**
  > *"Escribe una clase en Python usando POO llamada `DataQualityAuditor` que reciba una lista de diccionarios tabulares, verifique qué porcentaje de filas tiene valores nulos por columna, detecte duplicados por clave primaria `order_id` y devuelva un diccionario de diagnóstico listo para exportar a JSON."*

### Caso B: Refactorización y Depuración de Código Lento
- **Prompt para Claude:**
  > *"Analiza esta función en Python que tarda demasiado al cruzar dos archivos CSV grandes con bucles `for` anidados. Refactorízala utilizando un diccionario hash (`dict` lookup) en $O(N)$ de complejidad temporal y agrega manejo de errores si una clave no existe."*
