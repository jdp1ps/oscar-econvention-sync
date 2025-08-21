import json
from airflow.decorators import task
from models.activity_model import Activity
from models.convention_model import Convention


@task
def transform_from_econvention_to_oscar(conventions: list[dict]) -> str:
    """Transform from ECONVENTION to OSCAR by mapping their attribute."""

    econvention_list: list[Convention] = [
        Convention(**econvention) for econvention in conventions
    ]
    activity_list: list[Activity] = []
    for econvention in econvention_list:
        mapping = {
            "uid": econvention.Reference,
            "label": econvention.Titre,
            "persons": {
                "Porteur": econvention.Porteur,
                "Créateur": econvention.Createur,
            },
            "organizations": {
                "Structure Porteur": econvention.Structure_Porteur,
                "Partenaire": econvention.Partenaire,
            },
            "description": econvention.Description or "",
            "type": econvention.Type_de_la_convention or "",
            "datestart": (econvention.DateDemarrage),
            "dateend": (econvention.TermeConvention),
            "milestones": econvention.Etape or [],
        }
        activity_list.append(Activity(**mapping))
    results = json.dumps(
        [oscar_conv.model_dump(by_alias=True) for oscar_conv in activity_list],
        sort_keys=True,
        indent=4,
    )

    return results
