#!/usr/bin/env python3
"""
Pipeline ETL Orientado a Objetos (POO) y Auditoría Analítica
------------------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Certificación: Experto en Análisis y Visualización de Datos + IA (DataBoosters Academy)
Propósito: Implementar el proceso ETL completo (limpieza de texto, transformación de fechas,
búsqueda/enriquecimiento por catálogo y lógica condicional de negocio) usando Programación
Orientada a Objetos (POO) y manejo seguro de archivos en Python.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import csv
import io


@dataclass
class TransactionRecord:
    """Representa un registro de venta validado y enriquecido mediante POO."""
    order_id: str
    raw_customer_name: str
    order_date_str: str
    ship_date_str: str
    category_code: str
    gross_sales: float
    discount_rate: float
    shipping_cost: float

    # Campos derivados en el proceso ETL
    clean_customer_name: str = field(init=False)
    order_year: int = field(init=False)
    order_month: int = field(init=False)
    lead_time_days: int = field(init=False)
    category_name: str = field(init=False)
    net_sales: float = field(init=False)
    customer_tier: str = field(init=False)

    def apply_etl_transformations(self, category_lookup: Dict[str, str]) -> None:
        """Aplica funciones de Texto, Fecha, Búsqueda y Lógica sobre el registro."""
        # 1. Transformación de Texto: limpieza de espacios y formato Title Case
        self.clean_customer_name = " ".join(self.raw_customer_name.strip().split()).title()

        # 2. Transformación de Fecha: parseo y cálculo de días transcurridos (Lead Time)
        dt_order = datetime.strptime(self.order_date_str.strip(), "%Y-%m-%d")
        dt_ship = datetime.strptime(self.ship_date_str.strip(), "%Y-%m-%d")
        self.order_year = dt_order.year
        self.order_month = dt_order.month
        self.lead_time_days = max(0, (dt_ship - dt_order).days)

        # 3. Función de Búsqueda: cruce contra catálogo de categorías (equivalente a XLOOKUP / JOIN)
        self.category_name = category_lookup.get(self.category_code.strip().upper(), "Sin Categoría")

        # 4. Lógica Condicional y Cálculo de KPIs
        self.net_sales = round(self.gross_sales * (1.0 - self.discount_rate), 2)
        if self.net_sales >= 1000.0:
            self.customer_tier = "VIP"
        elif self.net_sales >= 300.0:
            self.customer_tier = "Regular"
        else:
            self.customer_tier = "Estandar"


class AnalyticsETLPipeline:
    """Motor ETL modular basado en POO para limpieza, enriquecimiento y resumen de KPIs."""

    def __init__(self, category_catalog: Optional[Dict[str, str]] = None) -> None:
        self.category_catalog: Dict[str, str] = category_catalog or {
            "TECH": "Tecnología",
            "FURN": "Mobiliario",
            "OFF": "Insumos de Oficina"
        }
        self.records: List[TransactionRecord] = []

    def load_from_csv_stream(self, csv_content: str) -> int:
        """Lee registros desde un flujo o archivo CSV y ejecuta el pipeline ETL."""
        reader = csv.DictReader(io.StringIO(csv_content.strip()))
        loaded = 0
        for row in reader:
            rec = TransactionRecord(
                order_id=row["order_id"],
                raw_customer_name=row["customer_name"],
                order_date_str=row["order_date"],
                ship_date_str=row["ship_date"],
                category_code=row["category_code"],
                gross_sales=float(row["gross_sales"]),
                discount_rate=float(row["discount_rate"]),
                shipping_cost=float(row["shipping_cost"]),
            )
            rec.apply_etl_transformations(self.category_catalog)
            self.records.append(rec)
            loaded += 1
        return loaded

    def compute_executive_kpis(self) -> Dict[str, Any]:
        """Calcula indicadores clave de negocio (KPIs) auditados."""
        if not self.records:
            return {}
        total_gross = round(sum(r.gross_sales for r in self.records), 2)
        total_net = round(sum(r.net_sales for r in self.records), 2)
        avg_lead_time = round(sum(r.lead_time_days for r in self.records) / len(self.records), 2)
        by_category: Dict[str, float] = {}
        for r in self.records:
            by_category[r.category_name] = round(by_category.get(r.category_name, 0.0) + r.net_sales, 2)

        return {
            "total_orders": len(self.records),
            "total_gross_sales": total_gross,
            "total_net_sales": total_net,
            "avg_lead_time_days": avg_lead_time,
            "net_sales_by_category": by_category,
        }


if __name__ == "__main__":
    sample_csv = """order_id,customer_name,order_date,ship_date,category_code,gross_sales,discount_rate,shipping_cost
ORD-1001,  ruben   barrios  ,2026-10-01,2026-10-04,TECH,1500.00,0.10,25.00
ORD-1002,MARIA GOMEZ,2026-10-05,2026-10-07,FURN,600.00,0.05,40.00
ORD-1003,carlos perez,2026-10-10,2026-10-12,OFF,180.00,0.00,12.00
"""
    pipeline = AnalyticsETLPipeline()
    count = pipeline.load_from_csv_stream(sample_csv)
    kpis = pipeline.compute_executive_kpis()
    print("=== Pipeline ETL Orientado a Objetos (POO) ===")
    print(f"[EXITO] Registros procesados y normalizados: {count}")
    print(f"[KPIs] Resumen Ejecutivo: {kpis}")
