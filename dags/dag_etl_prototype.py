import os
from datetime import datetime, timedelta
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG
from tasks.extract import (
    extract_from_econvention,
)
from tasks.transform import transform_from_econvention_to_oscar
from tasks.load import load

with DAG(
    "etl_prototype",
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    description="A prototype ETL process to synchronize data between Oscar and eConvention",
    schedule=timedelta(days=1),
    start_date=datetime(2025, 7, 1),
    catchup=False,
    tags=["prototype"],
) as dag:
    AIRFLOW_HOME_PATH = os.getenv("AIRFLOW_HOME", "/home/user/airflow")
    INPUT_FILE_PATH = f"{AIRFLOW_HOME_PATH}/data/test_econvention.json"
    curl_local = BashOperator(
        task_id="curl_local_file",
        bash_command=f"curl file://{AIRFLOW_HOME_PATH}/data/test_econvention.json",
        do_xcom_push=True,
        dag=dag,
    )
    raw_data = extract_from_econvention(INPUT_FILE_PATH)
    transformed_data = transform_from_econvention_to_oscar(raw_data)
    loaded_data = load(transformed_data)

    print_result = BashOperator(
        task_id="print_result",
        bash_command="echo '{{ ti.xcom_pull(task_ids=\"curl_load_file\") }}'",
        dag=dag,
    )

    curl_local >> raw_data >> transformed_data >> loaded_data >> print_result # pylint: disable=pointless-statement
