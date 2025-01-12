WITH total_won_points AS (
SELECT
       season,
       team,
       sum(match_point) as total_point,
       sum(score) as scored_goals,
       sum(goal_conceded) as conceded_goals
FROM `foot-analyse`.`foot_data`.`won_point`
WHERE country = 'Morocco'
GROUP BY season, team
)

SELECT *,
       row_number() over(PARTITION BY season ORDER BY total_point desc, scored_goals desc, conceded_goals asc) as rank
FROM total_won_points
ORDER BY season asc