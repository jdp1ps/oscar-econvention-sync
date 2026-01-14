from pydantic import (
    BaseModel,
    Field,
    NonNegativeFloat,
)
from utils.date_utils import ACTIVITY_DATE_PATTERN


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
