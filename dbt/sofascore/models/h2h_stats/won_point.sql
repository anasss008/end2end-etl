{% set teams = ['home_team', 'away_team'] %}
{% set teams_dict = {
  'home_team': {
    'team': 'home_team',
    'score': 'home_score',
    'goal_conceded': 'away_score',
    'points': [3, 0, 1]
  },

  'away_team': {
    'team': 'away_team',
    'score': 'away_score',
    'goal_conceded': 'home_score',
    'points': [0, 3, 1]
  }
} 
%}

SELECT *
FROM (
{%- for team in teams -%}
{%- set team_info = teams_dict[team] -%}
-- sql query
SELECT
  id,
  season,
  startTimestamp,
  country,
  tournament,
  {{ team_info['team'] }} as team,
  {{ team_info['score'] }} as score,
  {{ team_info['goal_conceded'] }} as goal_conceded,
  CASE
    WHEN winner_code = 1 THEN {{ team_info['points'][0] }}
    WHEN winner_code = 2 THEN {{ team_info['points'][1] }}
    ELSE {{ team_info['points'][2] }}
  END as match_point
FROM {{ ref('clean_table') }}
WHERE status = 'finished'
{% if not loop.last %}
UNION ALL
{% endif %}
{%- endfor -%}

)
ORDER BY startTimestamp, id
