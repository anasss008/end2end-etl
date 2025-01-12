


SELECT *
FROM (-- sql query
SELECT
  id,
  season,
  startTimestamp,
  country,
  home_team as team,
  home_score as score,
  away_score as goal_conceded,
  CASE
    WHEN winner_code = 1 THEN 3
    WHEN winner_code = 2 THEN 0
    ELSE 1
  END as match_point
FROM `foot-analyse`.`foot_data`.`football_results`
WHERE status = 'finished'

UNION ALL
-- sql query
SELECT
  id,
  season,
  startTimestamp,
  country,
  away_team as team,
  away_score as score,
  home_score as goal_conceded,
  CASE
    WHEN winner_code = 1 THEN 0
    WHEN winner_code = 2 THEN 3
    ELSE 1
  END as match_point
FROM `foot-analyse`.`foot_data`.`football_results`
WHERE status = 'finished'
)
ORDER BY startTimestamp, id