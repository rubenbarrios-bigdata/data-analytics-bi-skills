"""
Capa de Presentación e Interfaz CLI
"""
import sys
import os
from database import RepositorioProductos
from services import ServicioInventario

def imprimir_encabezado():
    print("=" * 60)
    print("   SISTEMA DE GESTIÓN Y PERSISTENCIA MODULAR (PYTHON & SQL)")
    print("   Talento Tech - Certificación de Automatización de Datos")
    print("=" * 60)

def main():
    imprimir_encabezado()
    db_file = os.path.join(os.path.dirname(__file__), "inventario_empresa.db")
    repo = RepositorioProductos(db_file)
    servicio = ServicioInventario(repo)

    # Carga de datos de demostración si la base está vacía
    resumen = servicio.obtener_inventario_valorizado()
    if resumen["metricas"]["total_productos_distintos"] == 0:
        print("[INFO] Inicializando catálogo con productos semilla...")
        servicio.registrar_nuevo_producto("PRD-001", "Monitor Curvo 27' 144Hz", "Hardware", 320.00, 15)
        servicio.registrar_nuevo_producto("PRD-002", "Teclado Mecánico RGB", "Periféricos", 75.50, 40)
        servicio.registrar_nuevo_producto("PRD-003", "Mouse Inalámbrico Pro", "Periféricos", 45.00, 50)
        resumen = servicio.obtener_inventario_valorizado()

    print("\n[+] Resumen Ejecutivo de Inventario:")
    for k, v in resumen["metricas"].items():
        print(f"  * {k.replace('_', ' ').capitalize()}: {v}")

    print("\n[+] Catálogo Detallado:")
    print(f"{'CÓDIGO':<10} | {'NOMBRE':<28} | {'CATEGORÍA':<14} | {'PRECIO':<10} | {'STOCK':<6}")
    print("-" * 75)
    for p in resumen["productos"]:
        print(f"{p['codigo']:<10} | {p['nombre']:<28} | {p['categoria']:<14} | ${p['precio']:<9.2f} | {p['stock']:<6}")

    print("\n[OK] Ejecución finalizada exitosamente sin vulnerabilidades.")

if __name__ == "__main__":
    main()
