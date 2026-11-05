#!/usr/bin/env python3
"""
Generador de Documentación y Tests YAML para dbt
------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Propósito: Construir automáticamente la estructura schema.yml con
pruebas genéricas (unique, not_null) y descripciones para modelos dbt.
"""

from typing import List, Dict, Any

def generar_schema_yaml(
    nombre_modelo: str,
    descripcion_modelo: str,
    columnas: List[Dict[str, Any]]
) -> str:
    """Genera el bloque YAML formateado para dbt."""
    lineas = [
        "version: 2",
        "",
        "models:",
        f"  - name: {nombre_modelo}",
        f"    description: \"{descripcion_modelo}\"",
        "    columns:"
    ]

    for col in columnas:
        lineas.append(f"      - name: {col['name']}")
        if "description" in col:
            lineas.append(f"        description: \"{col['description']}\"")
        if "tests" in col and col["tests"]:
            lineas.append("        tests:")
            for t in col["tests"]:
                lineas.append(f"          - {t}")

    return "\n".join(lineas)

if __name__ == "__main__":
    cols_ejemplo = [
        {"name": "transaction_id", "description": "Surrogate key única de la transacción.", "tests": ["unique", "not_null"]},
        {"name": "customer_id", "description": "Identificador del cliente comprador.", "tests": ["not_null"]},
        {"name": "transaction_date", "description": "Fecha del evento de compra.", "tests": ["not_null"]},
        {"name": "net_amount", "description": "Importe total neto facturado.", "tests": ["not_null"]}
    ]
    yaml_salida = generar_schema_yaml("stg_retail_transactions", "Capa de staging para ventas de retail.", cols_ejemplo)
    print(yaml_salida)

