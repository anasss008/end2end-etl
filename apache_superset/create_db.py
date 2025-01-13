import psycopg2
import time

# Define connection parameters
admin_conn_info = "host=postgres dbname=airflow user=airflow password=airflow"
role_name = "superset"
db_name = "superset"
role_password = "superset"


def create_db_role():
    # Sleep 1 minute
    time.sleep(60)
    # Create the database
    conn = psycopg2.connect(admin_conn_info)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE {db_name};")
    cur.close()
    conn.close()

    # Then connect again to create user and grant privileges
    with psycopg2.connect(admin_conn_info) as conn:
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute(f"CREATE USER {role_name} WITH PASSWORD '{role_password}';")
            cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {role_name};")


create_db_role()
print("DB created successfully!")