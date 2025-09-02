import csv
from airflow.decorators import task
from utils.config import ACTIVITY_TYPE_CSV_FILE_PATH


@task
def update_activity_types_csv(activity_types: list):
    """Write activity types read from Postgres table"""

    with open(ACTIVITY_TYPE_CSV_FILE_PATH, "w", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["id", "label"])
        csvwriter.writerows(activity_types)
    return ACTIVITY_TYPE_CSV_FILE_PATH
