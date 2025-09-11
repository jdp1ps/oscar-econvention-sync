import json
from pathlib import Path
import pendulum
import pytest
from airflow.utils.state import TaskInstanceState
from tests.utils.dag import (
    create_dag_run,
    create_task_instance,
)

UPDATE_JSON_TO_ECONVENTION_TASK_ID = "update_json_for_econvention"
UPDATE_JSON_TO_ECONVENTION_TASK_NAME = (
    "dags.tasks.oscar_to_econvention."
    + UPDATE_JSON_TO_ECONVENTION_TASK_ID
    + "."
    + UPDATE_JSON_TO_ECONVENTION_TASK_ID
)


@pytest.mark.parametrize(
    "dag_with_parameter",
    [
        {
            "task_name": UPDATE_JSON_TO_ECONVENTION_TASK_NAME,
            "param": json.dumps([{"Activité": "1"}]),
        }
    ],
    indirect=True,
)
def test_import_json_file(dag_with_parameter):
    """
    Test the `import_json` function verifies if the file is created correctly
    in OSCAR_TO_ECONVENTION_OUTPUT_DIR.
    This created file can be imported later on in eConvention.

    At the end of the run, the created file will be deleted.
    """

    dag_run = create_dag_run(
        dag=dag_with_parameter,
        logical_date=pendulum.datetime(2025, 7, 31, 1, 59, 59, 999999),
    )
    ti1 = create_task_instance(
        dag_with_parameter, dag_run, UPDATE_JSON_TO_ECONVENTION_TASK_ID
    )
    assert ti1.state == TaskInstanceState.SUCCESS

    initial_file_path = Path(ti1.xcom_pull(task_ids=UPDATE_JSON_TO_ECONVENTION_TASK_ID))
    assert initial_file_path.exists()

    ti2 = create_task_instance(
        dag_with_parameter, dag_run, UPDATE_JSON_TO_ECONVENTION_TASK_ID
    )
    assert ti2.state == TaskInstanceState.SUCCESS

    new_file_path = Path(ti2.xcom_pull(task_ids=UPDATE_JSON_TO_ECONVENTION_TASK_ID))

    assert new_file_path.exists()
    assert new_file_path == initial_file_path

    with open(new_file_path, "r",encoding="utf-8") as file:
        data = json.load(file)

    # Cleanup to avoid polluting ECONVENTION_TO_OSCAR_OUTPUT_DIR
    new_file_path.unlink()

    assert data == [{"Activité": "1"}, {"Activité": "1"}]
