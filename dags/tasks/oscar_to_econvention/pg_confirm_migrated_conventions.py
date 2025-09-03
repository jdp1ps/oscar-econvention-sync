import json
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from utils.config import POSTGRES_CONN_ID
from models.convention_model import Convention


@task
def pg_confirm_migratable_conventions(migrated_conventions: str) -> int:
    """
    Confirm migrated conventions that were extracted from Postgres activities
    by updating their attributes (e.g., description).

    These activities will not be extracted again.
    """
    convention_dict_list = json.loads(migrated_conventions)

    migrated_convention_list: list[Convention] = [
        Convention.model_validate(convention) for convention in convention_dict_list
    ]
    confirmed_uid_list = [
        convention.to_uid() for convention in migrated_convention_list
    ]
    if len(confirmed_uid_list) > 0:
        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn = hook.get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE ACTIVITYDATE AS ad
            SET comment = 'Activité extraite !'
            FROM ACTIVITY AS a
            WHERE ad.activity_id = a.id
                AND ad.finished = 100
                AND a.centaureid IN %s;
            """,
            (tuple(confirmed_uid_list),),
        )
        conn.commit()
        cursor.close()
        conn.close()
    return 0
