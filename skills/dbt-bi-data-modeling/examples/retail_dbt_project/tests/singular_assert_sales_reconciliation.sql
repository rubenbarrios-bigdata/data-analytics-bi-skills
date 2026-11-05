-- Test Singular: Reconciliación Contable de Venta Neta
-- dbt marca este test como fallido si la query devuelve 1 o más filas con discrepancia contable.

with auditoria as (
    select
        sale_daily_key,
        total_gross_sales,
        total_discounts,
        total_net_sales,
        round(total_gross_sales - total_discounts, 2) as venta_neta_esperada
    from {{ ref('fct_sales_daily') }}
)

select
    sale_daily_key,
    total_gross_sales,
    total_discounts,
    total_net_sales,
    venta_neta_esperada,
    abs(total_net_sales - venta_neta_esperada) as error_contable
from auditoria
where abs(total_net_sales - venta_neta_esperada) > 0.01

