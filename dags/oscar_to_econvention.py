from datetime import datetime
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from utils.config import POSTGRES_CONN_ID, BASCULE_ECONVENTION_ID

ACTIVITY_TYPE_LIST = None


@task
def pg_extract_activity_types():
    """[TEMPORARY] Extract activity types from Postgres table"""
    activity_types = []
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id,label FROM ACTIVITYTYPE;")
    for row in cursor.fetchall():
        activity_types.append(row)
    return activity_types


@task
def pg_extract_activities():
    """[TEMPORARY] Extract activities from Postgres table"""
    basculed_activities = []
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "select * from activity,activitydate "
        "where activitydate.activity_id = activity.id "
        f"and activitydate.type_id = {BASCULE_ECONVENTION_ID};"
    )
    for row in cursor.fetchall():
        basculed_activities.append(row)
    return basculed_activities


# pylint: disable=unexpected-keyword-arg
with DAG(
    dag_id="oscar_to_econvention",
    start_date=datetime(2025, 7, 30),
    schedule=None,
    catchup=False,
    tags=["api", "json", "etl", "post"],
) as oscar_to_econvention:
    activity_type_list = pg_extract_activity_types()
    activities = pg_extract_activities()
