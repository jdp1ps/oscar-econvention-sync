from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

from tasks.example_task import example_task

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
    dummy_input_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "1", "age": 30},
        {"id": "2", "age": 25},
    ]
    dummy_result = example_task(input_data=dummy_input_data)
    dummy_result2 = example_task(input_data=dummy_result)
    print_result = BashOperator(
        task_id="print_result",
        bash_command=f"echo {dummy_result2}"
    )
    dummy_result2 >> print_result
