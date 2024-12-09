# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
import logging.config

import yaml

from .config import LOGGING_CONFIG


def configure_logging():
    """Load the config file"""

    with open(LOGGING_CONFIG, "rt") as f:
        config = yaml.safe_load(f.read())
    # Configure the logging module with the config file
    logging.config.dictConfig(config)
