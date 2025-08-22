import pytest
from pydantic import ValidationError
from dags.models.convention_model import Convention, OrigineEnum

IMPOSTOR_VALUE = 18062018


def test_createur_is_normalized(convention_raw_data):
    """Ensure it extracts Créateur properly from a dict"""
    valid_raw_data = convention_raw_data[1]
    valid_convention_model = Convention.model_validate(valid_raw_data)
    assert valid_convention_model.Createur == "econvention"

    invalid_raw_data = valid_raw_data.copy()
    invalid_raw_data["Créateur"] = IMPOSTOR_VALUE
    with pytest.raises(ValidationError):
        Convention.model_validate(invalid_raw_data)


def test_origine_is_normalized(convention_raw_data):
    """Ensure it extracts Origine de la convention properly from a dict"""
    valid_raw_data = convention_raw_data[1]
    valid_convention_model = Convention.model_validate(valid_raw_data)
    assert valid_convention_model.Origine_de_la_convention == OrigineEnum.INTERNE

    valid_raw_data["Origine de la convention"] = "Partenaire"
    valid_convention_model = Convention.model_validate(valid_raw_data)
    assert valid_convention_model.Origine_de_la_convention == OrigineEnum.PARTENAIRE

    invalid_raw_data = valid_raw_data.copy()
    invalid_raw_data["Origine de la convention"] = str(IMPOSTOR_VALUE)
    with pytest.raises(ValidationError):
        Convention.model_validate(invalid_raw_data)


def test_partenaire_is_normalized(convention_raw_data):
    """Ensure it extracts Partenaire properly from a list[dict]"""
    valid_raw_data = convention_raw_data[1]
    valid_convention_model = Convention.model_validate(valid_raw_data)
    assert valid_convention_model.Partenaire == ["Partenaire 1", "Partenaire 2"]

    valid_raw_data["Partenaire"] = []
    valid_convention_bis = Convention.model_validate(valid_raw_data)
    assert valid_convention_bis.Partenaire == []

    valid_raw_data["Partenaire"] = None
    valid_convention_bis = Convention.model_validate(valid_raw_data)
    assert valid_convention_bis.Partenaire == []

    invalid_raw_data = valid_raw_data.copy()
    invalid_raw_data["Partenaire"] = IMPOSTOR_VALUE
    with pytest.raises(ValidationError):
        Convention.model_validate(invalid_raw_data)


def test_date_is_iso_format(convention_raw_data, unique_logical_date):
    """
    Ensure that date fields has format YYYY-MM-DD.
    then ensure an exception is raised when a date is invalid
    """
    valid_raw_data = convention_raw_data[1]
    valid_convention_model = Convention.model_validate(valid_raw_data)
    assert valid_convention_model.DateDemarrage == "2025-05-20"

    valid_raw_data["DateDemarrage"] = "20/05/2025"
    valid_convention_bis = Convention.model_validate(valid_raw_data)
    assert valid_convention_bis.DateDemarrage == "2025-05-20"

    valid_raw_data["DateDemarrage"] = str(unique_logical_date)
    valid_convention_bis = Convention.model_validate(valid_raw_data)
    assert valid_convention_bis.DateDemarrage == str(
        unique_logical_date.date().isoformat()
    )

    invalid_raw_data = valid_raw_data.copy()
    invalid_raw_data["DateDemarrage"] = str(IMPOSTOR_VALUE)
    with pytest.raises(ValidationError):
        Convention.model_validate(invalid_raw_data)

    invalid_raw_data["DateDemarrage"] = "2025-05-20"
    invalid_raw_data["TermeConvention"] = "2000-01-01"
    with pytest.raises(ValidationError):
        Convention.model_validate(invalid_raw_data)
