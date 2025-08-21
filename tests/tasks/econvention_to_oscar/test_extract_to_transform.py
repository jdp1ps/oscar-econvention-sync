import json
from datetime import datetime
from airflow.utils.state import TaskInstanceState
from tests.conftest import CONVENTION_RAW_DATA, ACTIVITY_EXPECTED_DATA
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
    date_iso = str(datetime.now().date().isoformat())

    # update dynamically any attributes that require ISO date
    for item in ACTIVITY_EXPECTED_DATA:
        if "acronym" in item:
            item["acronym"] = date_iso
        if "projectlabel" in item:
            item["projectlabel"] = date_iso

    dag_run = create_dag_run(
        dag=econvention_to_oscar_dag,
        data_interval_start=DATA_INTERVAL_START,
        data_interval_end=DATA_INTERVAL_END,
        logical_date=unique_logical_date,
        conf_data={"items": CONVENTION_RAW_DATA},
    )
    ti = create_task_instance(
        econvention_to_oscar_dag, dag_run, "extract_from_econvention"
    )
    assert ti.state == TaskInstanceState.SUCCESS

    # run transform
    ti_transform = create_task_instance(
        econvention_to_oscar_dag, dag_run, "transform_from_econvention_to_oscar"
    )
    assert ti_transform.state == TaskInstanceState.SUCCESS

    assert json.dumps(
        ti_transform.xcom_pull(task_ids="transform_from_econvention_to_oscar"),
        sort_keys=True,
    ) == json.dumps(ACTIVITY_EXPECTED_DATA, sort_keys=True)
