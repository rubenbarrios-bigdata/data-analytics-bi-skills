{{ config(
    materialized = 'table',
    partition_by = {
      "field": "transaction_date",
      "data_type": "date",
      "granularity": "day"
    },
    cluster_by = ["store_id", "customer_id"]
) }}

with reconciled_sales as (
    select * from {{ ref('int_sales_reconciliation') }}
),

aggregated_daily as (
    select
        to_hex(md5(concat(store_id, '|', cast(transaction_date as string), '|', product_sku))) as sale_daily_key,
        transaction_date,
        store_id,
        customer_id,
        product_sku,
        sum(quantity) as total_units_sold,
        sum(gross_amount) as total_gross_sales,
        sum(discount_amount) as total_discounts,
        sum(net_sales_amount) as total_net_sales,
        sum(tax_amount) as total_taxes,
        count(distinct transaction_id) as total_orders
    from reconciled_sales
    group by 1, 2, 3, 4, 5
)

select * from aggregated_daily

