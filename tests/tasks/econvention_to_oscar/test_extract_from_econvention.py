from airflow.utils.state import TaskInstanceState
from tests.conftest import ECONVENTION_RAW_DATA
from tests.utils.dag import (
    DATA_INTERVAL_START,
    DATA_INTERVAL_END,
    create_dag_run,
    create_task_instance,
)


def test_extract_from_econvention(econvention_to_oscar_dag, unique_logical_date):
    """
    Test the `extract_from_econvention` function to verify correct parsing
    and loading of JSON data used in the Airflow DAG pipeline.
    Note:
    This test uses static sample data located in `/tests/data/` to ensure repeatability.
    """

    dag_run = create_dag_run(
        dag=econvention_to_oscar_dag,
        data_interval_start=DATA_INTERVAL_START,
        data_interval_end=DATA_INTERVAL_END,
        logical_date=unique_logical_date,
        conf_data={"items": ECONVENTION_RAW_DATA},
    )
    ti = create_task_instance(
        econvention_to_oscar_dag, dag_run, "extract_from_econvention"
    )
    assert ti.state == TaskInstanceState.SUCCESS
