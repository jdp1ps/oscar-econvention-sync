import json
from airflow.decorators import task
from models.oscar_convention import OscarConvention
from models.econvention import Econvention


@task
def transform_from_econvention_to_oscar(econventions: list[dict]) -> str:
    """Transform from ECONVENTION to OSCAR by mapping their attribute."""

    econvention_list: list[Econvention] = [
        Econvention(**econvention) for econvention in econventions
    ]
    oscar_list: list[OscarConvention] = []
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
            "type": econvention.SousType or "",
            "datestart": (
                econvention.DateDemarrage.isoformat()
                if econvention.DateDemarrage
                else ""
            ),
            "dateend": (
                econvention.TermeConvention.isoformat()
                if econvention.TermeConvention
                else ""
            ),
            "milestones": econvention.Etape or [],
        }
        oscar_list.append(OscarConvention(**mapping))
    results = json.dumps(
        [oscar_conv.model_dump(by_alias=True) for oscar_conv in oscar_list],
        sort_keys=True,
        indent=4,
    )

    return results
