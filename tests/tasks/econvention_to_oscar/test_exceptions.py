import json
from pathlib import Path
import pytest
from airflow.utils.state import TaskInstanceState
from dags.models.convention_model import TITRE_ALIAS
from tests.utils.dag import (
    create_dag_run,
    create_task_instance,
)

TRANSFORM_TASK_ID = "transform_econvention_to_oscar"
TRANSFORM_TASK_NAME = (
    "dags.tasks.econvention_to_oscar." + TRANSFORM_TASK_ID + "." + TRANSFORM_TASK_ID
)
CREATE_JSON_TO_OSCAR_TASK_ID = "create_import_json_to_oscar"
CREATE_JSON_TO_OSCAR_TASK_NAME = (
    "dags.tasks.econvention_to_oscar.create_import_json_to_oscar."
    + CREATE_JSON_TO_OSCAR_TASK_ID
)
IMPOSTOR_VALUE = 18052018


def test_exceptions_receive(
    econvention_to_oscar_dag,
    unique_logical_date,
    convention_raw_data,
):
    """
    Test the task 'receive_from_econvention'
    to handle exceptions with invalid data.
    Note:
    This test uses static sample data located in `/tests/data/` to ensure repeatability
    and modify the extracted JSON data used in the Airflow DAG pipeline.
    """
    invalid_data = convention_raw_data
    invalid_data[0][TITRE_ALIAS] = IMPOSTOR_VALUE
    dag_run = create_dag_run(
        dag=econvention_to_oscar_dag,
        logical_date=unique_logical_date,
        conf_data={"items": invalid_data},
    )
    with pytest.raises(ValueError):
        create_task_instance(
            econvention_to_oscar_dag, dag_run, "receive_from_econvention"
        )


@pytest.mark.parametrize(
    "dag_with_parameter",
    [
        {
            "task_name": TRANSFORM_TASK_NAME,
            "param": [
                {
                    "uid": "test_exception",
                    "acronym": "SUS",
                    "projectlabel": "Projet suspect",
                    "label": "Projet suspect",
                    "financialImpact": str(IMPOSTOR_VALUE),
                    "type": "",
                    "currency": str(IMPOSTOR_VALUE),
                    "organizations": {
                        "Structure Porteur": ["structure suspect"],
                        "Gendarmerie": ["Service suspicieux"],
                    },
                    "persons": {
                        "Porteur": ["Porteur suspect"],
                    },
                    "description": "",
                    "milestones": [],
                    "status": IMPOSTOR_VALUE,
                    "tva": None,
                    "payments": [],
                }
            ],
        }
    ],
    indirect=True,
)
def test_transform_econvention_to_oscar(dag_with_parameter, unique_logical_date):
    """
    Test the task 'transform_econvention_to_oscar'
    to handle exceptions with invalid data.
    """

    dag_run = create_dag_run(
        dag=dag_with_parameter,
        logical_date=unique_logical_date,
    )
    with pytest.raises(ValueError):
        create_task_instance(dag_with_parameter, dag_run, TRANSFORM_TASK_ID)
