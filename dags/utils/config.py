import os
from dotenv import load_dotenv
import logging

# Load .env.test from the project root (two levels up from this file)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
dotenv_path = os.path.join(ROOT_DIR, ".env.test")
load_dotenv(dotenv_path)

logger = logging.getLogger(__name__)

# Search for generic and environment-specific .env.test files
APP_ENV = os.getenv("APP_ENV", "DEV")
for suffix in ["", f".{APP_ENV.lower()}"]:
    env_file_name = os.path.join(ROOT_DIR, f".env.test{suffix}")
    if not os.path.exists(env_file_name):
        logger.warning("%s env file not found", env_file_name)
    else:
        load_dotenv(env_file_name, verbose=True)


def get_env_var(key: str) -> str:
    """
    Get an environment variable or raise an error if missing.
    """
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(f"Missing environment variable: {key}")
    return value


ECONVENTION_TO_OSCAR_OUTPUT_DIR = get_env_var("ECONVENTION_TO_OSCAR_OUTPUT_DIR")
OSCAR_HOME_PATH = get_env_var("OSCAR_HOME")
