import json
from airflow.utils.state import TaskInstanceState
from tests.utils.dag import (
    create_dag_run,
    create_task_instance,
)


def test_receive_to_transform(
    econvention_to_oscar_dag,
    unique_logical_date,
    convention_raw_data,
    activity_expected_data,
):
    """
    Test the both tasks 'receive_from_econvention' and
    'transform_econvention_to_oscar' verify correct parsing
    and loading of JSON data used in the Airflow DAG pipeline.
    Note:
    This test uses static sample data located in `/tests/data/` to ensure repeatability.
    """

    dag_run = create_dag_run(
        dag=econvention_to_oscar_dag,
        logical_date=unique_logical_date,
        conf_data={"items": convention_raw_data},
    )
    ti = create_task_instance(
        econvention_to_oscar_dag, dag_run, "receive_from_econvention"
    )
    assert ti.state == TaskInstanceState.SUCCESS

    # run transform
    ti_transform = create_task_instance(
        econvention_to_oscar_dag, dag_run, "transform_econvention_to_oscar"
    )
    assert ti_transform.state == TaskInstanceState.SUCCESS

    assert json.dumps(
        ti_transform.xcom_pull(task_ids="transform_econvention_to_oscar"),
        sort_keys=True,
    ) == json.dumps(activity_expected_data, sort_keys=True)
