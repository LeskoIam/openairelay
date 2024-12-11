# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def get_env(var: str, default: Any = None) -> str | Any:
    """Return environment variable var value if it exists otherwise return default.

    :param var: environment variable to get
    :param default: default to return instead (defaults to None)
    :return: environment variable value
    """
    sr = os.getenv(var)
    return sr if isinstance(sr, str) else default


SYSTEM_ROLES = get_env("SYSTEM_ROLES", "./config/system_roles.yaml")

LOGGING_CONFIG = get_env("LOGGING_CONFIG", "./config/logging.yaml")
OPENAI_ASSISTANT_ID = get_env("OPENAI_ASSISTANT_ID")
