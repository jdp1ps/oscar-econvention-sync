import os
import pytest
import pendulum
from airflow import settings
from airflow.models import DagBag
from airflow.utils.db import resetdb


@pytest.fixture(name="unique_logical_date")
def unique_logical_date() -> pendulum.DateTime:
    """
    Get a unique execution date to avoid conflicts between tests
    :return: The unique execution date
    """
    return pendulum.now()


@pytest.fixture(scope="function", autouse=True, name="initialize_airflow_db")
def initialize_airflow_db() -> None:
    """
    Initialize the airflow database for testing and reset the database before each test
    :return: None
    """
    os.environ["AIRFLOW__CORE__SQL_ALCHEMY_CONN"] = "sqlite:////:memory:"
    resetdb()
    settings.configure_orm()


@pytest.fixture(name="dagbag")
def fixture_dagbag() -> DagBag:
    """
    Create a DagBag for testing dag loading
    :return: DagBag
    """
    airflow_home = os.getenv("AIRFLOW_HOME")
    assert airflow_home is not None, "AIRFLOW_HOME is not set"
    dag_folder = f"{airflow_home}/dags"
    print(f"Dag folder is : {dag_folder}")
    return DagBag(dag_folder=dag_folder)


@pytest.fixture(name="test_data_path")
def fixture_test_data_path():
    """
    Return the path to the test data file located in tests/demo_data/test_econvention.json
    """
    current_dir = os.path.dirname(__file__)
    test_file_path = os.path.join(current_dir, "demo_data", "test_econvention.json")

    if not os.path.isfile(test_file_path):
        raise FileNotFoundError(f"Test file not found at: {test_file_path}")

    return test_file_path
