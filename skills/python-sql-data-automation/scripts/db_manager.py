#!/usr/bin/env python3
"""
Módulo de Gestión de Base de Datos SQLite3 Seguro (Data Access Layer)
--------------------------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Programa: Talento Tech - Especialización Python & SQL
Propósito: Proveer una capa de persistencia transaccional con consultas
parametrizadas obligatorias, protección contra SQLi y context managers.
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "gestion_datos.db"):
        self.db_path = db_path
        self._init_schema()

    @contextmanager
    def get_connection(self):
        """Context manager que abre, configura, commitea y cierra la conexión de forma segura."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        """Inicializa las tablas DDL si no existen."""
        ddl_clientes = """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            telefono TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        ddl_transacciones = """
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            monto REAL NOT NULL CHECK(monto > 0),
            concepto TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT
        );
        """
        with self.get_connection() as conn:
            conn.execute(ddl_clientes)
            conn.execute(ddl_transacciones)

    def crear_cliente(self, nombre: str, email: str, telefono: Optional[str] = None) -> int:
        """Inserta un cliente utilizando parámetros seguros."""
        query = "INSERT INTO clientes (nombre, email, telefono) VALUES (?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (nombre.strip(), email.strip().lower(), telefono))
            return cursor.lastrowid

    def obtener_cliente_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca un cliente por email de forma inmune a Inyección SQL."""
        query = "SELECT id, nombre, email, telefono, fecha_registro FROM clientes WHERE email = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (email.strip().lower(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def registrar_transaccion(self, cliente_id: int, monto: float, concepto: str) -> int:
        """Registra una transacción transaccional vinculada a un cliente existente."""
        query = "INSERT INTO transacciones (cliente_id, monto, concepto) VALUES (?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (cliente_id, monto, concepto.strip()))
            return cursor.lastrowid

    def obtener_resumen_cliente(self, cliente_id: int) -> Dict[str, Any]:
        """Calcula métricas agregadas del cliente."""
        query = """
        SELECT 
            c.id, c.nombre, c.email,
            COUNT(t.id) as total_operaciones,
            COALESCE(SUM(t.monto), 0.0) as monto_total
        FROM clientes c
        LEFT JOIN transacciones t ON c.id = t.cliente_id
        WHERE c.id = ?
        GROUP BY c.id, c.nombre, c.email;
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (cliente_id,))
            row = cursor.fetchone()
            return dict(row) if row else {}

if __name__ == "__main__":
    test_db = "test_temp.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    db = DatabaseManager(test_db)
    try:
        cid = db.crear_cliente("Rubén Barrios", "ruben.data@example.com", "+5491100000000")
        db.registrar_transaccion(cid, 1500.75, "Licencia Antigravity Suite")
        resumen = db.obtener_resumen_cliente(cid)
        print("Módulo de base de datos verificado con éxito:")
        print(resumen)
    finally:
        if os.path.exists(test_db):
            os.remove(test_db)
