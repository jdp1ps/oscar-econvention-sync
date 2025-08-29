from datetime import datetime
from airflow import DAG
from tasks.oscar_to_econvention.pg_get_activity_types import pg_extract_activity_types
from tasks.oscar_to_econvention.pg_get_migratable_activities import (
    pg_get_migratable_activities,
)

ACTIVITY_TYPE_LIST = None


# pylint: disable=unexpected-keyword-arg
with DAG(
    dag_id="oscar_to_econvention",
    start_date=datetime(2025, 7, 30),
    schedule=None,
    catchup=False,
    tags=["api", "json", "etl", "post"],
) as oscar_to_econvention:
    activity_type_list = pg_extract_activity_types()
    activities = pg_get_migratable_activities()
