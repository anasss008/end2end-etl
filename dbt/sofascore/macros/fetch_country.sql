{% macro fetch_country(country_name) %}
    {% set query %}
        SELECT * FROM {{ source('foot_data', 'results') }}
        WHERE country = '{{ country_name }}'
    {% endset %}
    
    {{ log('Executing query for country: ' ~ country_name, info=True) }}
    {% set results = run_query(query) %}
    
    {% do log('Query results: ' ~ results.rows, info=True) %}
    
    {{ return(results) }}
{% endmacro %}