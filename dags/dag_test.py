from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

with DAG(
        "test",
        default_args={
            "depends_on_past": False,
            "retries": 1,
            "retry_delay": timedelta(minutes=5),
        },
        description="A simple test DAG",
        schedule=timedelta(days=1),
        start_date=datetime(2025, 7, 1),
        catchup=False,
        tags=["example"],
) as dag:
    t1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )

    t2 = BashOperator(
        task_id="sleep",
        depends_on_past=False,
        bash_command="sleep 5",
        retries=3,
    )
    t1 >> t2
