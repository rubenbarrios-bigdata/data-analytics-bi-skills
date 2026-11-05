#!/usr/bin/env python3
"""
Validador de Integridad de Proyectos Power BI Project (PBIP) y Archivos TMDL
----------------------------------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Área: Power BI DevOps & Microsoft Fabric CI/CD
Propósito: Validar en canalizaciones CI/CD la integridad estructural de un PBIP,
la validez sintáctica de sus JSONs y la ausencia estricta de encabezado BOM en TMDL.
"""

import os
import sys
import json
from typing import List, Dict, Any, Tuple

def verificar_bom_utf8(filepath: str) -> bool:
    """Verifica si un archivo contiene el Byte Order Mark (BOM: 0xEF, 0xBB, 0xBF)."""
    with open(filepath, "rb") as f:
        primeros_bytes = f.read(3)
        return primeros_bytes == b"\xef\xbb\xbf"

def validar_proyecto_pbip(directorio_raiz: str) -> Tuple[bool, List[str]]:
    errores = []

    if not os.path.isdir(directorio_raiz):
        return False, [f"El directorio especificado no existe: {directorio_raiz}"]

    # 1. Buscar archivo puntero .pbip
    archivos_pbip = [f for f in os.listdir(directorio_raiz) if f.endswith(".pbip")]
    if not archivos_pbip:
        errores.append("No se encontró el archivo raíz '.pbip' en el directorio.")
    else:
        nombre_base = os.path.splitext(archivos_pbip[0])[0]

        # 2. Validar estructura de carpetas .Report y .SemanticModel
        report_dir = os.path.join(directorio_raiz, f"{nombre_base}.Report")
        semantic_dir = os.path.join(directorio_raiz, f"{nombre_base}.SemanticModel")

        if not os.path.isdir(report_dir):
            errores.append(f"Falta la carpeta obligatoria de reporte: '{nombre_base}.Report'")
        else:
            pbir_path = os.path.join(report_dir, "definition.pbir")
            if not os.path.isfile(pbir_path):
                errores.append("Falta el archivo 'definition.pbir' dentro de la carpeta .Report")
            else:
                try:
                    with open(pbir_path, "r", encoding="utf-8") as f:
                        json.load(f)
                except Exception as e:
                    errores.append(f"Error de sintaxis JSON en 'definition.pbir': {e}")

        if not os.path.isdir(semantic_dir):
            errores.append(f"Falta la carpeta del modelo semántico: '{nombre_base}.SemanticModel'")
        else:
            pbism_path = os.path.join(semantic_dir, "definition.pbism")
            if not os.path.isfile(pbism_path):
                errores.append("Falta el archivo 'definition.pbism' dentro de .SemanticModel")

            # 3. Validar que los archivos TMDL no contengan BOM UTF-8
            for root, _, files in os.walk(semantic_dir):
                for file in files:
                    if file.endswith(".tmdl"):
                        full_tmdl_path = os.path.join(root, file)
                        if verificar_bom_utf8(full_tmdl_path):
                            errores.append(f"Error Fatal: Archivo TMDL con BOM UTF-8 detectado: '{file}' (debe ser UTF-8 sin BOM)")

    return len(errores) == 0, errores

if __name__ == "__main__":
    print("=== Auditor de Integridad PBIP para Pipelines CI/CD ===")
    ruta_a_testear = sys.argv[1] if len(sys.argv) > 1 else "."
    es_valido, lista_errores = validar_proyecto_pbip(ruta_a_testear)

    if es_valido:
        print("[EXITO] La estructura PBIP y codificación TMDL cumplen el estándar 100%.")
    else:
        print(f"[FALLO] Se detectaron {len(lista_errores)} incidencias:")
        for err in lista_errores:
            print(f" - {err}")

