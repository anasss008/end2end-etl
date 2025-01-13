WITH total_won_points AS (
SELECT
       season,
       team,
       tournament,
       count(*) as games,
       sum(match_point) as total_point,
       sum(score) as scored_goals,
       sum(goal_conceded) as conceded_goals
FROM {{ ref('won_point') }}
GROUP BY tournament, season, team
)

SELECT *,
       Dense_Rank() over(PARTITION BY season ORDER BY total_point desc, scored_goals desc, conceded_goals asc) as rank
FROM total_won_points
ORDER BY season asc, rank asc
