import logging.config

import yaml

from .config import LOGGING_CONFIG


def configure_logging():
    """Load the logging configuration file"""

    with open(LOGGING_CONFIG, "rt") as f:
        config = yaml.safe_load(f.read())
    # Configure the logging module with the config file
    logging.config.dictConfig(config)
