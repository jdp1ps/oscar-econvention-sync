from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from pydantic import ValidationError
from models.activity_model import Activity
from utils.config import POSTGRES_CONN_ID, BASCULE_ECONVENTION_ID
from utils.type_utils import ensure_list_of_dict


@task
def pg_extract_migratable_activities() -> list[dict]:
    """[TEMPORARY] Extract activities from Postgres table"""
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.centaureid as uid, a.label, 
               a.description, a.amount, 
               TO_CHAR(a.datestart,'YYYY-MM-DD') as datestart, 
               TO_CHAR(a.dateend,'YYYY-MM-DD') as dateend, 
               TO_CHAR(a.datesigned,'YYYY-MM-DD') as datesigned, 
               a.financialimpact, a.status, a.activitytype_id,
		    CONCAT_WS(' ',p.firstname,p.lastname) as person_fullname,
               urole.role_id as person_role,
		    o.fullname as organization_fullname, 
                orole.label as organization_role
		FROM activity as a, 
             activitydate as adate,
			 person as p, activityperson as ap,
			 organization as o, activityorganization as ao,
			 organizationrole as orole, user_role as urole
			 
        WHERE adate.activity_id = a.id 
          AND adate.type_id = %s AND adate.finished = 100
		  AND ap.person_id = p.id AND ap.activity_id = a.id
		  AND ao.organization_id = o.id AND ao.activity_id = a.id	
		  AND urole.id = ap.roleobj_id AND orole.id = ao.roleobj_id 
        """,
        (BASCULE_ECONVENTION_ID,),
    )
    column_names = [desc[0] for desc in cursor.description]
    migratable_activities = cursor.fetchall()

    raw_activities = [dict(zip(column_names, row)) for row in migratable_activities]
    for raw_activity in raw_activities:
        raw_activity["persons"] = {
            raw_activity["person_role"]: raw_activity["person_fullname"]
        }
        raw_activity["organizations"] = {
            raw_activity["organization_role"]: raw_activity["organization_fullname"]
        }
    activities = ensure_list_of_dict(raw_activities)
    activity_list: list[Activity] = []
    errors = []
    for i, activity in enumerate(activities):
        try:
            activity_list.append(Activity.model_validate(activity))
        except ValidationError as e:
            errors.append({"index": i, "errors": e.errors()})
    if len(errors) > 0:
        raise ValueError(f"Some activities failed validation: {errors}")

    results = [activity.model_dump() for activity in activity_list]
    return results
