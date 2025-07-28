import logging
from collections import defaultdict
import json
import csv
import os
from airflow.decorators import task
from sqlalchemy import false

logger = logging.getLogger(__name__)


@task
def extract_from_econvention(input_path: str) -> list[dict]:
    """
    Simulate a local `curl` to load data from econvention.
    TODO :
        Formatting the attributes with the attributes in map file.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Le fichier {input_path} est introuvable.")

    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@task
def extract_from_oscar(data : list[object]) -> list:
    pass


def transform(data: list[object], is_econvention_to_oscar: bool) -> list[dict]:
    dag_folder = os.path.dirname(os.path.abspath(__file__))
    mapping_path = os.path.join(dag_folder, "map_convention.csv")
    with open(mapping_path, mode="r", encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        map = [(row[0], row[1]) for row in reader]

    if is_econvention_to_oscar:
        mapping = {econv: oscar for econv, oscar in map}
    else:
        mapping = {oscar: econv for econv, oscar in map}

    # Transform data with attribute mapping
    transformed_data = [
        {
            mapping.get(key, key): value
            for key, value in item.items()
        }
        for item in data
    ]
    return transformed_data


@task
def transform_from_oscar_to_econvention(data : list[object]) -> list:
    return transform(data=data,is_econvention_to_oscar=False)

@task
def transform_from_econvention_to_oscar(data : list[object]) -> list:
    return transform(data=data,is_econvention_to_oscar=True)

@task
def load(data : list) -> str:
    return json.dumps(data, indent=3)

if __name__ == '__main__':
    transform([{"lol":"lol"}],False)

