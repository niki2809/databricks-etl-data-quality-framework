-- The test passes when this query returns zero rows.
select *
from {{ ref('stg_orders') }}
where order_amount < 0
