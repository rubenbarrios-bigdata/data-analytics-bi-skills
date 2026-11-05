# Plantilla de Diagnóstico y Auditoría de Consultoría BI

Esta plantilla estandariza el relevamiento inicial de necesidades analíticas en clientes corporativos.

---

## 1. Ficha del Proyecto
- **Empresa / Cliente:** [Nombre de la organización]
- **Sponsor Ejecutivo:** [Director General / CFO / CMO]
- **Consultor Responsable:** Rubén David Barrios Bello
- **Fecha de Relevamiento:** Noviembre 2026
- **Horizonte de Decisión:** [Mensual / Semanal / Tiempo Real]

---

## 2. Matriz de Alineación de Objetivos y Métricas

| Pregunta Estratégica de Negocio | Decisión Concreta a Tomar | KPI Principal | Fuentes de Datos Involucradas |
| :--- | :--- | :--- | :--- |
| ¿Qué productos generan el 80% de la utilidad bruta? | Reasignar presupuesto de compras e inventario. | Margen Bruto ($ y %) | Google Sheets / ERP SQL |
| ¿Qué canal de marketing atrae a los clientes más fieles? | Optimizar pauta publicitaria digital. | LTV (Customer Lifetime Value) | GA4 + CRM |
| ¿En qué días/horas colapsa la atención al cliente? | Dimensionar turnos del equipo operativo. | Tiempo de Primera Respuesta | Zendesk / Base de soporte |

---

## 3. Matriz de Auditoría y Calidad de Fuentes

| Atributo de Calidad | Criterio de Verificación | Estado (Aprobado / Crítico) | Acción Correctiva Requerida |
| :--- | :--- | :--- | :--- |
| **Completitud** | Porcentaje de nulos en llaves foráneas (`cliente_id`, `fecha`). | Aprobado (< 0.1% nulos) | Ninguna. |
| **Consistencia de Tipos** | Fechas en formato ISO `AAAA-MM-DD` sin texto mezclado. | Crítico | Aplicar normalización previa en Sheets con regex. |
| **Privacidad (PII)** | Sin exposición de contraseñas, tarjetas o datos sensibles. | Aprobado | Seudonimización con hash SHA-256 aplicada. |
| **Unicidad** | Duplicidad en identificadores de transacción. | Aprobado | Regla de deduplicación en la ingesta. |

