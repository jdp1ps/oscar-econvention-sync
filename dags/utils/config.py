from dotenv import load_dotenv
import os

# Load .env from the project root (two levels up from this file)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
dotenv_path = os.path.join(ROOT_DIR, ".env")
load_dotenv(dotenv_path)

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