import json
from models.abstract_models import ConventionFactory
from models.oscar_convention import OscarConvention
from models.econvention import Econvention


class OscarFactory(ConventionFactory):
    """
    Oscar factory for building or converting convention models.
    """

    @classmethod
    def from_api_payload(cls, raw_data: list[dict]) -> list[OscarConvention]:
        """Create a convention instance from a raw API payload."""

    @classmethod
    def convert_from(cls, clean_data: list[dict]) -> str:
        """Convert data from another convention model."""
        econvention_list: list[Econvention] = [
            Econvention(**dict(econvention.items())) for econvention in clean_data
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
