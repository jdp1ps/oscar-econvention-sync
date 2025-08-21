from airflow.decorators import task
from pydantic import ValidationError
from models.convention_model import Convention


@task
def extract_from_econvention(**context) -> list[dict]:
    """
    Extract data from REST API POST sent by eConvention
    then this raw API payload is cleaned before being instantiated.
    :param context: given automatically by Airflow which contains API payload
    :return: list of econvention instances formatted into JSON string.
    """
    raw_conventions = context["dag_run"].conf.get("items")
    if raw_conventions is None:
        raise ValueError("Missing 'items' key in dag_run.conf.")
    if not isinstance(raw_conventions, list):
        raise ValueError("Expected 'items' to be a list of dictionaries.")
    if not all(isinstance(item, dict) for item in raw_conventions):
        raise ValueError("All items in 'items' must be dictionaries.")

    convention_list: list[Convention] = []
    errors = []
    for i, convention in enumerate(raw_conventions):
        try:
            convention_list.append(Convention.model_validate(convention))
        except ValidationError as e:
            errors.append({"index": i, "errors": e.errors()})
    if errors:
        raise ValueError(f"Some conventions failed validation: {errors}")

    results = [econvention.model_dump() for econvention in convention_list]
    return results
