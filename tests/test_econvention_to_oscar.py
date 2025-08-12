import datetime
import json
import time
import pytest
from airflow.utils.state import TaskInstanceState
from models.econvention_factory import EconventionFactory
from tests.utils.dag import (
    assert_dag_dict_equal,
    DATA_INTERVAL_START,
    DATA_INTERVAL_END,
    create_dag_run,
    create_task_instance,
)

TRANSFORM_TASK_NAME = "dags.tasks.transform" + ".transform_from_econvention_to_oscar"


def test_dag_loaded(econvention_to_oscar_dag):
    """
    Test dag loading
    """
    assert econvention_to_oscar_dag is not None
    assert len(econvention_to_oscar_dag.tasks) == 4


def test_dag_structure(econvention_to_oscar_dag):
    """
    Test that the DAG has the correct structure
    """
    expected_structure = {
        "extract_from_econvention": ["transform_from_econvention_to_oscar"],
        "transform_from_econvention_to_oscar": ["load"],
        "load": ["load_to_oscar"],
        "load_to_oscar": [],  # END
    }
    assert_dag_dict_equal(expected_structure, econvention_to_oscar_dag)


def test_extract_from_econvention(
    econvention_to_oscar_dag, econvention_raw_data, unique_logical_date
):
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
        conf_data={"items": econvention_raw_data},
    )
    ti = create_task_instance(
        econvention_to_oscar_dag, dag_run, "extract_from_econvention"
    )
    assert ti.state == TaskInstanceState.SUCCESS


@pytest.mark.parametrize(
    "dag_with_parameter",
    [
        {
            "task_name": TRANSFORM_TASK_NAME,
            "param": EconventionFactory.from_api_payload(
                [
                    {
                        "Titre": "test1",
                        "Reference": "test1",
                        "Porteur": "econvention",
                        "Sticture Porteur": "Structure1",
                        "Partenaire": [{"DisplayName": "Partenaire 1"}],
                        "Créateur": {"DisplayName": "econvention"},
                    },
                    {
                        "Titre": "test2",
                        "Reference": "test2",
                        "Porteur": "Amel Dabiba-Mahdbi",
                        "Sticture Porteur": "Structure1",
                        "Partenaire": [
                            {"DisplayName": "Partenaire 1"},
                            {"DisplayName": "Partenaire 2"},
                        ],
                        "Créateur": {"DisplayName": "econvention"},
                    },
                ]
            ),
        }
    ],
    indirect=True,
)
def test_transform_econvention_to_oscar(
    dag_with_parameter, oscar_expected_data, unique_logical_date
):
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
    dag_run = create_dag_run(
        dag=dag_with_parameter,
        data_interval_start=DATA_INTERVAL_START,
        data_interval_end=DATA_INTERVAL_END,
        logical_date=unique_logical_date,
    )
    ti = create_task_instance(
        dag_with_parameter, dag_run, "transform_from_econvention_to_oscar"
    )
    assert ti.state == TaskInstanceState.SUCCESS
    assert json.dumps(
        ti.xcom_pull(task_ids="transform_from_econvention_to_oscar"), sort_keys=True
    ) == json.dumps(oscar_expected_data, sort_keys=True)
