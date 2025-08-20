from airflow.decorators import task


@task
def extract_from_econvention(**context) -> list[dict]:
    """
    Extract data from REST API POST sent by eConvention

    :param context: given automatically by Airflow

    :return:
        list of dictionaries
    """
    conf_json = context["dag_run"].conf
    items = conf_json.get("items")
    if items is None:
        raise ValueError("Missing 'items' key in dag_run.conf.")
    if not isinstance(items, list):
        raise ValueError("Expected 'items' to be a list of dictionaries.")
    if not all(isinstance(item, dict) for item in items):
        raise ValueError("All items in 'items' must be dictionaries.")

    return items
