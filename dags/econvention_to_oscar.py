import shlex
from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from tasks.econvention_to_oscar.receive_from_econvention import receive_from_econvention
from tasks.econvention_to_oscar.transform_econvention_to_oscar import (
    transform_econvention_to_oscar,
)
from tasks.econvention_to_oscar.create_import_json_to_oscar import (
    create_import_json_to_oscar,
)
from utils.config import (
    OSCAR_CLI_WORKING_DIRECTORY,
    REMOTE_OSCAR_OUTPUT_DIR,
    SSH_KEY_PATH,
    SSH_HOST,
    SSH_USER,
)


# pylint: disable=unexpected-keyword-arg
with DAG(
    dag_id="econvention_to_oscar",
    start_date=datetime(2025, 7, 30),
    schedule=None,
    catchup=False,
    user_defined_macros={'shlex': shlex},
    tags=["api", "json", "etl", "post", "econvention_to_oscar"],
) as econvention_to_oscar:

    raw_data = receive_from_econvention()
    transformed_data = transform_econvention_to_oscar(raw_data)
    loaded_data_path = create_import_json_to_oscar(transformed_data)

    transfer_and_import = BashOperator(
        dag=econvention_to_oscar,
        task_id="transfer_and_import",
        bash_command=(
            "echo {{ shlex.quote(ti.xcom_pull(task_ids='transform_econvention_to_oscar')) }} "
            f"| ssh -i {SSH_KEY_PATH} {SSH_USER}@{SSH_HOST} "
            f"'cat > {REMOTE_OSCAR_OUTPUT_DIR}/"
            f"{{{{ ti.xcom_pull(task_ids='create_import_json_to_oscar')['filename'] }}}}' && "

            f"ssh -i {SSH_KEY_PATH} {SSH_USER}@{SSH_HOST} "
            f"'php {OSCAR_CLI_WORKING_DIRECTORY}/bin/oscar.php activity:import-json "
            f"-f {REMOTE_OSCAR_OUTPUT_DIR}/"
            f"{{{{ ti.xcom_pull(task_ids='create_import_json_to_oscar')['filename'] }}}}'"
        ),
    )
    # pylint: disable=pointless-statement
    (transformed_data >> loaded_data_path >> transfer_and_import)
