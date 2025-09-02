from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    field_validator,
    NonNegativeFloat,
)
from utils.type_utils import CONVENTION_SOUS_TYPE_ENUM, ACTIVITY_TYPE_ENUM
from utils.date_utils import (
    ACTIVITY_DATE_PATTERN,
    to_iso_date,
    to_convention_date_format,
    ensure_start_before_end,
)
from utils.aliases import (
    PORTEUR_ALIAS,
    STRUCTURE_PORTEUR_ALIAS,
    RESPONSABLE_PORTEUR_ALIAS,
    REFERENT_DAJI_ALIAS,
    PARTENAIRE_ALIAS,
)


class FinancialImpactEnum(str, Enum):
    """
    3 possibles values for FinancialImpact
    """

    AUCUNE = "Aucune"
    RECETTE = "Recette"
    DEPENSE = "Dépense"


class CurrencyEnum(str, Enum):
    """
    4 possible values for Currency
    """

    EURO = "Euro"
    YENS = "Yens"
    LIVRE = "Livre"
    DOLLARS = "Dollars"


class StatusEnum(int, Enum):
    """
    Possible values for Status
    """

    ACTIF = 101
    BROUILLON = 102
    DEPOSE = 103
    TERMINE = 200
    RESILIE = 201
    ABANDONNE = 250
    REFUSE = 201  # alias pour RESILIE
    CONFLIT = 404  # Pas de statut


class Payment(BaseModel):
    """
    Payment in activity fields with required fields to import in OSCAR
    """

    amount: NonNegativeFloat
    date: str | None = Field(default=None, pattern=ACTIVITY_DATE_PATTERN)
    predicted: str | None = Field(default=None, pattern=ACTIVITY_DATE_PATTERN)


class Milestone(BaseModel):
    """
    Milestone in activity fields with required fields to import in OSCAR
    """

    type: str
    date: str | None = Field(default=None, pattern=ACTIVITY_DATE_PATTERN)
    description: str = ""


class Activity(BaseModel):
    """
    Activity representation in OSCAR, fields required to import in OSCAR
    """

    uid: str
    acronym: str = Field(default_factory=lambda: "~")
    projectlabel: str = Field(default_factory=lambda: "~")
    label: str
    persons: dict = {}
    organizations: dict = {}
    description: str = ""
    datestart: str | None = Field(default=None, pattern=ACTIVITY_DATE_PATTERN)
    dateend: str | None = Field(default=None, pattern=ACTIVITY_DATE_PATTERN)
    datesigned: str | None = Field(default=None, pattern=ACTIVITY_DATE_PATTERN)
    datePFI: str | None = Field(default=None, pattern=ACTIVITY_DATE_PATTERN)
    pfi: str = ""
    type: ACTIVITY_TYPE_ENUM | CONVENTION_SOUS_TYPE_ENUM = "Autre"
    amount: NonNegativeFloat | None = None
    tva: NonNegativeFloat | None = None
    currency: CurrencyEnum = CurrencyEnum.EURO
    financialImpact: FinancialImpactEnum = FinancialImpactEnum.AUCUNE
    milestones: list[Milestone] = []
    status: StatusEnum = StatusEnum.CONFLIT
    payments: list[Payment] = []

    @model_validator(mode="after")
    @classmethod
    def check_dates_order(cls, activity):
        """Ensure datestart is before dateend."""
        ensure_start_before_end(
            activity.datestart,
            activity.dateend,
            start_name="datestart",
            end_name="dateend",
        )
        return activity

    @field_validator("persons", "organizations")
    @classmethod
    def check_dict_format(cls, v):
        """
        Ensure that fields persons and organizations formats as:
        "organizations"/"persons": {
            "Role A": ['name1', 'name2'],
            "Role B": ["name3"]
          }
        """
        for role, entities in v.items():
            if not isinstance(role, str):
                raise ValueError(f"Invalid key type: {type(role).__name__}")
            if isinstance(entities, str):
                v[role] = [entities]
            elif not isinstance(entities, list):
                raise ValueError(
                    f"Invalid value type for role {role}: {type(entities).__name__}"
                )
        return v

    @field_validator("datestart", "dateend", "datesigned", mode="before")
    @classmethod
    def check_date_format(cls, raw_date) -> str:
        """wrapper to call to_iso_date used by models"""
        return to_iso_date(raw_date)

    def to_reference(self) -> str:
        """Convert uid to convention's reference"""
        return self.uid

    def to_titre(self) -> str:
        """Convert label to convention's title"""
        return self.label

    def to_porteur(self) -> str:
        """Convert part of persons to convention's porteur"""
        porteur = self.persons.get(PORTEUR_ALIAS)
        if porteur is None:
            raise ValueError(f"Invalid porteur: {porteur}")
        return porteur[0]

    def to_responsable_porteur(self) -> str:
        """Convert part of persons to convention's responsable porteur"""
        return self.persons.get(RESPONSABLE_PORTEUR_ALIAS, "")

    def to_referent_daji(self) -> str:
        """Convert part of persons to convention's referent"""
        return self.persons.get(REFERENT_DAJI_ALIAS, "")

    def to_structure(self) -> str:
        """Convert a part of organizations to convention's structure"""
        return self.persons.get(STRUCTURE_PORTEUR_ALIAS, "")

    def to_partenaire(self) -> str:
        """Convert a part of organizations to convention's partenaire"""
        return self.persons.get(PARTENAIRE_ALIAS, "")

    def to_convention_type(self) -> str:
        """
        Convert type to convention's type
        """
        return self.type

    def to_date_demarrage(self) -> str:
        """Convert datestart to convention's date_demarrage"""
        return to_convention_date_format(self.datestart)

    def to_terme_convention(self) -> str:
        """Convert dateend to convention's terme_convention"""
        return to_convention_date_format(self.dateend)

    def to_etape(self) -> str:
        """Return to convention's initial etape"""
        return "0 - Brouillon"
