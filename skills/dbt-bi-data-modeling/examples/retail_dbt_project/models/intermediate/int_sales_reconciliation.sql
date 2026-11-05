with base_transactions as (
    select * from {{ ref('stg_retail_transactions') }}
    where transaction_status = 'completed'
),

calculated_metrics as (
    select
        transaction_id,
        customer_id,
        store_id,
        product_sku,
        transaction_date,
        quantity,
        gross_amount,
        discount_amount,
        tax_amount,
        -- Regla contable de venta neta
        round(gross_amount - discount_amount, 2) as net_sales_amount,
        payment_method
    from base_transactions
)

select * from calculated_metrics

