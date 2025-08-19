from airflow.decorators import task
from models.econvention import Econvention


@task
def extract_from_econvention(**context) -> list[dict]:
    """
    Extract data from REST API POST sent by eConvention
    then this raw API payload is cleaned before being instantiated.
    :param context: given automatically by Airflow which contains API payload
    :return: list of econvention instances formatted into JSON string.
    """
    conf_json = context["dag_run"].conf
    items = conf_json.get("items")
    if items is None:
        raise ValueError("Missing 'items' key in dag_run.conf.")
    if not isinstance(items, list):
        raise ValueError("Expected 'items' to be a list of dictionaries.")
    if not all(isinstance(item, dict) for item in items):
        raise ValueError("All items in 'items' must be dictionaries.")

    econvention_list: list[Econvention] = []
    for econvention in items:
        # Extract list of partners by getting their DisplayName if partner exists as a list.
        if "Partenaire" in econvention and isinstance(econvention["Partenaire"], list):
            econvention["Partenaire"] = [
                item.get("DisplayName")
                for item in econvention["Partenaire"]
                if isinstance(item, dict)
            ]
        # Rename Fields in a good format
        econvention["Createur"] = econvention.get("Créateur").get("DisplayName")
        econvention["Structure_Porteur"] = econvention.pop("Sticture Porteur")

        filtered_data = {
            k: v for k, v in econvention.items() if k in Econvention.model_fields.keys()
        }
        econvention_list.append(Econvention(**filtered_data))
    results = [econvention.model_dump() for econvention in econvention_list]
    return results
