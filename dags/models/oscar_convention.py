from datetime import datetime
from typing import Optional
from pydantic import Field, PositiveInt, field_validator
from models.abstract_models import SyncConvention


class OscarConvention(SyncConvention):
    """
    Activity representation in OSCAR, fields required to import in OSCAR
    """

    uid: str
    acronym: str = Field(default_factory=lambda: datetime.now().date().isoformat())
    projectlabel: str = Field(default_factory=lambda: datetime.now().date().isoformat())
    label: str
    persons: Optional[dict] = {}
    organizations: Optional[dict] = {}
    description: str = ""
    type: Optional[str] = ""
    pfi: Optional[str] = ""
    datestart: str = ""
    dateend: str = ""
    financialImpact: Optional[str] = "Aucune"
    milestones: Optional[list[str]] = []
    status: PositiveInt = 200

    @field_validator("persons", "organizations", mode="before")
    @classmethod
    def ensure_dict_format(cls, v):
        """
        Ensure that the fields persons and organizations formats as :
        "organizations"/"persons": {
            "Role A": [],
            "Role B": []
          }
        """
        if not isinstance(v, dict):
            raise TypeError(f"Expected dict, got {type(v).__name__}")
        new_dict = {}
        for role, entities in v.items():
            if entities is None:
                new_dict[role] = []
            elif isinstance(entities, str):
                new_dict[role] = [entities]
            elif isinstance(entities, list):
                new_dict[role] = entities
            else:
                raise TypeError(
                    f"Invalid value for role {role}: {type(entities).__name__}"
                )
        return new_dict

    @field_validator("persons", "organizations", mode="after")
    @classmethod
    def check_dict_format(cls, v):
        """
        Ensure that the fields persons and organizations formats as :
        "organizations"/"persons": {
            "Role A": [],
            "Role B": []
          }
        """
        for role, entities in v.items():
            if not isinstance(role, str):
                raise ValueError(f"Invalid key type: {type(role).__name__}")
            if not isinstance(entities, list):
                raise ValueError(
                    f"Invalid value type for role {role}: {type(entities).__name__}"
                )
        return v
