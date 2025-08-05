import datetime
import pendulum
from airflow import DAG
from airflow.models import DagRun, TaskInstance
from airflow.utils.state import DagRunState
from airflow.utils.types import DagRunType, DagRunTriggeredByType

TEST_DAG_ID = "fixture_dag_id"
DATA_INTERVAL_START = pendulum.datetime(2025, 1, 1, tz="UTC")
DATA_INTERVAL_END = DATA_INTERVAL_START + datetime.timedelta(days=1)


def assert_dag_dict_equal(structure: dict, dag: DAG) -> None:
    """
    Controls the internal structure of the DAG by comparing the task_dict
    to a provided dictionary
    :param structure: Dictionary containing the structure of the DAG
    :param dag: DAG object to compare
    :return: None
    """
    assert dag.task_dict.keys() == structure.keys()
    for task_id, downstream_list in structure.items():
        assert dag.has_task(task_id)
        task = dag.get_task(task_id)
        assert task.downstream_task_ids == set(downstream_list)


def create_dag_run(
    dag: DAG,
    data_interval_start: datetime,
    data_interval_end: datetime,
    logical_date: datetime,
    conf_payload: dict,
) -> DagRun:
    """
    Create a DAG run for the given DAG
    :param dag: The DAG object
    :param data_interval_start: datetime object representing the start of the data interval
    :param data_interval_end: datetime object representing the end of the data interval
    :param logical_date: datetime given by pendulum
    :param conf: Data to input into the DAG
    :return: The created DAG run
    """
    dag_run = dag.create_dagrun(
        state=DagRunState.RUNNING,
        logical_date=logical_date,
        run_id=f"manual__{logical_date.isoformat()}",
        data_interval=(data_interval_start, data_interval_end),
        start_date=data_interval_end,
        run_type=DagRunType.MANUAL,
        run_after=datetime.datetime.now(tz=pendulum.UTC),
        triggered_by=DagRunTriggeredByType.TEST,
        conf=conf_payload,
    )
    return dag_run


def create_task_instance(dag: DAG, dag_run: DagRun, task_id: str) -> TaskInstance:
    """
    Create a task instance for the given task_id
    :param dag: The DAG object
    :param dag_run: The DAG run object
    :param task_id: The task_id to create the task instance for
    :return: The created task instance
    """
    ti = dag_run.get_task_instance(task_id=task_id)
    ti.task = dag.get_task(task_id=task_id)
    ti.run(ignore_ti_state=True)
    return ti

def import_from_path(path: str) -> callable:
    """
    Import an Airflow task from a module
    :param path: dot separated path to the task,
    e.g. tasks.supann_2021.convert_ldap_structure_name.convert_ldap_structure_name_task
    :return: The task function
    """
    module_name, function_name = path.rsplit('.', 1)
    print(f"Importing task {function_name} from module {module_name}")
    module = __import__(module_name, fromlist=[function_name])
    return getattr(module, function_name)

# pylint: disable=unexpected-keyword-arg
with DAG(
    dag_id="dag_test_transform_only",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["test"],
) as dag_test:
    pass
