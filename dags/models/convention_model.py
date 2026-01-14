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
    RECETTES_ALIAS,
    DEPENSES_ALIAS,
    convert_role_for_activity,
)
from models.submodels import Milestone
from models.enum_models import FinancialImpactEnum, OrigineEnum


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
    structure_porteur: str = Field(default="", alias=STRUCTURE_PORTEUR_ALIAS)
    responsable_porteur: str = Field(default="", alias=RESPONSABLE_PORTEUR_ALIAS)
    referent_daji: str = Field(default="", alias=REFERENT_DAJI_ALIAS)

    partenaire: str = Field(default="", alias=PARTENAIRE_ALIAS)

    description: str = Field(default="", alias=DESCRIPTION_ALIAS)
    origine_de_la_convention: OrigineEnum | None = Field(
        default=None, alias=ORIGINE_CONVENTION_ALIAS
    )
    montant_convention: str = Field(default="", alias=MONTANT_CONVENTION_ALIAS)
    recettes_convention: str = Field(default="", alias=RECETTES_ALIAS)
    depenses_convention: str = Field(default="", alias=DEPENSES_ALIAS)
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
    def check_date_format(cls, raw_date: str) -> str:
        """
        wrapper to call to_convention_date_format used by models
        """
        return to_convention_date_format(raw_date)

    @field_validator(
        "montant_convention", "recettes_convention", "depenses_convention", mode="after"
    )
    @classmethod
    def normalize_montant_convention(cls, raw_montant: str) -> str:
        """
        Normalize montant_convention by removing spaces and
        replacing commas with dots to ease NonNegativeFloat parsing.
        """
        try:
            if len(raw_montant) == 0:
                return raw_montant
            cleaned_montant = raw_montant.replace(" ", "").replace(",", ".")
            NonNegativeFloat(cleaned_montant)  # Try to convert if the conversion works
            return cleaned_montant
        except ValueError as e:
            raise ValueError(f"Invalid montant format: {raw_montant}") from e

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
            convert_role_for_activity(PORTEUR_ALIAS): self.porteur,
        }
        result = {key: value for key, value in temp_data.items() if value}
        return result

    def to_organizations(self) -> dict:
        """Convert structure_porteur & partenaire to activity's organizations"""

        temp_data = {}
        result = {key: value for key, value in temp_data.items() if value}
        return result

    def to_activity_type(self) ->str:
        """
        Converts type to activity's type.
        """
        return self.sous_type

    def to_financial_impact(self) -> FinancialImpactEnum:
        """
        Convert to FinancialImpactEnum based Recette/Dépense value.
        """
        recettes_len = len(self.recettes_convention)
        depenses_len = len(self.depenses_convention)

        if recettes_len == 0 and depenses_len == 0:
            return FinancialImpactEnum.AUCUNE

        if recettes_len > 0 and depenses_len > 0:
            raise ValueError(
                "Both recettes_convention and depenses_convention cannot have value simultaneously."
            )
        return (
            FinancialImpactEnum.RECETTE
            if recettes_len > 0
            else FinancialImpactEnum.DEPENSE
        )

    def to_amount(self) -> NonNegativeFloat:
        """
        Converts to amount if recettes has a value or depenses has a value.
        """
        try:
            amount = 0.0
            for str_amount in (
                self.recettes_convention,
                self.depenses_convention,
                self.montant_convention,
            ):
                if str_amount != "":
                    amount += NonNegativeFloat(str_amount)
            return amount
        except ValueError as e:
            raise ValueError(
                f"Invalid float value montant: {self.montant_convention},"
                f"recettes: {self.recettes_convention}"
                f"depenses: {self.depenses_convention}"
                f"for {self.reference}, amount equal 0 instead !",
            ) from e

    def to_datestart(self) -> str:
        """Convert DateDemarrage to activity's datestart"""
        return to_activity_date_format(self.date_demarrage)

    def to_dateend(self) -> str:
        """Convert TermeConvention to activity's dateend"""
        return to_activity_date_format(self.terme_convention)

    def to_milestones(self) -> list[Milestone]:
        """Convert Etape to activity's milestones"""
        return []
