/**
 * Colección Oficial de Payloads de DataLayer para GA4 E-commerce
 * Autor: Rubén David Barrios Bello - Data Analyst & BI Developer
 * Certificación: Analytics Way (Lorena Flores Saldías)
 * 
 * Regla de oro: Siempre resetear ecommerce a null antes de cada push.
 */

// 1. Vista de catálogo / Lista de productos (view_item_list)
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({ ecommerce: null });
window.dataLayer.push({
  event: "view_item_list",
  ecommerce: {
    item_list_id: "category_ropa_hombre",
    item_list_name: "Ropa Masculina - Colección Primavera",
    items: [
      {
        item_id: "SKU_7701",
        item_name: "Chaqueta Denim Clásica",
        item_brand: "DenimCo",
        item_category: "Ropa",
        item_category2: "Hombre",
        item_category3: "Chaquetas",
        price: 89.90,
        index: 1
      },
      {
        item_id: "SKU_7702",
        item_name: "Remera Algodón Pima",
        item_brand: "BasicStyle",
        item_category: "Ropa",
        item_category2: "Hombre",
        item_category3: "Remeras",
        price: 24.50,
        index: 2
      }
    ]
  }
});

// 2. Clic en producto de una lista (select_item)
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({ ecommerce: null });
window.dataLayer.push({
  event: "select_item",
  ecommerce: {
    item_list_id: "category_ropa_hombre",
    item_list_name: "Ropa Masculina - Colección Primavera",
    items: [
      {
        item_id: "SKU_7701",
        item_name: "Chaqueta Denim Clásica",
        item_brand: "DenimCo",
        item_category: "Ropa",
        item_category2: "Hombre",
        item_category3: "Chaquetas",
        price: 89.90,
        index: 1
      }
    ]
  }
});

// 3. Ficha de detalle de producto (view_item)
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({ ecommerce: null });
window.dataLayer.push({
  event: "view_item",
  ecommerce: {
    currency: "USD",
    value: 89.90,
    items: [
      {
        item_id: "SKU_7701",
        item_name: "Chaqueta Denim Clásica",
        item_brand: "DenimCo",
        item_category: "Ropa",
        item_category2: "Hombre",
        item_category3: "Chaquetas",
        item_variant: "Azul Lavado / M",
        price: 89.90,
        quantity: 1
      }
    ]
  }
});

// 4. Agregar producto al carrito (add_to_cart)
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({ ecommerce: null });
window.dataLayer.push({
  event: "add_to_cart",
  ecommerce: {
    currency: "USD",
    value: 89.90,
    items: [
      {
        item_id: "SKU_7701",
        item_name: "Chaqueta Denim Clásica",
        item_brand: "DenimCo",
        item_category: "Ropa",
        item_variant: "Azul Lavado / M",
        price: 89.90,
        quantity: 1
      }
    ]
  }
});

// 5. Iniciar Proceso de Pago (begin_checkout)
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({ ecommerce: null });
window.dataLayer.push({
  event: "begin_checkout",
  ecommerce: {
    currency: "USD",
    value: 114.40,
    coupon: "PRIMAVERA10",
    items: [
      {
        item_id: "SKU_7701",
        item_name: "Chaqueta Denim Clásica",
        price: 89.90,
        quantity: 1
      },
      {
        item_id: "SKU_7702",
        item_name: "Remera Algodón Pima",
        price: 24.50,
        quantity: 1
      }
    ]
  }
});

// 6. Transacción Exitosa / Compra (purchase)
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({ ecommerce: null });
window.dataLayer.push({
  event: "purchase",
  ecommerce: {
    transaction_id: "ORD-2026-99014",
    value: 124.40,
    tax: 10.00,
    shipping: 10.00,
    currency: "USD",
    coupon: "PRIMAVERA10",
    items: [
      {
        item_id: "SKU_7701",
        item_name: "Chaqueta Denim Clásica",
        price: 89.90,
        quantity: 1
      },
      {
        item_id: "SKU_7702",
        item_name: "Remera Algodón Pima",
        price: 24.50,
        quantity: 1
      }
    ]
  }
});

