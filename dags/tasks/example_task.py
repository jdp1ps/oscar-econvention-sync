import logging
from collections import defaultdict

from airflow.decorators import task

logger = logging.getLogger(__name__)


@task
def example_task(input_data: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    """
    Test task that processes input data and returns a dictionary.
    :param input_data: A list of dictionaries containing input data
    :return: A dictionary where each key is a unique identifier from the input data,
    """
    combined_results = defaultdict(dict)
    for entry in input_data:
        identifier = entry.get("id", "default_id")
        combined_results[identifier].update(entry)
    logger.info("Processed input data: %s", combined_results)
    return combined_results
