FROM apache/superset:latest

USER root

RUN pip install mysqlclient sqlalchemy-bigquery

ENV ADMIN_USERNAME $ADMIN_USERNAME
ENV ADMIN_EMAIL $ADMIN_EMAIL
ENV ADMIN_PASSWORD $ADMIN_PASSWORD

COPY ./apache_superset/superset-init.sh /superset-init.sh
RUN chmod +x /superset-init.sh

COPY ./apache_superset/superset_config.py /app/
ENV SUPERSET_CONFIG_PATH /app/superset_config.py

COPY ./apache_superset/create_db.py /app/

USER superset
ENTRYPOINT [ "/superset-init.sh" ]