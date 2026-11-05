# Prevención Rigurosa de Inyección SQL (SQL Injection) en Python

La Inyección SQL es una de las vulnerabilidades más críticas en el desarrollo de software. Ocurre cuando datos no confiables ingresados por un usuario se concatenan directamente en una sentencia SQL, permitiendo que el atacante altere la estructura semántica de la consulta.

---

## 1. Demostración de Vulnerabilidad vs Solución Segura

### ❌ Código Vulnerable (Antipatrón Prohibido)

```python
# PELIGRO: Uso de f-strings o concatenación de strings
usuario = input("Ingrese nombre de usuario: ")
# Si el usuario ingresa: admin' --
query = f"SELECT * FROM usuarios WHERE username = '{usuario}' AND password = '{password}'"
cursor.execute(query)
```

**Resultado de la consulta vulnerable:**
```sql
SELECT * FROM usuarios WHERE username = 'admin' --' AND password = 'xxx'
```
El motor de base de datos interpreta `--` como el inicio de un comentario, eliminando la validación del password y otorgando acceso irrestricto de administrador.

---

###  Código Inmune (Consulta Parametrizada Obligatoria)

```python
# SEGURO: El motor de SQLite3 compila la estructura SQL antes de evaluar los datos
usuario = input("Ingrese nombre de usuario: ")
query = "SELECT * FROM usuarios WHERE username = ? AND password = ?"
cursor.execute(query, (usuario, password))
```

**Mecanismo de Defensa:**
Al usar el marcador `?`, SQLite3 trata el valor ingresado (`admin' --`) estrictamente como una cadena de texto literal, nunca como código ejecutable. La comilla se escapa internamente y el comentario se evalúa como texto plano inofensivo.

---

## 2. Comparativa de Sintaxis Segura según el Tipo de Operación

| Operación | Sintaxis Parametrizada Segura | Tupla de Parámetros |
| :--- | :--- | :--- |
| **SELECT con Filtro** | `SELECT * FROM items WHERE id = ?` | `(item_id,)` *(nota la coma final para tupla de 1 elemento)* |
| **SELECT con Rango** | `SELECT * FROM ventas WHERE fecha BETWEEN ? AND ?` | `(fecha_inicio, fecha_fin)` |
| **INSERT** | `INSERT INTO clientes (nombre, email) VALUES (?, ?)` | `(nombre, email)` |
| **UPDATE** | `UPDATE productos SET precio = ? WHERE id = ?` | `(nuevo_precio, producto_id)` |
| **DELETE** | `DELETE FROM carritos WHERE expirado = ?` | `(True,)` |
| **Búsqueda Parcial (LIKE)** | `SELECT * FROM clientes WHERE nombre LIKE ?` | `(f"%{busqueda}%",)` *(el comodín se pasa al valor, no a la query)* |

---

## 3. Manejo Seguro de Nombres de Columnas o Tablas Dinámicas
Los marcadores de posición `?` **solo sirven para valores de datos**, no para nombres de tablas o columnas. Si una aplicación requiere ordenar por columnas dinámicas seleccionadas por el usuario, se debe aplicar una **Lista Blanca (Whitelist)** estricta:

```python
COLUMNAS_PERMITIDAS = {"nombre", "precio", "fecha_creacion"}
ORDENES_PERMITIDOS = {"ASC", "DESC"}

def listar_productos_ordenados(columna_orden: str, direccion: str = "ASC"):
    if columna_orden not in COLUMNAS_PERMITIDAS:
        raise ValueError(f"Columna de ordenación inválida: {columna_orden}")
    if direccion.upper() not in ORDENES_PERMITIDOS:
        raise ValueError(f"Dirección inválida: {direccion}")

    # Es seguro formatear únicamente porque pasó por validación estricta de lista blanca
    query = f"SELECT id, nombre, precio FROM productos ORDER BY {columna_orden} {direccion.upper()}"
    cursor.execute(query)
    return cursor.fetchall()
```

