from airflow.decorators import task
from utils.mapping import map_convention, defaults


@task
def transform_from_econvention_to_oscar(data: list[dict]) -> list[dict]:
    """

    :param data:
    :return:
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
