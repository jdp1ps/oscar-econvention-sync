from datetime import datetime
from pydantic import BaseModel, Field, PositiveInt, field_validator


class OscarConvention(BaseModel):
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
    type: str = ""
    pfi: str = ""
    datestart: str = ""
    dateend: str = ""
    financialImpact: str = "Aucune"
    milestones: list[str] = []
    status: PositiveInt = 200

    @field_validator("persons", "organizations")
    @classmethod
    def check_dict_format(cls, v):
        """
        Ensure that the fields persons and organizations formats as :
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
