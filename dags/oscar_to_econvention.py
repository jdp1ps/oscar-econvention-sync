from datetime import datetime
from airflow import DAG
from tasks.oscar_to_econvention.pg_get_activity_types import pg_extract_activity_types
from tasks.oscar_to_econvention.pg_extract_migratable_activities import (
    pg_extract_migratable_activities,
)
from tasks.oscar_to_econvention.redis_validate_activities import (
    redis_validate_activities,
)
from tasks.oscar_to_econvention.update_activity_types_csv import (
    update_activity_types_csv,
)
from tasks.oscar_to_econvention.transform_oscar_to_econvention import (
    transform_oscar_to_econvention,
)
from tasks.oscar_to_econvention.redis_confirm_migrated_conventions import (
    redis_confirm_migrated_conventions,
)
from tasks.oscar_to_econvention.create_import_json_to_econvention import (
    create_import_json_to_econvention
)

# pylint: disable=unexpected-keyword-arg
with DAG(
    dag_id="oscar_to_econvention",
    start_date=datetime(2025, 7, 30),
    schedule="*/10 * * * *",  # “At every 10th minute.”
    catchup=False,
    tags=["api", "json", "etl", "post"],
) as oscar_to_econvention:
    # Activity type's workflow
    activity_type_list = pg_extract_activity_types()
    activity_types_csv_path = update_activity_types_csv(activity_type_list)
    # Activities workflow
    raw_activities = pg_extract_migratable_activities()
    extracted_activities = redis_validate_activities(raw_activities)
    transformed_conventions = transform_oscar_to_econvention(extracted_activities)
    redis_confirm_migrated_conventions(transformed_conventions)
    create_import_json_to_econvention(transformed_conventions)
