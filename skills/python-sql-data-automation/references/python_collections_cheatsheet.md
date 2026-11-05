# Cheatsheet de Colecciones y Módulos Estándar en Python

Referencia rápida de estructuras de datos y utilidades nativas para ingeniería y automatización de datos.

---

## 1. Tabla Comparativa de Colecciones Estructuradas

| Colección | Sintaxis | Mutable | Ordenada | Duplicados | Complejidad Búsqueda | Caso de Uso Principal |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Lista (`list`)** | `[1, 2, 3]` | Sí | Sí | Sí | $O(n)$ | Almacenar secuencias de registros procesables. |
| **Tupla (`tuple`)** | `(1, 2, 3)` | No | Sí | Sí | $O(n)$ | Llaves compuestas, parámetros inmutables de SQL `?`. |
| **Conjunto (`set`)** | `{1, 2, 3}` | Sí | No | No | $O(1)$ promedio | Deduplicación inmediata, verificación de membresía (`x in s`). |
| **Diccionario (`dict`)** | `{"a": 1}` | Sí | Sí (inserción) | Claves no | $O(1)$ promedio | Representación de entidades, registros de base de datos (`Row`). |

---

## 2. Comprensión de Colecciones (Comprehensions)

```python
# 1. Comprensión de Listas con filtrado condicional
precios_brutos = [100.0, 45.0, 230.0, 15.0]
precios_con_iva = [round(p * 1.21, 2) for p in precios_brutos if p > 20.0]

# 2. Comprensión de Diccionarios
usuarios = [("usr_1", "Ruben"), ("usr_2", "David"), ("usr_3", "Barrios")]
mapa_usuarios = {uid: nombre for uid, nombre in usuarios}

# 3. Comprensión de Conjuntos para deduplicación normalizada
categorias_sucias = [" Moda ", "Tecnología", "moda", " HOGAR ", "tecnología"]
categorias_limpias = {c.strip().capitalize() for c in categorias_sucias}
# Resultado: {'Moda', 'Tecnología', 'Hogar'}
```

---

## 3. Módulos Estándar Críticos para Pipelines

### A. Módulo `datetime`
```python
from datetime import datetime, timezone, timedelta

# Fecha y hora actual en UTC
ahora_utc = datetime.now(timezone.utc)
iso_string = ahora_utc.isoformat()

# Parseo de strings de fecha
fecha_objeto = datetime.strptime("2026-11-04 20:30:00", "%Y-%m-%d %H:%M:%S")

# Cálculo de intervalos temporales
hace_30_dias = ahora_utc - timedelta(days=30)
```

### B. Módulo `csv` (I/O Robusto)
```python
import csv

# Lectura segura con DictReader
with open("ventas.csv", mode="r", encoding="utf-8", newline="") as f:
    lector = csv.DictReader(f)
    for fila in lector:
        id_venta = int(fila["id"])
        monto = float(fila["monto"])

# Escritura segura con DictWriter
fieldnames = ["id", "cliente", "monto"]
with open("salida.csv", mode="w", encoding="utf-8", newline="") as f:
    escritor = csv.DictWriter(f, fieldnames=fieldnames)
    escritor.writeheader()
    escritor.writerow({"id": 101, "cliente": "Empresa S.A.", "monto": 4500.50})
```

### C. Módulos `os` y `sys`
```python
import os
import sys

# Construcción de rutas multiplataforma
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "data", "sistema.db")

# Creación segura de directorios
os.makedirs(os.path.dirname(db_path), exist_ok=True)
```

