import pytest
from pydantic import ValidationError
from dags.models.convention_model import (
    Convention,
    OrigineEnum,
    RESPONSABLE_PORTEUR_ALIAS,
    ORIGINE_CONVENTION_ALIAS,
    PARTENAIRE_ALIAS,
)
from utils.date_utils import to_convention_date_format

IMPOSTOR_VALUE = 18062018


def test_responsable_porteur_is_normalized(convention_raw_data):
    """Ensure it extracts Créateur properly from a dict"""
    valid_raw_data = convention_raw_data[0]
    valid_convention_model = Convention.model_validate(valid_raw_data)
    assert (
        valid_convention_model.responsable_porteur == "Personnels:Roles:DIR UFR UFR 27"
    )

    invalid_raw_data = valid_raw_data.copy()
    invalid_raw_data[RESPONSABLE_PORTEUR_ALIAS] = IMPOSTOR_VALUE
    with pytest.raises(ValidationError):
        Convention.model_validate(invalid_raw_data)


def test_origine_is_normalized(convention_raw_data):
    """Ensure it extracts Origine de la convention properly from a dict"""
    valid_raw_data = convention_raw_data[0]
    valid_convention_model = Convention.model_validate(valid_raw_data)
    assert valid_convention_model.origine_de_la_convention == OrigineEnum.INTERNE

    valid_raw_data[ORIGINE_CONVENTION_ALIAS] = "Partenaire"
    valid_convention_model = Convention.model_validate(valid_raw_data)
    assert valid_convention_model.origine_de_la_convention == OrigineEnum.PARTENAIRE

    invalid_raw_data = valid_raw_data.copy()
    invalid_raw_data[ORIGINE_CONVENTION_ALIAS] = str(IMPOSTOR_VALUE)
    with pytest.raises(ValidationError):
        Convention.model_validate(invalid_raw_data)


def test_partenaire_is_normalized(convention_raw_data):
    """Ensure it extracts Partenaire properly from a list[dict]"""
    valid_raw_data = convention_raw_data[0]
    valid_convention_model = Convention.model_validate(valid_raw_data)
    assert valid_convention_model.partenaire == "Association PIVOD"

    valid_raw_data[PARTENAIRE_ALIAS] = ""
    valid_convention_bis = Convention.model_validate(valid_raw_data)
    assert valid_convention_bis.partenaire == ""

    invalid_raw_data = valid_raw_data.copy()
    invalid_raw_data[PARTENAIRE_ALIAS] = None
    with pytest.raises(ValidationError):
        Convention.model_validate(invalid_raw_data)

    invalid_raw_data[PARTENAIRE_ALIAS] = IMPOSTOR_VALUE
    with pytest.raises(ValidationError):
        Convention.model_validate(invalid_raw_data)


def test_date_is_iso_format(convention_raw_data, unique_logical_date):
    """
    Ensure that date fields has format DD/MM/YYYY hh:mm.
    then ensure an exception is raised when a date is invalid
    """
    valid_raw_data = convention_raw_data[0]
    valid_convention_model = Convention.model_validate(valid_raw_data)
    assert valid_convention_model.date_demarrage == "01/09/2024 00:00"

    valid_raw_data["DateDemarrage"] = "2025-05-20"
    valid_convention_bis = Convention.model_validate(valid_raw_data)
    assert valid_convention_bis.date_demarrage == "20/05/2025 00:00"

    valid_raw_data["DateDemarrage"] = str(unique_logical_date)
    valid_convention_bis = Convention.model_validate(valid_raw_data)
    assert valid_convention_bis.date_demarrage == to_convention_date_format(
        str(unique_logical_date)
    )

    invalid_raw_data = valid_raw_data.copy()
    invalid_raw_data["DateDemarrage"] = str(IMPOSTOR_VALUE)
    with pytest.raises(ValidationError):
        Convention.model_validate(invalid_raw_data)

    invalid_raw_data["DateDemarrage"] = "01/09/2027 00:00"
    invalid_raw_data["TermeConvention"] = "01/09/2024 00:00"
    with pytest.raises(ValidationError):
        Convention.model_validate(invalid_raw_data)
