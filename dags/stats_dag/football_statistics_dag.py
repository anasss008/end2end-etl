import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.results_scraper import ResultScraper, get_events, save_to_json
from utils.statistics_scraper import StatsScraper
from utils.highlights_scraper import HighlightsScraper
from google.cloud import bigquery, storage
from airflow.decorators import dag, task
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.exceptions import AirflowSkipException
from datetime import datetime, timedelta
import logging
import queue
import json
import concurrent.futures


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

ids_queue = queue.Queue()
matches_statistics = queue.Queue()

ids_queue2 = queue.Queue()
matches_highlights = queue.Queue()

DATA_DIR = "./scraped_data/"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


@task(task_id='get_json_data')
def get_json_data(**context):
    execution_date = context['ds']
    results_path = os.path.join(DATA_DIR, f"results/{execution_date}.json")
    if os.path.isfile(results_path):
        json_data = json.load(open(results_path))

    else:
        logger.info("Getting results..")
        scraper = ResultScraper()
        json_data = scraper.get_json(execution_date)
        save_to_json(json_data, execution_date, results_path)

    return json_data


@task(task_id='extract_desired_info')
def extract_desired_info(json_data, **context):
    ds = context["ds"]
    desired_info = get_events(json_data, ds)
    return desired_info


@task(task_id='prepare_to_load')
def prepare_to_load(desired_data, **context):
    ds = context["ds"]
    # Step 1: Save desired_data to a local JSON file in newline-delimited JSON format
    temp_file_name = f"all_data_{ds}.json"
    with open(temp_file_name, 'w') as f:
        for record in desired_data:
            json.dump(record, f)
            f.write('\n')  # Each record on a new line

    return temp_file_name


@task(task_id='load_to_bq')
def load_to_bq(temp_file_name, **context):
    ds = context["ds"]
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("BQ_DATASET_ID")
    table_id = os.getenv("BQ_TABLE_ID")
    table = f"{project_id}.{dataset_id}.{table_id}"
    bucket_name = os.getenv("BUCKET_ID")  # Replace with your GCS bucket

    # Initialize BigQuery and GCS clients
    bq_client = bigquery.Client()
    storage_client = storage.Client()


    # Step 2: Upload the file to GCS
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(temp_file_name)
    blob.upload_from_filename(temp_file_name)
    logging.info(f"Uploaded file to GCS: gs://{bucket_name}/{temp_file_name}")

    # Step 3: Configure the load job and load the data into BigQuery
    table_ref = bq_client.dataset(dataset_id).table(table_id)
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        max_bad_records=10  # Allow tolerance for minor issues
    )

    load_job = bq_client.load_table_from_uri(
        f"gs://{bucket_name}/{temp_file_name}",
        table_ref,
        job_config=job_config, 
    )
    logging.info("Starting BigQuery batch load job...")
    load_job.result()  # Wait for the load job to complete
    logging.info(f"Batch load job completed. Loaded data into {table}.")

    # Step 4: Clean up temporary files
    blob.delete()  # Delete the file from GCS
    os.remove(temp_file_name)  # Delete the local temporary file
    logging.info("Cleaned up temporary files.")


@task.bash
def run_dbt() -> str:
    return '''
    cd /opt/airflow/ || exit 1
    dbt run --profiles-dir /opt/airflow
    '''



@dag(
    dag_id="football_results_dag_v2.1",
    schedule_interval='@daily',
    start_date=datetime(2022, 8, 1),
    catchup=False,
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'retries': 3,  # Number of retries for all tasks in the DAG
        'retry_delay': timedelta(minutes=5),  # Delay between retries for all tasks in the DAG
    }
)
def football_results_dag():
    #get raw data from Sofascore
    raw_data_json = get_json_data()
    # extract desired informations from matches
    desired_info = extract_desired_info(raw_data_json)
    # Prepare data to be loaded to BigQuery
    prepared_data = prepare_to_load(desired_info)
    # Load data to BigQuery
    load_2bq = load_to_bq(prepared_data)
    # Run DBT dag
    load_2bq >> run_dbt()    

# start the dag
football_results_dag()
