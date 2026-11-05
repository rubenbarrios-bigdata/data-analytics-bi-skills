# Especificación Técnica del DataLayer para E-commerce en GA4

Esta guía define la arquitectura obligatoria de capas de datos (DataLayer) para implementaciones de comercio electrónico según el estándar de Google Analytics 4.

---

## 1. Regla Mandatoria: Reseteo del Objeto E-commerce
Para evitar que datos residuales de interacciones previas (como listas de items o identificadores) contaminen eventos posteriores en aplicaciones de una sola página (SPA) o durante la navegación del usuario, **siempre** debe resetearse el objeto `ecommerce` antes de un nuevo push:

```javascript
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({ ecommerce: null }); // Limpia el objeto previo
window.dataLayer.push({
  event: "nombre_evento",
  ecommerce: {
    // contenido del evento
  }
});
```

---

## 2. Esquema Estándar del Objeto `item` (Ítem de Producto)

Cada producto contenido en el array `items` debe apegarse a la siguiente estructura:

| Campo | Tipo | Requerido | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- | :--- |
| `item_id` | String | Sí* | SKU o identificador único del producto. | `"SKU_12345"` |
| `item_name` | String | Sí* | Nombre descriptivo del producto. | `"Camisa Oxford Slim Fit"` |
| `affiliation` | String | Opcional | Tienda física o partner comercial. | `"Tienda Central"` |
| `coupon` | String | Opcional | Cupón de descuento aplicado al ítem. | `"VERANO2026"` |
| `currency` | String | Opcional | Moneda en formato ISO 4217 (3 letras). | `"USD"`, `"ARS"` |
| `discount` | Number | Opcional | Monto numérico del descuento por unidad. | `5.00` |
| `index` | Number | Opcional | Posición del producto en la lista/grilla. | `1` |
| `item_brand` | String | Opcional | Marca del producto. | `"Acme Brand"` |
| `item_category` | String | Opcional | Categoría principal. | `"Ropa"` |
| `item_category2` | String | Opcional | Subcategoría nivel 2. | `"Hombre"` |
| `item_category3` | String | Opcional | Subcategoría nivel 3. | `"Camisas"` |
| `item_list_id` | String | Opcional | ID de la lista donde se muestra el producto. | `"related_products"` |
| `item_list_name` | String | Opcional | Nombre de la lista o carrusel. | `"Productos Relacionados"` |
| `item_variant` | String | Opcional | Variante específica (talle, color, modelo). | `"Azul / Talle L"` |
| `price` | Number | Recomendado | Precio unitario del producto (sin símbolos). | `49.99` |
| `quantity` | Number | Recomendado | Cantidad de unidades seleccionadas/compradas. | `2` |

*\*Nota: Se requiere al menos `item_id` o `item_name` para que GA4 procese el ítem válidamente.*

---

## 3. Especificación de Eventos Principales del Funnel

### 3.1. `view_item` (Ficha de Producto)
Se dispara cuando el usuario carga la página de detalle de un producto:

```javascript
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({ ecommerce: null });
window.dataLayer.push({
  event: "view_item",
  ecommerce: {
    currency: "USD",
    value: 49.99,
    items: [
      {
        item_id: "SKU_12345",
        item_name: "Camisa Oxford Slim Fit",
        item_brand: "Acme Brand",
        item_category: "Ropa",
        item_category2: "Hombre",
        item_category3: "Camisas",
        item_variant: "Azul / Talle L",
        price: 49.99,
        quantity: 1
      }
    ]
  }
});
```

### 3.2. `add_to_cart` (Agregar al Carrito)
Se dispara cuando el usuario pulsa el botón de añadir al carrito:

```javascript
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({ ecommerce: null });
window.dataLayer.push({
  event: "add_to_cart",
  ecommerce: {
    currency: "USD",
    value: 99.98,
    items: [
      {
        item_id: "SKU_12345",
        item_name: "Camisa Oxford Slim Fit",
        item_brand: "Acme Brand",
        item_category: "Ropa",
        item_variant: "Azul / Talle L",
        price: 49.99,
        quantity: 2
      }
    ]
  }
});
```

### 3.3. `begin_checkout` (Inicio del Proceso de Pago)
Se dispara cuando el usuario ingresa a la primera pantalla del túnel de compra:

```javascript
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({ ecommerce: null });
window.dataLayer.push({
  event: "begin_checkout",
  ecommerce: {
    currency: "USD",
    value: 99.98,
    coupon: "DESC10",
    items: [
      {
        item_id: "SKU_12345",
        item_name: "Camisa Oxford Slim Fit",
        item_brand: "Acme Brand",
        item_category: "Ropa",
        price: 49.99,
        quantity: 2
      }
    ]
  }
});
```

### 3.4. `purchase` (Transacción Completada)
Se dispara una única vez en la página de confirmación/gracias (`Thank You Page`):

```javascript
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({ ecommerce: null });
window.dataLayer.push({
  event: "purchase",
  ecommerce: {
    transaction_id: "ORD_2026_98765", // OBLIGATORIO Y ÚNICO
    value: 104.98,                    // Total neto pagado por el cliente
    tax: 5.00,                        // Impuestos
    shipping: 10.00,                  // Costo de envío
    currency: "USD",                  // Moneda ISO
    coupon: "DESC10",                 // Cupón global de la orden si aplica
    items: [
      {
        item_id: "SKU_12345",
        item_name: "Camisa Oxford Slim Fit",
        item_brand: "Acme Brand",
        item_category: "Ropa",
        price: 49.99,
        quantity: 2
      }
    ]
  }
});
```

