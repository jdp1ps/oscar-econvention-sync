from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator


class OrigineEnum(str, Enum):
    """
    The convention is originated from intern or partner
    """

    INTERNE = "Interne"
    PARTENAIRE = "Partenaire"


class TypeEnum(str, Enum):
    """
    The convention is originated from intern or partner
    """

    PEDAGOGIE = "Pédagogie"
    RECHERCHE = "Recherche"


class Convention(BaseModel):
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
    Structure_Porteur: str = Field(
        validation_alias="Sticture Porteur", serialization_alias="Structure Porteur"
    )
    Description: str = ""
    Origine_de_la_convention: OrigineEnum | None = Field(
        default=None, alias="Origine de la convention"
    )
    Type_de_la_convention: TypeEnum | None = Field(
        default=None, alias="Type de la convention"
    )
    DateDemarrage: str | None = Field(default=None, pattern=r"\d{4}-\d{2}-\d{2}")
    TermeConvention: str | None = Field(default=None, pattern=r"\d{4}-\d{2}-\d{2}")
    Etape: list[str] = []

    @field_validator("Origine_de_la_convention", mode="before")
    @classmethod
    def normalize_origine(cls, origin: dict | str) -> str:
        """
        Ensure Origine de la convention is always str
        """
        if isinstance(origin, dict):
            return origin.get("Value")
        return origin

    @field_validator("Createur", mode="before")
    @classmethod
    def normalize_createur(cls, creator: dict | str) -> str:
        """
        Ensure Créateur is always a str.
        """
        if isinstance(creator, dict):
            return creator.get("DisplayName")
        return creator

    @field_validator("Partenaire", mode="before")
    @classmethod
    def normalize_partenaire(cls, partners: list[dict]) -> list[str]:
        """
        Ensure Partenaire is always a list[str] of DisplayNames.
        """
        if isinstance(partners, list):
            return [
                item.get("DisplayName") if isinstance(item, dict) else str(item)
                for item in partners
            ]
        return partners or []
