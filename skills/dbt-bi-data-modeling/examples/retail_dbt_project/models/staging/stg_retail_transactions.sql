with source_data as (
    select * from {{ source('retail_raw', 'pos_transactions') }}
),

renamed_and_cast as (
    select
        cast(transaction_id as string) as transaction_id,
        cast(customer_id as string) as customer_id,
        cast(store_id as string) as store_id,
        cast(product_sku as string) as product_sku,
        cast(transaction_date as date) as transaction_date,
        cast(quantity as int64) as quantity,
        cast(gross_price as numeric) as gross_amount,
        cast(discount_value as numeric) as discount_amount,
        cast(coalesce(tax_value, 0) as numeric) as tax_amount,
        lower(trim(payment_method)) as payment_method,
        lower(trim(transaction_status)) as transaction_status
    from source_data
)

select * from renamed_and_cast

