#!/usr/bin/env python3
"""
Sanitizador y Validador de BOM en Archivos TMDL
-----------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Propósito: Inspeccionar y eliminar recursivamente el encabezado BOM
(Byte Order Mark: 0xEF, 0xBB, 0xBF) de todos los archivos .tmdl en un PBIP,
garantizando compatibilidad estricta con el motor tabular de Analysis Services.
"""

import os
import sys
from typing import List, Tuple

UTF8_BOM = b"\xef\xbb\xbf"

def sanitizar_archivo_tmdl(filepath: str) -> bool:
    """Lee el archivo binario; si tiene BOM, lo sobreescribe sin él."""
    with open(filepath, "rb") as f:
        contenido = f.read()

    if contenido.startswith(UTF8_BOM):
        contenido_sin_bom = contenido[len(UTF8_BOM):]
        with open(filepath, "wb") as f:
            f.write(contenido_sin_bom)
        return True  # Fue reparado
    return False  # Ya estaba limpio

def escanear_directorio_tmdl(directorio_raiz: str) -> Tuple[int, int, List[str]]:
    total_tmdl = 0
    total_reparados = 0
    archivos_afectados = []

    for root, _, files in os.walk(directorio_raiz):
        for file in files:
            if file.endswith(".tmdl"):
                total_tmdl += 1
                ruta_completa = os.path.join(root, file)
                fue_reparado = sanitizar_archivo_tmdl(ruta_completa)
                if fue_reparado:
                    total_reparados += 1
                    archivos_afectados.append(ruta_completa)

    return total_tmdl, total_reparados, archivos_afectados

if __name__ == "__main__":
    directorio = sys.argv[1] if len(sys.argv) > 1 else "."
    print("=" * 65)
    print("   SANITIZADOR DE ARCHIVOS TMDL (UTF-8 SIN BOM)")
    print("=" * 65)
    total, reparados, lista = escanear_directorio_tmdl(directorio)
    print(f" Total de archivos .tmdl examinados: {total}")
    print(f" Archivos con BOM reparados a UTF-8 puro: {reparados}")

    if reparados > 0:
        print("\n[!] Archivos que contenían BOM corregidos:")
        for a in lista:
            print(f"  * {a}")
    else:
        print("\n[OK] Todos los archivos TMDL cumplen con la codificación requerida.")
    print("=" * 65)

