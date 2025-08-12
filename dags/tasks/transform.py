from airflow.decorators import task
from models.oscar_factory import OscarFactory


@task
def transform_from_econvention_to_oscar(econventions: list[dict]) -> str:
    """Transform from ECONVENTION to OSCAR with factory design pattern."""
    return OscarFactory.convert_from(econventions)
