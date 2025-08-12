from models.abstract_models import ConventionFactory
from models.econvention import Econvention


class EconventionFactory(ConventionFactory):
    """
    Oscar factory for building or converting convention models.
    """

    @classmethod
    def from_api_payload(cls, data: list[dict]) -> list[dict]:
        """
        Create a convention instance from a raw API payload sent by eConvention.
        This raw API payload is cleaned before being instantiated.
        :param data: raw API payload sent by eConvention.
        :return: list of econvention instances formatted into JSON string.
        """
        econvention_list: list[Econvention] = []
        for econvention in data:
            # Extract list of partners by getting their DisplayName if partner exists as a list.
            if "Partenaire" in econvention and isinstance(
                econvention["Partenaire"], list
            ):
                econvention["Partenaire"] = [
                    item.get("DisplayName")
                    for item in econvention["Partenaire"]
                    if isinstance(item, dict)
                ]
            # Rename Fields in a good format
            econvention["Createur"] = econvention.get("Créateur").get("DisplayName")
            econvention["Structure_Porteur"] = econvention.pop("Sticture Porteur")

            filtered_data = {
                k: v for k, v in econvention.items() if k in Econvention.model_fields
            }
            econvention_list.append(Econvention(**filtered_data))
        result_list = [econvention.model_dump() for econvention in econvention_list]
        return result_list

    @classmethod
    def convert_from(cls, data: list[dict]) -> str:
        """Convert data from another convention model."""
