import json
import datetime
import time
from airflow.utils.state import TaskInstanceState
from tests.utils.dag import (
    assert_dag_dict_equal,
    DATA_INTERVAL_START,
    DATA_INTERVAL_END,
    create_dag_run,
    create_task_instance,
)
from dags.tasks.transform import transform_econvention_to_oscar


def test_dag_loaded(dagbag):
    """
    Test dag loading
    """
    dag = dagbag.get_dag(dag_id="econvention_to_oscar")
    assert dagbag.import_errors == {}
    assert dag is not None
    assert len(dag.tasks) == 4


def test_dag_structure(dagbag):
    """
    Test that the DAG has the correct structure
    """
    dag = dagbag.get_dag(dag_id="econvention_to_oscar")
    expected_structure = {
        "extract_from_econvention": ["transform_from_econvention_to_oscar"],
        "transform_from_econvention_to_oscar": ["load"],
        "load": ["load_to_oscar"],
        "load_to_oscar": [],  # END
    }
    assert_dag_dict_equal(expected_structure, dag)


def test_extract_from_econvention(dagbag, econvention_raw_data, unique_logical_date):
    """
    Test the `extract_from_econvention` function to verify correct parsing
    and loading of JSON data used in the Airflow DAG pipeline.
    Note:
    This test uses static sample data located in `/tests/data/` to ensure repeatability.
    """

    dag = dagbag.get_dag(dag_id="econvention_to_oscar")
    dag_run = create_dag_run(
        dag=dag,
        data_interval_start=DATA_INTERVAL_START,
        data_interval_end=DATA_INTERVAL_END,
        logical_date=unique_logical_date,
        conf_payload={"items": econvention_raw_data},
    )
    ti = create_task_instance(dag, dag_run, "extract_from_econvention")
    assert ti.state == TaskInstanceState.SUCCESS


def test_transform_econvention_to_oscar(econvention_raw_data, oscar_expected_data):
    """
    Test the `transform_econvention_to_oscar` function to ensure that it correctly
    converts raw eConvention data into the format expected by the OSCAR system.

    This test validates:
    - Field mappings between eConvention and OSCAR.
    - Proper handling of nested and special keys (e.g., keys requiring transformation).
    - Consistency of output types and structure.

    Note:
    Fields that depend on the current date (e.g., "acronym", "projectlabel") must be
    explicitly set in the expected data, as the source file is static and does not
    auto-update with the current date.
    """
    date_iso = str(datetime.date.fromtimestamp(time.time()).isoformat())

    # update dynamically any attributes that require ISO date
    for item in oscar_expected_data:
        if "acronym" in item:
            item["acronym"] = date_iso
        if "projectlabel" in item:
            item["projectlabel"] = date_iso
    assert json.dumps(
        transform_econvention_to_oscar(econvention_raw_data), sort_keys=True, indent=4
    ) == json.dumps(oscar_expected_data, sort_keys=True, indent=4)
