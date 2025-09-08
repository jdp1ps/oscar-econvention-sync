import json
from pathlib import Path
import pytest
from airflow.utils.state import TaskInstanceState
from tests.utils.dag import (
    create_dag_run,
    create_task_instance,
)

CREATE_JSON_TO_ECONVENTION_TASK_ID = "create_import_json_to_econvention"
CREATE_JSON_TO_ECONVENTION_TASK_NAME = (
    "dags.tasks.oscar_to_econvention.create_import_json_to_econvention."
    + CREATE_JSON_TO_ECONVENTION_TASK_ID
)


@pytest.mark.parametrize(
    "dag_with_parameter",
    [
        {
            "task_name": CREATE_JSON_TO_ECONVENTION_TASK_NAME,
            "param": json.dumps(
                [
                    {
                        "Reference": "eC2024-1",
                        "Title": "Convention MIAGE - Association PIVOD",
                        "Porteur": "Carine Souveyet Jarosz",
                        "StructurePorteur": "UFR 27 : Mathématiques et informatique",
                        "ResponsablePorteur": "Personnels:Roles:DIR UFR UFR 27",
                        "ReferentDAJI": "David Dubois-Penicaud",
                        "Partenaire": "Association PIVOD",
                        "OrigineConvention": "Partenaire",
                        "DescriptionConvention": "Description abrégée.",
                        "TypeConvention": "Recherche",
                        "SousType": "ANR",
                        "DateDemarrage": "01/09/2024 00:00",
                        "TermeConvention": "01/09/2027 00:00",
                        "MontantConvention": "",
                        "Recettes": "100.10",
                        "Depenses": "",
                        "Etape": "0 - Brouillon",
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
    in OSCAR_TO_ECONVENTION_OUTPUT_DIR.
    This created file can be imported later on in eConvention.

    At the end of the run, the created file will be deleted.
    """

    dag_run = create_dag_run(
        dag=dag_with_parameter,
        logical_date=unique_logical_date,
    )
    ti = create_task_instance(
        dag_with_parameter, dag_run, CREATE_JSON_TO_ECONVENTION_TASK_ID
    )
    assert ti.state == TaskInstanceState.SUCCESS

    file_path = Path(ti.xcom_pull(task_ids=CREATE_JSON_TO_ECONVENTION_TASK_ID))
    assert file_path.exists()

    # Cleanup to avoid polluting ECONVENTION_TO_OSCAR_OUTPUT_DIR
    file_path.unlink()
