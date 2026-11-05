#!/usr/bin/env python3
"""
Cliente de Integración con Fabric y Power BI REST API (Service Principal)
-------------------------------------------------------------------------
Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
Área: Power BI DevOps & Microsoft Fabric CI/CD
Propósito: Obtener tokens JWT de Microsoft Entra ID mediante Client Credentials
y ejecutar operaciones de CI/CD (refresco de SemanticModels o trigger de despliegues).
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional

def obtener_token_entra_id(tenant_id: str, client_id: str, client_secret: str) -> Optional[str]:
    """Obtiene un Bearer Token OAuth 2.0 para Power BI REST API."""
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://analysis.windows.net/powerbi/api/.default"
    }

    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(token_url, data=data, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            return res_json.get("access_token")
    except Exception as e:
        print(f"[ERROR] Falla de autenticación en Microsoft Entra ID: {e}")
        return None

def disparar_refresco_modelo(token: str, workspace_id: str, dataset_id: str) -> Dict[str, Any]:
    """Dispara un refresco desatendido en Power BI / Fabric Service."""
    api_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = json.dumps({"notifyOption": "MailOnFailure"}).encode("utf-8")
    req = urllib.request.Request(api_url, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as response:
            return {"status": "success", "http_code": response.status}
    except urllib.error.HTTPError as e:
        return {"status": "error", "http_code": e.code, "message": e.read().decode("utf-8")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("Módulo Fabric REST Deployer cargado exitosamente.")
    print("Listo para autenticar con Service Principal en pipelines CI/CD.")

