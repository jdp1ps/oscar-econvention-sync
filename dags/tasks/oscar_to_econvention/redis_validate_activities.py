from airflow.providers.redis.hooks.redis import RedisHook
from airflow.decorators import task
from pydantic import ValidationError
from models.activity_model import Activity
from utils.config import REDIS_CONN_ID
from utils.type_utils import ensure_list_of_dict
from utils.aliases import CONFIRMED_ACTIVITY_ALIAS


@task
def redis_validate_activities(raw_data: tuple) -> list[dict]:
    """
    Receive raw_data from PostgreSQL to validate activities.
    If some activities are already confirmed in Redis db, they will be skipped.
    """
    column_names = raw_data[0]
    migratable_activities = raw_data[1]

    redis_hook = RedisHook(REDIS_CONN_ID)
    redis_conn = redis_hook.get_conn()

    activities = ensure_list_of_dict(
        [dict(zip(column_names, activity)) for activity in migratable_activities]
    )
    activity_list: list[Activity] = []
    errors = []
    for i, activity in enumerate(activities):
        try:
            raw_activity = Activity.model_validate(activity)
            uid = raw_activity.uid
            # verify if this uid is in Redis db
            if redis_conn.sismember(CONFIRMED_ACTIVITY_ALIAS, uid):
                continue  # skip that activity

            activity_list.append(raw_activity)
        except ValidationError as e:
            errors.append({"index": i, "errors": e.errors()})
    if len(errors) > 0:
        raise ValueError(f"Some activities failed validation: {errors}")

    redis_conn.close()
    results = [activity.model_dump() for activity in activity_list]
    return results
