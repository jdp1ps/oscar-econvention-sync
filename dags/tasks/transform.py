from airflow.decorators import task
from utils.mapping import map_convention, defaults


@task
def transform_from_econvention_to_oscar(data: list[dict]) -> list[dict]:
    """
    Maps econvention fields to OSCAR format using a predefined dictionary (map_convention).

    For most fields, the mapping is direct (e.g., 'Reference' → 'uid').
    Fields mapped to 'persons' or 'organizations' are grouped into subdictionaries.
    Missing keys are completed with default values.

    Args:
        data (list[dict]): A list of dictionaries containing raw data from econvention.

    Returns:
        list[dict]: A list of transformed dictionaries ready for OSCAR ingestion.
    """
    mapping = map_convention

    transformed_data = []
    for item in data:
        transformed_item = {}

        for key, value in item.items():
            if key not in mapping:
                continue
            new_key = mapping[key]

            if new_key in {"persons", "organizations"}:
                transformed_item.setdefault(new_key, {})[key] = [value]
            else:
                transformed_item[new_key] = value

        for key, default_value in defaults.items():
            if key not in transformed_item:
                transformed_item[key] = default_value

        transformed_data.append(transformed_item)

    return transformed_data
