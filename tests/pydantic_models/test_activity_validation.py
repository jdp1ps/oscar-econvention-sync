import pytest
from pydantic import ValidationError
from dags.models.activity_model import Activity

IMPOSTOR_VALUE = 18062018


def test_persons_is_normalized(activity_expected_data):
    """Ensure it extracts persons properly from a dict"""
    valid_raw_data = activity_expected_data[0]
    valid_activity_model = Activity.model_validate(valid_raw_data)
    assert valid_activity_model.persons == {
        "Chargé(e) de valorisation": ["Carine Souveyet Jarosz"],
    }

    valid_raw_data["persons"] = {"Role": "Membre"}
    valid_activity_model = Activity.model_validate(valid_raw_data)
    assert valid_activity_model.persons == {"Role": ["Membre"]}

    invalid_raw_data = valid_raw_data.copy()
    invalid_raw_data["persons"] = str(IMPOSTOR_VALUE)
    with pytest.raises(ValidationError):
        Activity.model_validate(invalid_raw_data)

    invalid_raw_data["persons"] = {"Fake role": IMPOSTOR_VALUE}
    with pytest.raises(ValidationError):
        Activity.model_validate(invalid_raw_data)


def test_organizations_is_normalized(activity_expected_data):
    """Ensure it extracts organizations properly from dict"""
    valid_raw_data = activity_expected_data[0]
    valid_activity_model = Activity.model_validate(valid_raw_data)
    assert valid_activity_model.organizations == {}

    valid_raw_data["organizations"] = {"Role": "Membre"}
    valid_activity_model = Activity.model_validate(valid_raw_data)
    assert valid_activity_model.organizations == {"Role": ["Membre"]}

    invalid_raw_data = valid_raw_data.copy()
    invalid_raw_data["organizations"] = str(IMPOSTOR_VALUE)
    with pytest.raises(ValidationError):
        Activity.model_validate(invalid_raw_data)

    invalid_raw_data["organizations"] = {"Role": IMPOSTOR_VALUE}
    with pytest.raises(ValidationError):
        Activity.model_validate(invalid_raw_data)


def test_date_is_iso_format(activity_expected_data, unique_logical_date):
    """
    Ensure that date fields has format YYYY-MM-DD.
    then ensure an exception is raised when a date is invalid
    """
    valid_raw_data = activity_expected_data[0]
    valid_convention_model = Activity.model_validate(valid_raw_data)
    assert valid_convention_model.datestart == "2024-09-01"

    valid_raw_data["datestart"] = "20/05/2025 00:00"
    valid_convention_bis = Activity.model_validate(valid_raw_data)
    assert valid_convention_bis.datestart == "2025-05-20"

    valid_raw_data["datestart"] = unique_logical_date.date().isoformat()
    valid_convention_bis = Activity.model_validate(valid_raw_data)
    assert valid_convention_bis.datestart == unique_logical_date.strftime("%Y-%m-%d")

    invalid_raw_data = valid_raw_data.copy()
    invalid_raw_data["datestart"] = str(IMPOSTOR_VALUE)
    with pytest.raises(ValidationError):
        Activity.model_validate(invalid_raw_data)

    invalid_raw_data["datestart"] = "2025-05-20"
    invalid_raw_data["dateend"] = "2000-01-01"
    with pytest.raises(ValidationError):
        Activity.model_validate(invalid_raw_data)


def test_amount_is_normalized(activity_expected_data):
    """Ensure it extracts amount properly from dict"""
    valid_raw_data = activity_expected_data[0]
    valid_convention_model = Activity.model_validate(valid_raw_data)
    assert valid_convention_model.amount == 500000.50

    valid_raw_data["amount"] = 666
    valid_convention_bis = Activity.model_validate(valid_raw_data)
    assert valid_convention_bis.amount == 666

    valid_raw_data["amount"] = 666.6
    valid_convention_bis = Activity.model_validate(valid_raw_data)
    assert valid_convention_bis.amount == 666.6

    invalid_raw_data = valid_raw_data.copy()
    invalid_raw_data["amount"] = -666.6
    with pytest.raises(ValidationError):
        Activity.model_validate(invalid_raw_data)


def test_milestones_is_normalized(activity_expected_data):
    """Ensure it extracts milestones properly from list[dict]"""
    valid_raw_data = activity_expected_data[0]
    valid_activity_model = Activity.model_validate(valid_raw_data)
    assert [
        model.model_dump(mode="json") for model in valid_activity_model.milestones
    ] == []

    valid_raw_data["milestones"] = [
        {
            "type": "Rapport scientifique",
            "date": "2017-01-07",
            "description": "DESCRIPTION RAPPORT SCIENTIFIQUE, DANS CET EXEMPLE COLONNE + 1 (35)",
        }
    ]
    valid_activity_model = Activity.model_validate(valid_raw_data)
    assert [
        model.model_dump(mode="json") for model in valid_activity_model.milestones
    ] == [
        {
            "type": "Rapport scientifique",
            "date": "2017-01-07",
            "description": "DESCRIPTION RAPPORT SCIENTIFIQUE, DANS CET EXEMPLE COLONNE + 1 (35)",
        }
    ]
    invalid_raw_data = valid_raw_data.copy()
    invalid_raw_data["milestones"] = [
        {
            "type": "Rapport scientifique",
            "date": str(IMPOSTOR_VALUE),
            "description": "DESCRIPTION RAPPORT SCIENTIFIQUE, DANS CET EXEMPLE COLONNE + 1 (35)",
        }
    ]
    with pytest.raises(ValidationError):
        Activity.model_validate(invalid_raw_data)


def test_payment_is_normalized(activity_expected_data):
    """Ensure it extracts payment properly from list[dict]"""
    valid_raw_data = activity_expected_data[0]
    valid_convention_model = Activity.model_validate(valid_raw_data)
    assert valid_convention_model.payments == []

    valid_raw_data["payments"] = [
        {"amount": 20000, "date": "2017-01-07", "predicted": "2017-01-01"}
    ]
    valid_convention_bis = Activity.model_validate(valid_raw_data)
    assert [
        payment.model_dump(mode="json") for payment in valid_convention_bis.payments
    ] == [{"amount": 20000, "date": "2017-01-07", "predicted": "2017-01-01"}]
    invalid_raw_data = valid_raw_data.copy()
    invalid_raw_data["payments"] = [
        {"amount": 20000, "date": str(IMPOSTOR_VALUE), "predicted": "2017-01-01"}
    ]
    with pytest.raises(ValidationError):
        Activity.model_validate(invalid_raw_data)

    invalid_raw_data["payments"] = [
        {"amount": -1, "date": "2017-01-07", "predicted": "2017-01-01"}
    ]
    with pytest.raises(ValidationError):
        Activity.model_validate(invalid_raw_data)
