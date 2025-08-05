from airflow.decorators import task
from utils.mapping import map_convention, defaults, oscar_special_keys


def nest_special_keys(item: dict, value: dict, econvention_key) -> dict:
    """
    Handler of special oscar keys by merging or appending values
    to a dictionary under a specific key.

    The function is designed to handle keys that have the following structure:
    {
        "econvention_key": ["value1", "value2", ...],
        "another_key": ["value3", "value4", ...],
        ...
    }
    :arg:
    item : dict
        The dictionary to update or extend. If None, it will be initialized as an empty dict.
    value : dict or list
        The value(s) associated with the `econvention_key`.
        !!! Elements inside must be dictionaries with a "DisplayName" key !!!
    econvention_key : hashable
        The key under which the processed values will be stored/appended in the `item` dictionary.
    :return:
        The updated dictionary `item` with the econvention_key mapping to a list of values.

    Example:
    --------
    data :
    item = {"key1": ["Value1"]}
    value = [{"DisplayName": "Value2"}] or {"DisplayName": "Value2"}
    econvention_key = "key1"
    result :
    nest_special_keys(item, value, econvention_key) gives :
        {'key1': ['Value1', 'Value2']}
    """
    if item is None:
        item = {}

    # Extract display name if applicable
    if isinstance(value, list):
        values = [v.get("DisplayName", v) if isinstance(v, dict) else v for v in value]
    else:
        values = [value.get("DisplayName", value) if isinstance(value, dict) else value]

    if econvention_key not in item:
        item[econvention_key] = values
    else:
        item[econvention_key].extend(values)

    return item


def transform_econvention_to_oscar(data: list[dict]) -> list[dict]:
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
        for econvention_key, value in item.items():
            if econvention_key not in mapping:
                continue
            oscar_key = mapping[econvention_key]

            if oscar_key in oscar_special_keys:
                transformed_item.setdefault(oscar_key, {})
                transformed_item[oscar_key] = nest_special_keys(
                    transformed_item[oscar_key], value, econvention_key
                )

            else:
                transformed_item[oscar_key] = value

        for econvention_key, default_value in defaults.items():
            if econvention_key not in transformed_item:
                transformed_item[econvention_key] = default_value

        transformed_data.append(transformed_item)

    return transformed_data


@task
def transform_from_econvention_to_oscar(data: list[dict]) -> list[dict]:
    """Wrapper for transform_econvention_to_oscar."""
    return transform_econvention_to_oscar(data)
