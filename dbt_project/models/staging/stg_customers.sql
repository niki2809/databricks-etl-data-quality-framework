with source as (
    select * from {{ source('raw', 'raw_customers') }}
)

select
    cast(customer_id as int)    as customer_id,
    trim(first_name)            as first_name,
    trim(last_name)             as last_name,
    lower(trim(email))          as email,
    cast(signup_date as date)   as signup_date,
    trim(country)               as country
from source