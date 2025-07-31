import os
import json
from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta


@task
def save_json_from_trigger(**context):
    """
    Note:
    os.getenv("AIRFLOW_HOME") often returns None inside Airflow tasks or DAG files
    because Airflow runs its scheduler, webserver, and workers in separate processes
    which may not inherit the environment variables from the user shell where you export them.
    Thus, even if you do 'export AIRFLOW_HOME=...', these variables might not be visible
    to Airflow's running processes unless explicitly set in the service environment (e.g., systemd, docker-compose).
    To avoid this issue, provide a default fallback path in os.getenv, or use a relative path based on the DAG file location.
    """
    airflow_home = os.getenv("AIRFLOW_HOME", "/home/user/airflow")
    conf = context["dag_run"].conf
    logical_date = str(context["logical_date"])
    data_dir = os.path.join(airflow_home, "data")

    filename = f"econvention_{logical_date}.json"
    target_path = os.path.join(data_dir, filename)

    with open(target_path, "w") as f:
        json.dump(conf, f)

    print(f"[INFO] JSON saved to {target_path}")


with DAG(
    dag_id="receive_external_json",
    start_date=datetime(2025, 7, 30),
    schedule=None,
    catchup=False,
    tags=["api", "json", "post"],
) as dag:
    save_json_from_trigger()
