from airflow.decorators import task
from pydantic import ValidationError
from models.convention_model import Convention
from utils.type_utils import ensure_list_of_dict


@task
def receive_from_econvention(**context) -> list[dict]:
    """
    Receive data from REST API POST sent by eConvention
    then this raw API payload is cleaned before being instantiated.
    :param context: given automatically by Airflow which contains API payload
    :return: list of econvention instances formatted into JSON string.
    """
    raw_conventions = ensure_list_of_dict(context["dag_run"].conf.get("items"))

    convention_list: list[Convention] = []
    errors = []
    for i, convention in enumerate(raw_conventions):
        try:
            convention_list.append(Convention.model_validate(convention))
        except ValidationError as e:
            errors.append({"index": i, "errors": e.errors()})
    if len(errors) > 0:
        raise ValueError(f"Some conventions failed validation: {errors}")

    results = [convention.model_dump() for convention in convention_list]
    return results
