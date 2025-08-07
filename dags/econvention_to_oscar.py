from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from tasks.extract import extract_from_econvention
from tasks.transform import transform_from_econvention_to_oscar
from tasks.load import load
from utils.config import OSCAR_HOME_PATH


# pylint: disable=unexpected-keyword-arg
with DAG(
    dag_id="econvention_to_oscar",
    start_date=datetime(2025, 7, 30),
    schedule=None,
    catchup=False,
    tags=["api", "json", "etl", "post"],
) as econvention_to_oscar:

    raw_data = extract_from_econvention()
    transformed_data = transform_from_econvention_to_oscar(raw_data)
    loaded_data = load(transformed_data)

    import_activity_oscar = BashOperator(
        task_id="load_to_oscar",
        bash_command=(
            f"php {OSCAR_HOME_PATH}/bin/oscar.php activity:import-json "
            "-f {{ ti.xcom_pull(task_ids='load') }}"
        ),
    )
    # pylint: disable=pointless-statement
    (transformed_data >> loaded_data >> import_activity_oscar)
