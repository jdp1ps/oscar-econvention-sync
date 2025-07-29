import csv
import os
from airflow.decorators import task


def transform(data: list[dict], econvention_to_oscar: bool) -> list[dict]:
    """
    Transforms data by mapping keys based on a CSV file.

    Args:
        data: A list of dictionaries to transform.
        econvention_to_oscar: If True, maps eConvention keys to Oscar keys.
                              Otherwise, maps Oscar to eConvention.

    Returns:
        A list of transformed dictionaries.
    """
    dag_folder = os.path.dirname(os.path.abspath(__file__))
    mapping_path = os.path.join(dag_folder, "map_convention.csv")

    with open(mapping_path, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=";")
        # Avoid redefining the built-in 'map'
        attribute_map_list = [(row[0], row[1]) for row in reader]

    if econvention_to_oscar:
        # Use dict() for a more concise and efficient conversion
        mapping = dict(attribute_map_list)
    else:
        # Reverse the mapping
        mapping = {oscar: econv for econv, oscar in attribute_map_list}

    # Transform data using the created attribute mapping
    transformed_data = [
        {mapping.get(key, key): value for key, value in item.items()} for item in data
    ]
    return transformed_data


@task
def transform_from_oscar_to_econvention(data: list[dict]) -> list[dict]:
    """Wrapper to convert Oscar -> eConvention format."""
    return transform(data=data, econvention_to_oscar=False)


@task
def transform_from_econvention_to_oscar(data: list[dict]) -> list[dict]:
    """Wrapper to convert eConvention -> Oscar format."""
    return transform(data=data, econvention_to_oscar=True)
