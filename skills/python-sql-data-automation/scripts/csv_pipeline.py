#!/usr/bin/env python3
"""
Pipeline de Ingesta y Carga Masiva de CSV a SQLite3
--------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Propósito: Automatizar la ingesta, limpieza de datos y carga transaccional
en bloque (bulk loading) desde archivos CSV hacia SQLite3.
"""

import csv
import sqlite3
import os
from typing import List, Tuple

def procesar_y_cargar_csv(csv_path: str, db_path: str) -> int:
    """
    Lee un archivo CSV con encoding UTF-8, valida sus campos numéricos
    y realiza una inserción masiva transaccional usando executemany.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Archivo no encontrado: {csv_path}")

    registros_validos: List[Tuple[str, float, int]] = []

    # 1. Lectura segura con DictReader
    with open(csv_path, mode="r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for num_fila, row in enumerate(reader, start=2):
            try:
                producto = row["producto"].strip()
                precio = float(row["precio"].replace("$", "").strip())
                stock = int(row["stock"].strip())

                if not producto or precio < 0 or stock < 0:
                    continue
                registros_validos.append((producto, precio, stock))
            except (ValueError, KeyError) as e:
                print(f"[ALERTA] Fila {num_fila} descartada por formato erróneo: {e}")

    # 2. Persistencia Transaccional con executemany
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS inventario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto TEXT NOT NULL,
                    precio REAL NOT NULL,
                    stock INTEGER NOT NULL
                );
            """)
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO inventario (producto, precio, stock) VALUES (?, ?, ?)",
                registros_validos
            )
            total_insertados = cursor.rowcount
            print(f"[EXITO] {total_insertados} registros insertados en una única transacción atómica.")
            return total_insertados
    finally:
        conn.close()

if __name__ == "__main__":
    print("Módulo de pipeline CSV listo para ejecución.")

