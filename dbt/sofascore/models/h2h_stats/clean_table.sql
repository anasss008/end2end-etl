with cte as (
  select *,
    row_number() over(partition by id) as rn
  from {{ source('foot_data', 'results') }}
)

select * EXCEPT(rn)
from cte
where rn = 1