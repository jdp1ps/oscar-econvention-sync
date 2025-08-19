from pydantic import BaseModel, Field, ConfigDict


class Econvention(BaseModel):
    """
    Econvention model which represents an ECONVENTION.
    """

    model_config = ConfigDict(
        validate_by_name=True, validate_by_alias=True, frozen=True
    )

    Reference: str
    Titre: str
    Porteur: str
    Createur: str = Field(alias="Créateur")
    Partenaire: list[str] = []
    Structure_Porteur: str
    Description: str = ""
    Origine_de_la_convention: str = ""
    SousType: str = ""
    DateDemarrage: str = ""
    TermeConvention: str = ""
    Etape: list[str] = []
