from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.decorators import task
from tasks.transform import transform_from_econvention_to_oscar
from tasks.load import load
from utils.config import OSCAR_HOME_PATH


@task
def extract_from_econvention(**context) -> list[dict]:
    """
    Extract data from REST API POST sent by eConvention

    :param context: given automatically by Airflow

    :return:
        list of dictionaries
    """
    conf_json = context["dag_run"].conf
    items = conf_json.get("items")
    if items is None:
        raise ValueError("Missing 'items' key in dag_run.conf.")
    if not isinstance(items, list):
        raise ValueError("Expected 'items' to be a list of dictionaries.")
    if not all(isinstance(item, dict) for item in items):
        raise ValueError("All items in 'items' must be dictionaries.")

    return items


# pylint: disable=unexpected-keyword-arg
with DAG(
    dag_id="dag_etl",
    start_date=datetime(2025, 7, 30),
    schedule=None,
    catchup=False,
    tags=["api", "json", "etl", "post"],
) as dag_etl:

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
