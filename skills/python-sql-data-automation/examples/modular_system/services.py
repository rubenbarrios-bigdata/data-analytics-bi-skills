"""
Capa de Lógica de Negocio y Servicios (BLL)
"""
from typing import List, Dict, Any, Optional
from database import RepositorioProductos

class ServicioInventario:
    def __init__(self, repo: RepositorioProductos):
        self.repo = repo

    def registrar_nuevo_producto(self, codigo: str, nombre: str, categoria: str, precio: float, stock: int) -> int:
        # Validaciones de reglas de negocio
        if not codigo or len(codigo) < 3:
            raise ValueError("El código de producto debe tener al menos 3 caracteres.")
        if precio <= 0:
            raise ValueError("El precio debe ser un valor positivo estrictamente mayor a 0.")
        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")

        existente = self.repo.buscar_por_codigo(codigo)
        if existente:
            raise ValueError(f"Ya existe un producto registrado con el código '{codigo}'.")

        return self.repo.agregar_producto(codigo, nombre, categoria, precio, stock)

    def obtener_inventario_valorizado(self) -> Dict[str, Any]:
        productos = self.repo.listar_todos()
        total_items = sum(p["stock"] for p in productos)
        valor_total_inventario = sum(p["precio"] * p["stock"] for p in productos)
        categorias = {p["categoria"] for p in productos}

        return {
            "productos": productos,
            "metricas": {
                "total_productos_distintos": len(productos),
                "unidades_totales": total_items,
                "valor_total_usd": round(valor_total_inventario, 2),
                "categorias_activas": sorted(list(categorias))
            }
        }

