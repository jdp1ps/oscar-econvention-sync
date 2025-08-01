from configparser import ConfigParser
import os

parser = ConfigParser()

config_file_path = os.path.join(os.path.dirname(__file__), "etl.cfg")
parser.read(config_file_path)


def get_config(section: str, option: str) -> str:
    """
    Retrieve a configuration value from the etl.cfg file.
    Args:
        section (str): The section name in the configuration file.
        option (str): The option/key name within the section.

    Returns:
        str: The value corresponding to the section and option.

    Raises:
        EnvironmentError: If the section or option is missing in the configuration file.
    """
    if parser.has_section(section) and parser.has_option(section, option):
        return parser.get(section, option)
    raise EnvironmentError(f"Missing [{section}] {option} in etl.cfg")


AIRFLOW_HOME_PATH = get_config("paths", "AIRFLOW_HOME")
AIRFLOW_ETL_LOAD_PATH = get_config("paths", "AIRFLOW_ETL_LOAD")
OSCAR_HOME_PATH = get_config("paths", "OSCAR_HOME")
