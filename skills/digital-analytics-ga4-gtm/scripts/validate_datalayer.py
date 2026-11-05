#!/usr/bin/env python3
"""
Validador de DataLayer de Google Analytics 4 (GA4)
-------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Propósito: Validar que los payloads o volcados del dataLayer cumplan con la
taxonomía oficial de GA4, la estructura de items y las reglas de e-commerce.
"""

import json
import sys
from typing import Dict, Any, List, Tuple

VALID_ECOMMERCE_EVENTS = {
    "view_item_list",
    "select_item",
    "view_item",
    "add_to_cart",
    "remove_from_cart",
    "view_cart",
    "begin_checkout",
    "add_shipping_info",
    "add_payment_info",
    "purchase",
    "refund"
}

VALID_CURRENCIES = {"USD", "EUR", "ARS", "MXN", "CLP", "COP", "BRL", "GBP"}

def validate_item(item: Dict[str, Any], index: int) -> List[str]:
    errors = []
    if not isinstance(item, dict):
        return [f"El ítem en la posición {index} debe ser un objeto/diccionario."]
    
    if "item_id" not in item and "item_name" not in item:
        errors.append(f"Ítem [{index}]: Debe incluir al menos 'item_id' o 'item_name'.")
    
    if "price" in item:
        price = item["price"]
        if not isinstance(price, (int, float)):
            errors.append(f"Ítem [{index}]: 'price' debe ser numérico (int/float), recibido: {type(price).__name__} ('{price}').")
        elif price < 0:
            errors.append(f"Ítem [{index}]: 'price' no puede ser negativo ({price}).")

    if "quantity" in item:
        qty = item["quantity"]
        if not isinstance(qty, int):
            errors.append(f"Ítem [{index}]: 'quantity' debe ser un número entero (int), recibido: {type(qty).__name__}.")
        elif qty <= 0:
            errors.append(f"Ítem [{index}]: 'quantity' debe ser mayor a 0 ({qty}).")

    return errors

def validate_datalayer_event(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors = []
    event_name = payload.get("event")

    if not event_name:
        errors.append("El objeto dataLayer no contiene la clave obligatoria 'event'.")
        return False, errors

    if event_name in VALID_ECOMMERCE_EVENTS:
        if "ecommerce" not in payload:
            errors.append(f"El evento de e-commerce '{event_name}' requiere la propiedad 'ecommerce'.")
            return False, errors

        ecom = payload["ecommerce"]
        if not isinstance(ecom, dict):
            errors.append(f"La propiedad 'ecommerce' debe ser un objeto diccionario, recibido: {type(ecom).__name__}.")
            return False, errors

        # Validaciones específicas de purchase
        if event_name == "purchase":
            if "transaction_id" not in ecom or not str(ecom["transaction_id"]).strip():
                errors.append("Evento 'purchase' requiere un 'transaction_id' obligatorio y no vacío.")
            if "value" not in ecom or not isinstance(ecom["value"], (int, float)):
                errors.append("Evento 'purchase' requiere un 'value' numérico válido.")
            if "currency" not in ecom:
                errors.append("Evento 'purchase' requiere 'currency' (código ISO de 3 letras).")
            elif ecom["currency"] not in VALID_CURRENCIES:
                errors.append(f"Moneda '{ecom['currency']}' no habitual o no verificada.")

        # Validación del array de items si está presente
        if "items" in ecom:
            items = ecom["items"]
            if not isinstance(items, list):
                errors.append("La propiedad 'items' dentro de ecommerce debe ser un array/lista.")
            elif len(items) == 0 and event_name in {"purchase", "begin_checkout", "add_to_cart"}:
                errors.append(f"El evento '{event_name}' no debería tener un array de 'items' vacío.")
            else:
                for idx, itm in enumerate(items):
                    errors.extend(validate_item(itm, idx))
        elif event_name in {"view_item", "add_to_cart", "purchase"}:
            errors.append(f"El evento '{event_name}' requiere el array 'items' dentro de 'ecommerce'.")

    return len(errors) == 0, errors

def main():
    print("=== Validador de DataLayer GA4 ===")
    sample_payload = {
        "event": "purchase",
        "ecommerce": {
            "transaction_id": "T_12345",
            "value": 99.50,
            "currency": "USD",
            "tax": 4.50,
            "shipping": 5.00,
            "items": [
                {
                    "item_id": "SKU_998",
                    "item_name": "Pantalón Chino Beige",
                    "price": 45.00,
                    "quantity": 2
                }
            ]
        }
    }
    
    is_valid, errors = validate_datalayer_event(sample_payload)
    if is_valid:
        print("[EXITO] Payload de prueba es 100% compatible con GA4 E-commerce.")
    else:
        print(f"[ERROR] Se encontraron {len(errors)} inconsistencias:")
        for err in errors:
            print(f" - {err}")

if __name__ == "__main__":
    main()

