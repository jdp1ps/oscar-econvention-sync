import json
from pathlib import Path
import pytest
from airflow.utils.state import TaskInstanceState
from dags.utils.config import FALLBACK_OUTPUT_DIR
from tests.utils.dag import (
    create_dag_run,
    create_task_instance,
)


TRANSFORM_TASK_NAME = (
    "dags.tasks.econvention_to_oscar.transform_econvention_to_oscar"
    ".transform_econvention_to_oscar"
)
CREATE_JSON_TO_OSCAR_TASK_NAME = (
    "dags.tasks.econvention_to_oscar.create_import_json_to_oscar"
    ".create_import_json_to_oscar"
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
    invalid_data[0]["Titre"] = IMPOSTOR_VALUE
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
        create_task_instance(
            dag_with_parameter, dag_run, "transform_econvention_to_oscar"
        )


@pytest.mark.parametrize(
    "dag_with_parameter",
    [
        {
            "task_name": CREATE_JSON_TO_OSCAR_TASK_NAME,
            "param": json.dumps(
                [
                    {
                        "uid": "test_exception",
                        "acronym": "exc",
                        "projectlabel": "projet exceptionnel",
                        "label": "label exceptionnel",
                        "financialImpact": "Aucune",
                        "type": "",
                        "currency": "Euro",
                        "organizations": {
                            "Structure Porteur": ["Structure d'exception !"],
                        },
                        "persons": {
                            "Porteur": ["Porteur exceptionnel"],
                        },
                        "description": """
                            Ce fichier a été exceptionnel écrit pour montrer
                            à quel point ce fichier est exceptionnel en supportant
                            l'exception PermissionError ou FileNotFound.
                        """,
                        "milestones": [],
                        "status": 404,
                        "tva": None,
                        "payments": [],
                    }
                ]
            ),
        }
    ],
    indirect=True,
)
def test_import_json_file_with_fallback(
    dag_with_parameter, unique_logical_date, monkeypatch
):
    """
    Test the `import_json` function verifies if the file is created correctly
    in FALLBACK_OUTPUT_DIR when ECONVENTION_TO_OSCAR_OUTPUT_DIR is invalid temporary.
    """

    # Force an invalid/unwritable directory for the main output
    monkeypatch.setenv("ECONVENTION_TO_OSCAR_OUTPUT_DIR", "/root/invalid_dir")

    dag_run = create_dag_run(
        dag=dag_with_parameter,
        logical_date=unique_logical_date,
    )
    ti = create_task_instance(
        dag_with_parameter, dag_run, "create_import_json_to_oscar"
    )
    assert ti.state == TaskInstanceState.SUCCESS

    file_path = Path(ti.xcom_pull(task_ids="create_import_json_to_oscar"))
    assert file_path.exists()
    assert str(file_path).startswith(str(FALLBACK_OUTPUT_DIR))

    # Cleanup to avoid polluting ECONVENTION_TO_OSCAR_OUTPUT_DIR
    file_path.unlink()
