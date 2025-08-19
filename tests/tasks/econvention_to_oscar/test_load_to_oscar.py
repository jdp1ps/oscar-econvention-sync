import json
import pytest
from airflow.utils.state import TaskInstanceState
from tests.conftest import OSCAR_EXPECTED_DATA
from tests.utils.dag import (
    create_dag_run,
    create_task_instance,
)

LOAD_TASK_NAME = "dags.tasks.econvention_to_oscar.load.load"


@pytest.mark.parametrize(
    "dag_with_parameter",
    [
        {
            "task_name": LOAD_TASK_NAME,
            "param": json.dumps(OSCAR_EXPECTED_DATA),
        }
    ],
    indirect=True,
)
def test_load_json_file(dag_with_parameter, unique_logical_date):
    """
    Test the `load` function to verify if the file is created correctly
    and loading of JSON data from this file to import in OSCAR via BashOperator.
    Note:
    This test uses static sample data located in `/tests/data/` to ensure repeatability.
    """

    dag_run = create_dag_run(
        dag=dag_with_parameter,
        logical_date=unique_logical_date,
    )
    ti = create_task_instance(dag_with_parameter, dag_run, "load")
    assert ti.state == TaskInstanceState.SUCCESS
