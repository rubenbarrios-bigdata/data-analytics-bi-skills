"""
Capa de Acceso a Datos (DAL) para Sistema Modular
"""
import sqlite3
from typing import List, Dict, Any, Optional

class RepositorioProductos:
    def __init__(self, db_path: str = "sistema.db"):
        self.db_path = db_path
        self._crear_tablas()

    def _conectar(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def _crear_tablas(self) -> None:
        query = """
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL CHECK(precio >= 0),
            stock INTEGER NOT NULL CHECK(stock >= 0)
        );
        """
        with self._conectar() as conn:
            conn.execute(query)

    def agregar_producto(self, codigo: str, nombre: str, categoria: str, precio: float, stock: int) -> int:
        query = """
        INSERT INTO productos (codigo, nombre, categoria, precio, stock)
        VALUES (?, ?, ?, ?, ?)
        """
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (codigo.upper(), nombre.strip(), categoria.strip(), precio, stock))
            return cursor.lastrowid

    def listar_todos(self) -> List[Dict[str, Any]]:
        query = "SELECT id, codigo, nombre, categoria, precio, stock FROM productos ORDER BY categoria, nombre"
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def buscar_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        query = "SELECT id, codigo, nombre, categoria, precio, stock FROM productos WHERE codigo = ?"
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (codigo.upper().strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None

