import json
import pytest
from airflow.utils.state import TaskInstanceState
from tests.utils.dag import (
    create_dag_run,
    create_task_instance,
)

TRANSFORM_TASK_ID = "transform_oscar_to_econvention"
TRANSFORM_TASK_NAME = (
    "dags.tasks.oscar_to_econvention.transform_oscar_to_econvention."
    + TRANSFORM_TASK_ID
)


@pytest.mark.parametrize(
    "dag_with_parameter",
    [
        {
            "task_name": TRANSFORM_TASK_NAME,
            "param": [
                {
                    "acronym": "~Association PIVOD Jarosz",
                    "amount": 100.1,
                    "currency": "Euro",
                    "datePFI": None,
                    "dateend": "2027-01-09",
                    "datesigned": None,
                    "datestart": "2024-01-09",
                    "description": "Description abrégée.",
                    "financialImpact": "Aucune",
                    "label": "Convention MIAGE - Association PIVOD",
                    "milestones": [
                        {
                            "date": None,
                            "description": "",
                            "type": "100 - Dossier Complet",
                        }
                    ],
                    "organizations": {
                        "Partenaire": ["Association PIVOD"],
                        "StructurePorteur": ["UFR 27 : Mathématiques et informatique"],
                    },
                    "payments": [],
                    "persons": {
                        "Porteur": ["Carine Souveyet Jarosz"],
                        "ReferentDAJI": ["David Dubois-Penicaud"],
                        "ResponsablePorteur": ["Personnels:Roles:DIR UFR UFR 27"],
                    },
                    "pfi": "",
                    "projectlabel": "Convention MIAGE - Association PIVOD",
                    "status": 404,
                    "tva": None,
                    "type": "ANR",
                    "uid": "eC2024-1",
                }
            ],
        }
    ],
    indirect=True,
)
def test_transform_oscar_to_econvention(dag_with_parameter, unique_logical_date):
    """
    Test the task 'transform_oscar_to_econvention'
    to ensure that the data conversion works properly.
    """
    convention_expected_data = [
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
            "MontantConvention": "100.10",
            "Etape": "0 - Brouillon",
        }
    ]
    dag_run = create_dag_run(
        dag=dag_with_parameter,
        logical_date=unique_logical_date,
    )
    ti_transform = create_task_instance(dag_with_parameter, dag_run, TRANSFORM_TASK_ID)
    assert ti_transform.state == TaskInstanceState.SUCCESS

    assert json.dumps(
        ti_transform.xcom_pull(task_ids=TRANSFORM_TASK_ID),
        sort_keys=True,
    ) == json.dumps(convention_expected_data, sort_keys=True)
