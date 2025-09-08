import json
from airflow.providers.redis.hooks.redis import RedisHook
from airflow.decorators import task
from models.convention_model import Convention
from utils.config import REDIS_CONN_ID
from utils.aliases import CONFIRMED_ACTIVITY_ALIAS


@task
def redis_confirm_migrated_conventions(migrated_conventions: str) -> int:
    """
    Confirm migrated conventions that were extracted from Postgres activities
    by storing their UID in Redis.

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
        redis_hook = RedisHook(redis_conn_id=REDIS_CONN_ID)
        redis_conn = redis_hook.get_conn()

        for uid in confirmed_uid_list:
            redis_conn.sadd(CONFIRMED_ACTIVITY_ALIAS, uid)

    return len(confirmed_uid_list)
