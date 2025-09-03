from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from pydantic import ValidationError
from models.activity_model import Activity
from utils.config import POSTGRES_CONN_ID, BASCULE_ECONVENTION_ID
from utils.type_utils import ensure_list_of_dict


@task
def pg_extract_migratable_activities() -> list[dict]:
    """
    Extract activities from the Postgres table that meet the following conditions:
    - The milestone "bascule eConvention" is present.
    - The milestone (activitydate) is marked as finished.
    - The milestone's description is different from 'Activité extraite'.

    The extracted activities are then validated using the Activity model to ensure they are valid.

    Finally, these validated activities are returned for further processing.
    """
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.centaureid as uid, a.label, 
			atype.label as type,
            a.description, 
            jsonb_object_agg(urole.role_id, CONCAT_WS(' ', p.firstname, p.lastname)) AS persons,
    		jsonb_object_agg(orole.label, o.fullname) AS organizations,
			TO_CHAR(a.datestart,'YYYY-MM-DD') as datestart, 
            TO_CHAR(a.dateend,'YYYY-MM-DD') as dateend, 
            TO_CHAR(a.datesigned,'YYYY-MM-DD') as datesigned, 
            a.amount, a.financialimpact, a.status
		FROM activity as a, 
             activitydate as adate,
			 activitytype as atype,
			 person as p, activityperson as ap,
			 organization as o, activityorganization as ao,
			 organizationrole as orole, user_role as urole
        WHERE adate.activity_id = a.id 
          AND adate.type_id = %s AND adate.finished = 100 AND adate.comment != 'Activité extraite !'
		  AND atype.id = a.activitytype_id
		  AND ap.person_id = p.id AND ap.activity_id = a.id
		  AND ao.organization_id = o.id AND ao.activity_id = a.id	
		  AND urole.id = ap.roleobj_id AND orole.id = ao.roleobj_id 
		GROUP BY 
		    a.centaureid, a.label, atype.label, a.description,
		    a.datestart, a.dateend, a.datesigned, 
		    a.amount, a.financialimpact, a.status, a.activitytype_id;
        """,
        (BASCULE_ECONVENTION_ID,),
    )
    column_names = [desc[0] for desc in cursor.description]
    migratable_activities = cursor.fetchall()
    cursor.close()
    conn.close()
    activities = ensure_list_of_dict(
        [dict(zip(column_names, activity)) for activity in migratable_activities]
    )
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
