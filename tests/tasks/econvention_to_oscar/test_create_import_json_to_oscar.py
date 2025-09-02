import json
from pathlib import Path
import pytest
from airflow.utils.state import TaskInstanceState
from tests.utils.dag import (
    create_dag_run,
    create_task_instance,
)

CREATE_JSON_TO_OSCAR_TASK_ID = "create_import_json_to_oscar"
CREATE_JSON_TO_OSCAR_TASK_NAME = (
    "dags.tasks.econvention_to_oscar.create_import_json_to_oscar."
    + CREATE_JSON_TO_OSCAR_TASK_ID
)


@pytest.mark.parametrize(
    "dag_with_parameter",
    [
        {
            "task_name": CREATE_JSON_TO_OSCAR_TASK_NAME,
            "param": json.dumps(
                [
                    {
                        "uid": "test_create_import_json",
                        "acronym": "sth",
                        "projectlabel": "something",
                        "label": "test1",
                        "financialImpact": "Aucune",
                        "type": "",
                        "currency": "Euro",
                        "organizations": {
                            "Structure Porteur": ["Structure1"],
                            "Partenaire": ["Partenaire 1"],
                        },
                        "persons": {
                            "Porteur": ["econvention"],
                            "Créateur": ["econvention"],
                        },
                        "description": """
                            Ce fichier a été généré via un test de load, 
                            si vous apercevez ce fichier alors qu'il n'est pas au bon en endroit, 
                            contactez l'équipe SINR de la DIREVAL
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
def test_import_json_file(dag_with_parameter, unique_logical_date):
    """
    Test the `import_json` function verifies if the file is created correctly
    in ECONVENTION_TO_OSCAR_OUTPUT_DIR.
    This created file can be imported later on in Oscar.

    At the end of the run, the created file will be deleted.
    """

    dag_run = create_dag_run(
        dag=dag_with_parameter,
        logical_date=unique_logical_date,
    )
    ti = create_task_instance(dag_with_parameter, dag_run, CREATE_JSON_TO_OSCAR_TASK_ID)
    assert ti.state == TaskInstanceState.SUCCESS

    file_path = Path(ti.xcom_pull(task_ids=CREATE_JSON_TO_OSCAR_TASK_ID))
    assert file_path.exists()

    # Cleanup to avoid polluting ECONVENTION_TO_OSCAR_OUTPUT_DIR
    file_path.unlink()
