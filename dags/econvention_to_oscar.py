from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from tasks.econvention_to_oscar.receive_from_econvention import receive_from_econvention
from tasks.econvention_to_oscar.transform_from_econvention_to_oscar import (
    transform_from_econvention_to_oscar,
)
from tasks.econvention_to_oscar.create_import_json_to_oscar import (
    create_import_json_to_oscar,
)
from utils.config import OSCAR_HOME_PATH


# pylint: disable=unexpected-keyword-arg
with DAG(
    dag_id="econvention_to_oscar",
    start_date=datetime(2025, 7, 30),
    schedule=None,
    catchup=False,
    tags=["api", "json", "etl", "post"],
) as econvention_to_oscar:

    raw_data = receive_from_econvention()
    transformed_data = transform_from_econvention_to_oscar(raw_data)
    loaded_data = create_import_json_to_oscar(transformed_data)

    import_activity_oscar = BashOperator(
        dag=econvention_to_oscar,
        task_id="load_to_oscar",
        bash_command=(
            f"php {OSCAR_HOME_PATH}/bin/oscar.php activity:import-json "
            "-f {{ ti.xcom_pull(task_ids='create_import_json_to_oscar') }}"
        ),
    )
    # pylint: disable=pointless-statement
    (transformed_data >> loaded_data >> import_activity_oscar)
