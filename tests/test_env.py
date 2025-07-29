import os

from airflow import DAG
from airflow.providers.standard.operators.empty import EmptyOperator

from project_dags import (
    create_dag_run,
    create_task_instance,
    DATA_INTERVAL_START,
    DATA_INTERVAL_END,
    TEST_DAG_ID,
)


def test_airflow_home_is_set():
    """
    Ensure that AIRFLOW_HOME environment variable is set and points to a valid directory

    """
    airflow_home = os.getenv("AIRFLOW_HOME")
    assert airflow_home is not None, "AIRFLOW_HOME environment variable is not set"
    assert os.path.isdir(
        airflow_home
    ), f"AIRFLOW_HOME directory does not exist: {airflow_home}"


def test_file_exists(test_data_path):
    """
    Check that the test data file exists.
    """
    assert os.path.isfile(test_data_path)


def test_dag_run(unique_logical_date):
    """
    Verify that a DAG can be instantiated and contains the expected task.
    """
    # pylint: disable=unexpected-keyword-arg
    with DAG(
        dag_id=TEST_DAG_ID,
        schedule="@daily",
        start_date=DATA_INTERVAL_START,
    ) as created_dag:
        EmptyOperator(task_id="example_task")

        dag_run = create_dag_run(
            created_dag, DATA_INTERVAL_START, DATA_INTERVAL_END, unique_logical_date
        )
        create_task_instance(created_dag, dag_run, "example_task")

        assert isinstance(created_dag, DAG)
        assert created_dag.dag_id == TEST_DAG_ID
        assert "example_task" in created_dag.task_ids
