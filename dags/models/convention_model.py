from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
from utils.iso_date import DATE_PATTERN, to_iso_date, ensure_start_before_end
from models.activity_model import Milestone


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

    reference: str = Field(alias="Reference")
    titre: str = Field(alias="Titre")
    porteur: str = Field(alias="Porteur")
    createur: str = Field(alias="Créateur")
    partenaire: list[str] = Field(default=[], alias="Partenaire")
    structure_porteur: str = Field(
        validation_alias="Sticture Porteur", serialization_alias="Structure Porteur"
    )
    description: str = Field(default="", alias="Description")
    origine_de_la_convention: OrigineEnum | None = Field(
        default=None, alias="Origine de la convention"
    )
    type_de_la_convention: TypeEnum | None = Field(
        default=None, alias="Type de la convention"
    )
    date_demarrage: str | None = Field(
        default=None, alias="DateDemarrage", pattern=DATE_PATTERN
    )
    terme_convention: str | None = Field(
        default=None, alias="TermeConvention", pattern=DATE_PATTERN
    )
    etape: list[dict] = Field(default=[], alias="Etape")

    @model_validator(mode="after")
    @classmethod
    def check_dates_order(cls, convention):
        """Ensure DateDemarrage is before TermeConvention."""
        ensure_start_before_end(
            convention.date_demarrage,
            convention.terme_convention,
            start_name="DateDemarrage",
            end_name="TermeConvention",
        )
        return convention

    @field_validator("origine_de_la_convention", mode="before")
    @classmethod
    def normalize_origine(cls, origin: dict | str) -> str:
        """
        Ensure Origine de la convention is always str
        """
        if isinstance(origin, dict):
            return origin.get("Value")
        return origin

    @field_validator("createur", mode="before")
    @classmethod
    def normalize_createur(cls, creator: dict | str) -> str:
        """
        Ensure Créateur is always a str.
        """
        if isinstance(creator, dict):
            return creator.get("DisplayName")
        return creator

    @field_validator("partenaire", mode="before")
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

    @field_validator("date_demarrage", "terme_convention", mode="before")
    @classmethod
    def check_date_format(cls, raw_date):
        """
        wrapper to call to_iso_date used by models
        """
        return to_iso_date(raw_date)

    def to_uid(self):
        """Convert reference to activity's uid"""
        return self.reference

    def to_label(self):
        """Convert titre to activity's label"""
        return self.titre

    def to_persons(self):
        """Convert porteur & createur to activity's persons"""
        return {"Porteur": self.porteur, "Créateur": self.createur}

    def to_organizations(self):
        """Convert structure_porteur & partenaire to activity's organizations"""
        return {
            "Structure Porteur": self.structure_porteur,
            "Partenaire": self.partenaire,
        }

    def to_activity_type(self):
        """
        Converts type to activity's type.
        [TEMPORARY IMPLEMENTATION] This method currently returns an empty string as a placeholder.
        """
        return ""

    def to_datestart(self):
        """Convert DateDemarrage to activity's datestart"""
        return self.date_demarrage

    def to_dateend(self):
        """Convert TermeConvention to activity's dateend"""
        return self.terme_convention

    def to_milestones(self):
        """Convert Etape to activity's milestones"""
        return [
            Milestone(type=item["Title"]) for item in self.etape if item.get("Active")
        ]
