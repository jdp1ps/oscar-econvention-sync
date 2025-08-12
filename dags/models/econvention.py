from typing import Optional
from pydantic import Field, ConfigDict
from models.abstract_models import SyncConvention


class Econvention(SyncConvention):
    """
    Econvention model which represents an ECONVENTION.
    """

    model_config = ConfigDict(populate_by_name=True)  # permet d'utiliser le nom Python

    Reference: str
    Titre: str
    Porteur: str
    Createur: str = Field(alias="Créateur")
    Partenaire: Optional[list[str]] = None
    Structure_Porteur: str
    Description: Optional[str] = ""
    Origine_de_la_convention: Optional[str] = None
    SousType: Optional[str] = None
    DateDemarrage: Optional[str] = ""
    TermeConvention: Optional[str] = ""
    Etape: Optional[list[str]] = []
