from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from utils.config import POSTGRES_CONN_ID


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
