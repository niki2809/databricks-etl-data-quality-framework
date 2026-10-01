with source as (
    select * from {{ source('raw', 'raw_orders') }}
)

select
    cast(order_id as int)          as order_id,
    cast(customer_id as int)       as customer_id,
    cast(order_date as date)       as order_date,
    cast(order_amount as double)   as order_amount,
    upper(trim(order_status))      as order_status
from source