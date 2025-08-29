import os
import sys
import json
from pathlib import Path
import pytest
from _pytest.fixtures import SubRequest
import pendulum
from airflow.models import DagBag
from airflow import settings, DAG
from airflow.utils.db import resetdb
from tests.utils.dag import TEST_DAG_ID, import_from_path, DATA_INTERVAL_START

os.environ["APP_ENV"] = "TEST"

dags_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dags"))
if dags_path not in sys.path:
    sys.path.insert(0, dags_path)

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture(name="convention_raw_data")
def convention_raw_data_fixture():
    """load data from convention_raw_data.json"""
    with open(DATA_DIR / "convention_raw_data2.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(name="activity_expected_data")
def activity_expected_data_fixture():
    """load data from activity_expected_data.json"""
    with open(DATA_DIR / "activity_expected_data2.json", encoding="utf-8") as f:
        return json.load(f)


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


@pytest.fixture()
def econvention_to_oscar_dag(dagbag) -> DAG:
    """
    Create a DAG for testing
    :return: The DAG object
    """
    dag = dagbag.get_dag(dag_id="econvention_to_oscar")
    return dag


@pytest.fixture(name="dag_with_parameter")
def dag_fixture(request: SubRequest) -> DAG:
    """
    Create a DAG for testing the convert_ldap_structure_description_task
    :param request: The pytest request object
    It is a dictionary with the following keys
    - task_name: The name of the task to be created
    - param: The values of the parameters to be passed to the task
    :return: The DAG object
    """
    task_name = request.param["task_name"]
    param = request.param["param"]
    # pylint: disable=unexpected-keyword-arg
    with DAG(
        dag_id=TEST_DAG_ID,
        schedule="@daily",
        start_date=DATA_INTERVAL_START,
    ) as created_dag:
        task = import_from_path(task_name)
        task(param)
    return created_dag
