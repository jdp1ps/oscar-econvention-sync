import pytest
import pendulum
from airflow.models import DagBag

@pytest.fixture(name="unique_logical_date")
def unique_logical_date() -> pendulum.DateTime:
    """
    Get a unique execution date to avoid conflicts between tests
    :return: The unique execution date
    """
    return pendulum.now()

@pytest.fixture()
def dagbag():
    """
    Create a DagBag for testing dag loading
    :return:
    """
    return DagBag()
