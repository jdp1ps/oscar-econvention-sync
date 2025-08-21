from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from models.iso_date import DATE_PATTERN, to_iso_date


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
    amount: float | None = None
    tva: float | None = None
    currency: CurrencyEnum = CurrencyEnum.EURO
    financialImpact: FinancialImpactEnum = FinancialImpactEnum.AUCUNE
    milestones: list[dict] = []
    status: StatusEnum = StatusEnum.CONFLIT
    payments: list[dict] = []

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
        """
        wrapper to call to_iso_date used by models
        """
        return to_iso_date(raw_date)
