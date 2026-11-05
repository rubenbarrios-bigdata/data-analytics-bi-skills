---
name: python-sql-data-automation
description: "Desarrollo de software y pipelines de automatización de datos con Python estándar y SQLite3 transaccional. Arquitectura modular por capas, prevención de Inyección SQL, manipulación estructurada de colecciones, I/O de CSV/archivos y CLI robustos. Basado en la certificación oficial de Talento Tech (Ministerio de Educación CABA)."
---

# Python & SQL Data Automation: Programación Modular y Persistencia

## Propósito y Alcance Operativo
Esta skill capacita al agente para construir soluciones de software, utilidades CLI de automatización y pipelines de persistencia relacional con **Python** y **SQLite3**, adhiriéndose a las mejores prácticas de desarrollo y datos: modularidad por capas, transaccionalidad segura (`commit`/`rollback`), consultas parametrizadas obligatorias para neutralizar la Inyección SQL, gestión de colecciones complejas y manejo robusto de archivos planos (CSV y texto).

---

## 1. Árbol de Decisión Operativo

```mermaid
flowchart TD
    Task([Requerimiento de Software / Datos]) --> Type{Naturaleza de la Tarea}

    Type -->|Persistencia Relacional| DB{Operación de BD}
    Type -->|Procesamiento de Archivos| IO{Tipo de Formato}
    Type -->|Estructura de Software| Arch[Diseño Modular en Capas]
    Type -->|Transformación en Memoria| Struct[Colecciones & Comprensión]

    DB -->|DDL / Creación de Esquema| DDL[Tablas, Llaves Primarias & Restricciones]
    DB -->|CRUD / DML| DML[Consultas Parametrizadas Seguras (?)]
    DB -->|Transacciones Múltiples| TX[Context Manager + try/except Commit/Rollback]

    IO -->|CSV / Texto Delimitado| CSV[Módulo csv nativo: reader/writer & DictReader]
    IO -->|Archivos Planos / Logs| TXT[Manejo con with open y codificación UTF-8]

    Arch --> Layers[Separación: Data Access Layer / Business Logic / CLI Interface]
```

---

## 2. Flujo de Trabajo Metodológico y Estándares de Código

### Fase 1: Arquitectura Modular por Capas (Separation of Concerns)
Todo desarrollo de automatización en Python debe dividirse en componentes desacoplados:
1. **Capa de Persistencia / Acceso a Datos (`database.py` o `repositories/`):**
   - Responsable exclusiva de conexiones SQLite3, transacciones y sentencias SQL.
   - Prohibido mezclar lógica de negocio o entradas/salidas de usuario (`input()`, `print()`) en esta capa.
2. **Capa de Negocio / Servicios (`services.py`):**
   - Validación de reglas de dominio, cálculo de métricas, filtrado y transformación de datos.
3. **Capa de Presentación / CLI (`main.py` o `cli.py`):**
   - Menú de usuario, lectura de argumentos por consola (`sys.argv` o menú interactivo), manejo de mensajes estéticos con `colorama`.

---

### Fase 2: Colecciones Estructuradas y Eficiencia en Memoria
1. **Elección de Estructuras de Datos:**
   - **Listas (`list`):** Secuencias ordenadas y mutables. Ideales para listas de registros o resultados iterativos.
   - **Tuplas (`tuple`):** Secuencias inmutables. Uso obligatorio para representar registros inalterables y parámetros de consulta SQL (`(param1, param2)`).
   - **Diccionarios (`dict`):** Estructura clave-valor $O(1)$. Uso preferente para mapeo de registros relacionales (con `sqlite3.Row` o `csv.DictReader`).
   - **Conjuntos (`set`):** Elementos únicos sin orden. Uso obligado para deduplicación rápida y operaciones de teoría de conjuntos (`union`, `intersection`, `difference`).
2. **Comprensión de Listas y Diccionarios (Comprehensions):**
   - Priorizar comprehensions legibles sobre bucles `for` tradicionales con `.append()` para transformaciones puras en memoria.

---

### Fase 3: Persistencia Relacional con SQLite3 Seguro
1. **Regla de Oro contra Inyección SQL (SQL Injection):**
   - **ESTRICTAMENTE PROHIBIDO:** Concatenar strings o usar f-strings en consultas (`f"SELECT * FROM users WHERE id = '{user_id}'"`).
   - **OBLIGATORIO:** Usar marcadores posicionales (`?`) con tuplas de argumentos:
     ```python
     cursor.execute("SELECT * FROM users WHERE email = ? AND status = ?", (email, status))
     ```
2. **Transaccionalidad Atómica y Recuperación de Fallos:**
   - Toda operación de modificación (INSERT, UPDATE, DELETE) debe estar envuelta en un bloque `try/except/finally`.
   - Si la operación tiene éxito, ejecutar `conn.commit()`.
   - Si ocurre una excepción (`sqlite3.Error`), ejecutar `conn.rollback()` para preservar la integridad del estado previo.
   - Uso de context managers (`with conn:`) para garantizar el cierre adecuado de cursores y conexiones.
3. **Optimización con `sqlite3.Row`:**
   - Configurar `conn.row_factory = sqlite3.Row` para acceder a las columnas tanto por índice numérico como por nombre de campo (`row['precio']`).

---

### Fase 4: Procesamiento de Archivos e Integración CSV
1. **Codificación Universal:**
   - Toda lectura y escritura de archivos debe especificar explícitamente `encoding="utf-8"` y `newline=""` en Windows para evitar saltos de línea dobles indeseados.
2. **Uso de `csv.DictReader` y `csv.DictWriter`:**
   - Manejar archivos tabulares asociando cabeceras a diccionarios para hacer el código inmune a cambios en el orden físico de las columnas.
3. **Flujos de Carga Masiva (Bulk Loading):**
   - Utilizar `cursor.executemany()` para insertar lotes de registros desde CSV de manera transaccional y eficiente.

---

## 3. Antipatrones Críticos a Evitar

| Antipatrón | Riesgo Técnico | Solución Mandatoria |
| :--- | :--- | :--- |
| **Concatenación de SQL con f-strings** | Vulnerabilidad crítica de SQL Injection y corrupción de base de datos. | Uso exclusivo de consultas parametrizadas con placeholders `?` y tuplas. |
| **Omitir `conn.rollback()` en excepciones** | Estados inconsistentes o bloqueos transaccionales (*database is locked*). | Envolver sentencias DML en `try / except sqlite3.Error` con rollback explícito. |
| **No cerrar archivos o conexiones** | Fuga de descriptores de archivo y bloqueos en Windows. | Utilizar siempre la instrucción `with` (`with open(...)`, `with sqlite3.connect(...)`). |
| **Mezclar `print()` y `input()` dentro de la lógica SQL** | Código acoplado, imposible de testear y no reutilizable. | Separar en capas: el módulo de datos retorna datos puros (`dict`/`list`), el CLI maneja la interacción. |
| **Abrir archivos en Windows sin `encoding='utf-8'`** | Errores de decodificación `UnicodeDecodeError` con tildes y caracteres especiales. | Declarar siempre `open(path, 'r', encoding='utf-8')`. |

---

## 4. Reglas de Verificación y Testing de Código

1. **Prueba de Inyección SQL:**
   - Pasar strings maliciosos como `' OR '1'='1` o `'; DROP TABLE usuarios; --` como argumento de búsqueda y validar que el motor los trate como literales inertes sin ejecutar sintaxis SQL.
2. **Prueba de Rollback Transaccional:**
   - Simular una inserción por lotes con un registro inválido al final y verificar que la base de datos revierta todos los registros precedentes del lote.
3. **Prueba de Concurrencia e Integridad de Tipos:**
   - Verificar la aplicación de constraints en SQLite3 (`PRAGMA foreign_keys = ON;`, `PRIMARY KEY`, `NOT NULL`, `UNIQUE`, `CHECK`).

