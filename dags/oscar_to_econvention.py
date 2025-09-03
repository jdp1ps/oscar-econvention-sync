from datetime import datetime
from airflow import DAG
from tasks.oscar_to_econvention.pg_get_activity_types import pg_extract_activity_types
from tasks.oscar_to_econvention.pg_extract_migratable_activities import (
    pg_extract_migratable_activities,
)
from tasks.oscar_to_econvention.update_activity_types_csv import (
    update_activity_types_csv,
)
from tasks.oscar_to_econvention.transform_oscar_to_econvention import (
    transform_oscar_to_econvention,
)
from tasks.oscar_to_econvention.pg_confirm_migrated_conventions import (
    pg_confirm_migratable_conventions,
)

# pylint: disable=unexpected-keyword-arg
with DAG(
    dag_id="oscar_to_econvention",
    start_date=datetime(2025, 7, 30),
    schedule="*/10 * * * *",  # “At every 10th minute.”
    catchup=False,
    tags=["api", "json", "etl", "post"],
) as oscar_to_econvention:
    activity_type_list = pg_extract_activity_types()
    activity_types_csv_path = update_activity_types_csv(activity_type_list)
    extracted_activities = pg_extract_migratable_activities()
    transformed_conventions = transform_oscar_to_econvention(extracted_activities)
    pg_confirm_migratable_conventions(transformed_conventions)
