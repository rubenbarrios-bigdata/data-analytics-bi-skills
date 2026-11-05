{{ config(
    materialized = 'table',
    cluster_by = ["customer_city", "loyalty_tier"]
) }}

with customer_source as (
    select * from {{ source('retail_raw', 'crm_customers') }}
),

curated_customers as (
    select
        cast(customer_id as string) as customer_key,
        trim(first_name) as first_name,
        trim(last_name) as last_name,
        lower(trim(email)) as email,
        coalesce(city, 'Desconocida') as customer_city,
        coalesce(loyalty_tier, 'Regular') as loyalty_tier,
        cast(first_purchase_date as date) as first_purchase_date
    from customer_source
)

select * from curated_customers

