from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, field_validator, PositiveFloat
from models.iso_date import DATE_PATTERN, to_iso_date, ensure_start_before_end


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
    amount: PositiveFloat | None = None
    tva: PositiveFloat | None = None
    currency: CurrencyEnum = CurrencyEnum.EURO
    financialImpact: FinancialImpactEnum = FinancialImpactEnum.AUCUNE
    milestones: list[dict] = []
    status: StatusEnum = StatusEnum.CONFLIT
    payments: list[dict] = []

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

    @field_validator("payments", mode="after")
    @classmethod
    def validate_payments(cls, payments: list[dict]) -> list[dict]:
        """
        Ensure that each milestone dictionary contains the required keys:
            - "amount": PositiveFloat or None
            - "date": str (validated and converted to ISO format)
            - "predicted": str (validated and converted to ISO format)

        If any key is missing, a ValueError is raised.
        The "date" and "predicted" fields are normalized using `to_iso_date`.
        """
        required_keys = {"amount", "date", "predicted"}
        for i, payment in enumerate(payments):
            missing = required_keys - payment.keys()
            if missing:
                raise ValueError(f"Payment {i} is missing keys: {missing}")
            amount = payment.get("amount")
            if not isinstance(amount, (int, float)):
                raise TypeError(
                    f"Payment {i} 's amount must be a number, got {type(amount).__name__}"
                )
            if amount < 0:
                raise ValueError(f"Payment {i} 's amount is negative: {amount}")
            payment["date"] = to_iso_date(payment["date"])
            payment["predicted"] = to_iso_date(payment["predicted"])

        return payments

    @field_validator("milestones", mode="after")
    @classmethod
    def validate_milestones(cls, milestones: list[dict]) -> list[dict]:
        """
        Ensure that each milestone dictionary contains the required keys:
            - "type": str
            - "date": str (validated and converted to ISO format)
            - "description": str

        If any key is missing, a ValueError is raised.
        The "date" field is normalized using `to_iso_date`.
        """

        required_keys = {"type", "date", "description"}
        for i, milestone in enumerate(milestones):
            missing = required_keys - milestone.keys()
            if missing:
                raise ValueError(f"Milestone {i} is missing keys: {missing}")
            milestone["date"] = to_iso_date(milestone["date"])
        return milestones
