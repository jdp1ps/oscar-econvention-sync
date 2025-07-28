from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG
from tasks.etl import (
    extract_from_econvention,
    transform_from_econvention_to_oscar,
    load,
)

import os

with DAG(
    "etl_prototype",
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    description="A prototype which enables to ETL process in order to synchronize data between Oscar and eConvention",
    schedule=timedelta(days=1),
    start_date=datetime(2025, 7, 1),
    catchup=False,
    tags=["prototype"],
) as dag:

    airflow_path = os.getenv("AIRFLOW_HOME", "/home/user/airflow")
    input_file_path = f"{airflow_path}/data/test_econvention.json"

    curl_local = BashOperator(
        task_id="curl_local_file",
        bash_command=f"curl file://{airflow_path}/data/test_econvention.json",
        do_xcom_push=True,
        dag=dag,
    )
    raw_data = extract_from_econvention(input_file_path)
    transformed_data = transform_from_econvention_to_oscar(raw_data)
    loaded_data = load(transformed_data)

    print_result = BashOperator(
        task_id="print_result",
        bash_command="echo '{{ ti.xcom_pull(task_ids=\"curl_load_file\") }}'",
        dag=dag,
    )

    curl_local >> raw_data >> transformed_data >> loaded_data >> print_result
