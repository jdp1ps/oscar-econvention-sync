import os
import sys
import json
from pathlib import Path
import pytest
import pendulum
from airflow.models import DagBag

dags_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dags"))
if dags_path not in sys.path:
    sys.path.insert(0, dags_path)


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


DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def econvention_raw_data():
    """
    Load the raw ECONVENTION data.
    :return:
    """
    with open(DATA_DIR / "econvention_raw_data.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def oscar_expected_data():
    """
    Load the expected OSCAR data.
    :return:
    """
    with open(DATA_DIR / "oscar_expected_data.json", encoding="utf-8") as f:
        return json.load(f)
