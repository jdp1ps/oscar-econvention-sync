from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, field_validator, PositiveFloat
from utils.iso_date import DATE_PATTERN, to_iso_date, ensure_start_before_end


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

    amount: PositiveFloat
    date: str | None = Field(default=None, pattern=DATE_PATTERN)
    predicted: str | None = Field(default=None, pattern=DATE_PATTERN)


class Milestone(BaseModel):
    """
    Milestone in activity fields with required fields to import in OSCAR
    """

    type: str
    date: str | None = Field(default=None, pattern=DATE_PATTERN)
    description: str = ""


class Activity(BaseModel):
    """
    Activity representation in OSCAR, fields required to import in OSCAR
    """

    uid: str
    acronym: str = Field(default_factory=lambda: datetime.now().date().isoformat())
    projectlabel: str = Field(default_factory=lambda: datetime.now().date().isoformat())
    label: str
    persons: dict = {}
    organizations: dict = {}
    description: str = ""
    datestart: str | None = Field(default=None, pattern=DATE_PATTERN)
    dateend: str | None = Field(default=None, pattern=DATE_PATTERN)
    datesigned: str | None = Field(default=None, pattern=DATE_PATTERN)
    datePFI: str | None = Field(default=None, pattern=DATE_PATTERN)
    pfi: str = ""
    type: str = ""
    amount: PositiveFloat | None = None
    tva: PositiveFloat | None = None
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
    def check_date_format(cls, raw_date):
        """wrapper to call to_iso_date used by models"""
        return to_iso_date(raw_date)

    def to_reference(self):
        """Convert uid to convention's reference"""
        return self.to_uid()

    def to_titre(self):
        """Convert label to convention's title"""
        return self.label

    def to_porteur(self):
        """Convert part of persons to convention's porteur"""
        return self.persons.get("Porteur")

    def to_createur(self):
        """Convert part of persons to convention's createur"""
        return self.persons.get("Createur")

    def to_structure(self):
        """Convert a part of organizations to convention's structure"""
        return self.organizations.get("Structure")

    def to_partenaire(self):
        """Convert a part of organizations to convention's partenaire"""
        return self.organizations.get("Partenaire")

    def to_convention_type(self):
        """
        Convert type to convention's type
        [TEMPORARY IMPLEMENTATION] This method currently returns an empty string as a placeholder.
        """
        return ""

    def to_date_demarrage(self):
        """Convert datestart to convention's date_demarrage"""
        return self.datestart

    def to_terme_convention(self):
        """Convert dateend to convention's terme_convention"""
        return self.dateend

    def to_etape(self):
        """Convert milestones to convention's etape"""
        return self.milestones
