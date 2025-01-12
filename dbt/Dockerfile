FROM python:3.13.1-slim-bullseye

WORKDIR /usr/app/dbt

# Install dbt-bigquery
RUN apt-get -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false update && \
    apt-get install -y git && \
    apt-get clean && \
    pip install dbt-bigquery

# Command to run when container starts
CMD tail -f /dev/null