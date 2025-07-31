from airflow import DAG
from datetime import datetime, timedelta

with DAG(
    dag_id="check_api_availability",
    description="Check if an external API is available",
    schedule=timedelta(days=1),
    start_date=datetime(2025, 7, 1),
    catchup=False,
    tags=["sensor", "http"],
) as dag:
    """
    A dummy DAG that checks if the command line
    curl -X GET http://localhost:8080/api/v2/dags -H "Authorization: Bearer <JWT access_token>"
    works properly.
    """
    pass

