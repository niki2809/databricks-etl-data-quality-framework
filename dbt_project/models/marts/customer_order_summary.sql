with customers as (
    select * from {{ ref('stg_customers') }}
),
orders as (
    select * from {{ ref('stg_orders') }}
),
agg as (
    select
        customer_id,
        count(order_id)                as total_orders,
        sum(order_amount)              as total_spent,
        round(avg(order_amount), 2)    as avg_order_value,
        max(order_date)                as last_order_date
    from orders
    where order_status <> 'CANCELLED'
    group by customer_id
)

select
    c.customer_id,
    concat(c.first_name, ' ', c.last_name) as customer_name,
    c.email,
    c.country,
    coalesce(a.total_orders, 0)       as total_orders,
    coalesce(a.total_spent, 0.0)      as total_spent,
    coalesce(a.avg_order_value, 0.0)  as avg_order_value,
    a.last_order_date
from customers c
left join agg a on a.customer_id = c.customer_id
