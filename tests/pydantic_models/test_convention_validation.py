import pytest
from pydantic import ValidationError
from dags.models.convention_model import Convention, OrigineEnum

RAW_DATA = {
    "Titre": "test1",
    "Reference": "test1",
    "Porteur": "econvention",
    "Sticture Porteur": "Structure1",
    "Partenaire": [{"DisplayName": "Lab1"}, {"DisplayName": "Lab2"}],
    "Créateur": {"DisplayName": "econvention"},
    "Origine de la convention": {"id": 1, "Value": "Interne"},
    "DateDemarrage": "1111-11-11",
}
CONVENTION_MODEL = Convention.model_validate(RAW_DATA)


def test_createur_is_normalized():
    """Ensure it extracts Créateur properly from a dict"""
    assert CONVENTION_MODEL.Createur == "econvention"


def test_origine_is_normalized():
    """Ensure it extracts Origine de la convention properly from a dict"""
    assert CONVENTION_MODEL.Origine_de_la_convention == OrigineEnum.INTERNE


def test_partenaire_is_normalized():
    """Ensure it extracts Partenaire properly from a list[dict]"""
    assert CONVENTION_MODEL.Partenaire == ["Lab1", "Lab2"]


def test_invalid_date_fails():
    """Ensure an exception is raised when a date is invalid"""
    RAW_DATA["DateDemarrage"] = "11/11/1111"
    with pytest.raises(ValidationError):
        Convention.model_validate(RAW_DATA)
