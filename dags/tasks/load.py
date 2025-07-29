import json
from airflow.decorators import task


@task
def load(data: list[dict]) -> str:
    """
    Serializes the transformed data into a JSON string.

    Args:
        data: The final list of dictionaries to be loaded.

    Returns:
        A JSON-formatted string of the data.
    """
    return json.dumps(data, indent=4)
