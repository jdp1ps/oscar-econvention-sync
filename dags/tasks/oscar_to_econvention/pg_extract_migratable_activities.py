from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from models.enum_models import StatusEnum
from utils.config import POSTGRES_CONN_ID, BASCULE_ECONVENTION_ID


@task
def pg_extract_migratable_activities() -> tuple:
    """
    Extract activities from the Postgres table that meet the following conditions:
    - The milestone "bascule eConvention" is present.
    - The milestone (activitydate) is marked as finished.
    - The status of the activity is "Acceptée".

    The extracted activities are then validated using the Activity model to ensure they are valid.

    Finally, these validated activities are returned for further processing.
    """
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    pg_conn = pg_hook.get_conn()
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute(
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
            AND adate.type_id = %s AND adate.finished = 100
            AND a.status = %s
		    AND atype.id = a.activitytype_id
		    AND ap.person_id = p.id AND ap.activity_id = a.id
		    AND ao.organization_id = o.id AND ao.activity_id = a.id	
		    AND urole.id = ap.roleobj_id AND orole.id = ao.roleobj_id 
		GROUP BY 
		    a.centaureid, a.label, atype.label, a.description,
		    a.datestart, a.dateend, a.datesigned, 
		    a.amount, a.financialimpact, a.status, a.activitytype_id;
        """,
        (BASCULE_ECONVENTION_ID, StatusEnum.ACCEPTE),
    )
    column_names = [desc[0] for desc in pg_cursor.description]
    migratable_activities = pg_cursor.fetchall()
    pg_cursor.close()
    pg_conn.close()

    return column_names, migratable_activities
