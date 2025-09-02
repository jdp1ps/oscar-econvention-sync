from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
    field_validator,
    NonNegativeFloat,
)
from utils.type_utils import (
    CONVENTION_TYPE_ENUM,
    CONVENTION_SOUS_TYPE_ENUM,
)
from utils.date_utils import (
    CONVENTION_DATE_PATTERN,
    to_activity_date_format,
    ensure_start_before_end,
    to_convention_date_format,
)
from utils.aliases import (
    REFERENCE_ALIAS,
    TITRE_ALIAS,
    PORTEUR_ALIAS,
    STRUCTURE_PORTEUR_ALIAS,
    RESPONSABLE_PORTEUR_ALIAS,
    REFERENT_DAJI_ALIAS,
    PARTENAIRE_ALIAS,
    DESCRIPTION_ALIAS,
    ORIGINE_CONVENTION_ALIAS,
    MONTANT_CONVENTION_ALIAS,
    TYPE_CONVENTION_ALIAS,
    SOUS_TYPE_CONVENTION_ALIAS,
    DATE_DEMARRAGE_ALIAS,
    TERME_CONVENTION_ALIAS,
    ETAPE_ALIAS,
)
from models.submodels import Milestone


class OrigineEnum(str, Enum):
    """
    The convention is originated from intern or partner
    """

    INTERNE = "Interne"
    PARTENAIRE = "Partenaire"


class Convention(BaseModel):
    """
    Econvention model which represents an ECONVENTION.
    """

    model_config = ConfigDict(
        validate_by_name=True, validate_by_alias=True, frozen=True
    )

    reference: str = Field(alias=REFERENCE_ALIAS)
    titre: str = Field(alias=TITRE_ALIAS)
    porteur: str = Field(alias=PORTEUR_ALIAS)
    structure_porteur: str = Field(alias=STRUCTURE_PORTEUR_ALIAS)
    responsable_porteur: str = Field(default="", alias=RESPONSABLE_PORTEUR_ALIAS)
    referent_daji: str = Field(default="", alias=REFERENT_DAJI_ALIAS)

    partenaire: str = Field(default="", alias=PARTENAIRE_ALIAS)

    description: str = Field(default="", alias=DESCRIPTION_ALIAS)
    origine_de_la_convention: OrigineEnum | None = Field(
        default=None, alias=ORIGINE_CONVENTION_ALIAS
    )
    montant_convention: NonNegativeFloat | str = Field(
        default="", alias=MONTANT_CONVENTION_ALIAS
    )
    type_convention: CONVENTION_TYPE_ENUM | None = Field(
        default=None, alias=TYPE_CONVENTION_ALIAS
    )
    sous_type: CONVENTION_SOUS_TYPE_ENUM | None = Field(
        default=None, alias=SOUS_TYPE_CONVENTION_ALIAS
    )
    date_demarrage: str | None = Field(
        default=None, alias=DATE_DEMARRAGE_ALIAS, pattern=CONVENTION_DATE_PATTERN
    )
    terme_convention: str | None = Field(
        default=None, alias=TERME_CONVENTION_ALIAS, pattern=CONVENTION_DATE_PATTERN
    )
    etape: str = Field(default="", alias=ETAPE_ALIAS)

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

    @field_validator("date_demarrage", "terme_convention", mode="before")
    @classmethod
    def check_date_format(cls, raw_date) -> str:
        """
        wrapper to call to_convention_date_format used by models
        """
        return to_convention_date_format(raw_date)

    def to_uid(self) -> str:
        """Convert reference to activity's uid"""
        return self.reference

    def to_acronym(self) -> str:
        """
        Use partenaire and porteur lastname
        to create activity's acronym automatically
        It is an unofficial acronym indicated with ~
        """
        # pylint: disable=E1101
        return "~" + self.partenaire + " " + self.porteur.split()[-1]

    def to_projectlabel(self) -> str:
        """Convert reference to activity's projectlabel"""
        return self.titre

    def to_label(self) -> str:
        """Convert titre to activity's label"""
        return self.titre

    def to_persons(self) -> dict:
        """Convert some persons to activity's persons"""

        temp_data = {
            PORTEUR_ALIAS: self.porteur,
            RESPONSABLE_PORTEUR_ALIAS: self.responsable_porteur,
            REFERENT_DAJI_ALIAS: self.referent_daji,
        }
        result = {key: value for key, value in temp_data.items() if value}
        return result

    def to_organizations(self):
        """Convert structure_porteur & partenaire to activity's organizations"""
        temp_data = {
            STRUCTURE_PORTEUR_ALIAS: self.structure_porteur,
            PARTENAIRE_ALIAS: self.partenaire,
        }
        result = {key: value for key, value in temp_data.items() if value}
        return result

    def to_activity_type(self):
        """
        Converts type to activity's type.
        """
        return self.sous_type

    def to_datestart(self) -> str:
        """Convert DateDemarrage to activity's datestart"""
        return to_activity_date_format(self.date_demarrage)

    def to_dateend(self) -> str:
        """Convert TermeConvention to activity's dateend"""
        return to_activity_date_format(self.terme_convention)

    def to_milestones(self) -> list[Milestone]:
        """Convert Etape to activity's milestones"""
        return [Milestone(type=self.etape)]
