from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from utils.config import POSTGRES_CONN_ID, BASCULE_ECONVENTION_ID


@task
def pg_get_migratable_activities():
    """[TEMPORARY] Extract activities from Postgres table"""
    migratable_activities = []
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT *
        FROM activity,
             activitydate
        WHERE activitydate.activity_id = activity.id
          AND activitydate.type_id = %s;
        """,
        (BASCULE_ECONVENTION_ID,),
    )
    for row in cursor.fetchall():
        migratable_activities.append(row)
    return migratable_activities
