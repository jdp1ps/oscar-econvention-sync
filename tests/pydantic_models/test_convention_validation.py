from datetime import datetime
import pytest
from pydantic import ValidationError
from dags.models.convention_model import Convention, OrigineEnum
from tests.conftest import CONVENTION_RAW_DATA

VALID_RAW_DATA = CONVENTION_RAW_DATA[1]
VALID_CONVENTION_MODEL = Convention.model_validate(VALID_RAW_DATA)
IMPOSTOR_VALUE = 18062018


def test_createur_is_normalized():
    """Ensure it extracts Créateur properly from a dict"""
    assert VALID_CONVENTION_MODEL.Createur == "econvention"
    unvalid_raw_data = VALID_RAW_DATA.copy()
    unvalid_raw_data["Créateur"] = IMPOSTOR_VALUE
    with pytest.raises(ValidationError):
        Convention.model_validate(unvalid_raw_data)


def test_origine_is_normalized():
    """Ensure it extracts Origine de la convention properly from a dict"""
    assert VALID_CONVENTION_MODEL.Origine_de_la_convention == OrigineEnum.INTERNE
    unvalid_raw_data = VALID_RAW_DATA.copy()
    unvalid_raw_data["Origine de la convention"] = str(IMPOSTOR_VALUE)
    with pytest.raises(ValidationError):
        Convention.model_validate(unvalid_raw_data)


def test_partenaire_is_normalized():
    """Ensure it extracts Partenaire properly from a list[dict]"""
    assert VALID_CONVENTION_MODEL.Partenaire == ["Partenaire 1", "Partenaire 2"]
    unvalid_raw_data = VALID_RAW_DATA.copy()
    unvalid_raw_data["Partenaire"] = IMPOSTOR_VALUE
    with pytest.raises(ValidationError):
        Convention.model_validate(unvalid_raw_data)


def test_invalid_date_fails(unique_logical_date):
    """
    Ensure that date fields has format YYYY-MM-DD.
    then ensure an exception is raised when a date is invalid
    """
    valid_raw_data_bis = VALID_RAW_DATA.copy()
    valid_raw_data_bis["DateDemarrage"] = str(unique_logical_date)
    valid_convention_bis = Convention.model_validate(valid_raw_data_bis)
    assert valid_convention_bis.DateDemarrage == str(datetime.now().date().isoformat())
    unvalid_raw_data = VALID_RAW_DATA.copy()
    unvalid_raw_data["DateDemarrage"] = str(IMPOSTOR_VALUE)
    with pytest.raises(ValidationError):
        Convention.model_validate(unvalid_raw_data)
