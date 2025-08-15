from datetime import datetime
import json
import pytest
from airflow.utils.state import TaskInstanceState
from models.econvention_factory import EconventionFactory
from tests.utils.dag import (
    DATA_INTERVAL_START,
    DATA_INTERVAL_END,
    create_dag_run,
    create_task_instance,
)

TRANSFORM_TASK_NAME = "dags.tasks.transform.transform_from_econvention_to_oscar"


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
    date_iso = str(datetime.now().date().isoformat())

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
