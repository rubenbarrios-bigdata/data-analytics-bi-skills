#!/usr/bin/env python3
"""
Cliente de GA4 Measurement Protocol (Server-to-Server)
------------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Propósito: Despachar eventos offline o de backend hacia GA4 utilizando la API
oficial del Measurement Protocol, soportando endpoint de validación y producción.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

MEASUREMENT_PROTOCOL_PROD_URL = "https://www.google-analytics.com/mp/collect"
MEASUREMENT_PROTOCOL_DEBUG_URL = "https://www.google-analytics.com/debug/mp/collect"

def send_ga4_event(
    api_secret: str,
    measurement_id: str,
    client_id: str,
    event_name: str,
    event_params: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    debug: bool = True
) -> Dict[str, Any]:
    """
    Envía un evento a Google Analytics 4 mediante Measurement Protocol.
    
    :param api_secret: API Secret generado en Administrador > Flujos de datos > Measurement Protocol API secrets.
    :param measurement_id: Identificador de flujo (formato G-XXXXXXXXXX).
    :param client_id: Identificador único de cliente/dispositivo (pseudonymized ID).
    :param event_name: Nombre del evento en snake_case (ej. 'purchase', 'offline_lead').
    :param event_params: Diccionario de parámetros del evento.
    :param user_id: ID interno de usuario autenticado (opcional).
    :param debug: Si es True, utiliza el endpoint de depuración (/debug/mp/collect) para validar sintaxis.
    :return: Respuesta parseada de la API.
    """
    base_url = MEASUREMENT_PROTOCOL_DEBUG_URL if debug else MEASUREMENT_PROTOCOL_PROD_URL
    url = f"{base_url}?api_secret={api_secret}&measurement_id={measurement_id}"

    payload = {
        "client_id": client_id,
        "events": [
            {
                "name": event_name,
                "params": event_params or {}
            }
        ]
    }

    if user_id:
        payload["user_id"] = user_id

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            if debug:
                return json.loads(res_body) if res_body else {"status": "ok", "validation_messages": []}
            return {"status": "ok", "http_code": response.status}
    except urllib.error.HTTPError as e:
        error_content = e.read().decode("utf-8")
        return {"status": "error", "http_code": e.code, "message": error_content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("Módulo GA4 Measurement Protocol cargado exitosamente.")
    print("Ejemplo de uso:")
    print("res = send_ga4_event('API_KEY', 'G-12345678', 'client_123', 'offline_conversion', {'value': 100})")

