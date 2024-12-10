# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
import logging
import os

import yaml

from .config import SYSTEM_ROLES
from .config import ASSISTANT_INSTRUCTIONS

log = logging.getLogger("airelay")


class LoadSystemRoleException(Exception):
    pass


class ci_dict(dict):  # noqa: N801
    def __init__(self, _dict: dict):
        """Case-insensitive dictionary

        :param _dict: input dict
        """
        super().__init__()
        for k, v in _dict.items():
            self.__setitem__(k, v)

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())


def load_system_role(role: str):
    """Load system role configuration file.

    :param role:
    :return:
    """
    log.debug("config file path: '%s'", SYSTEM_ROLES)
    log.debug("getting role: '%s'", role)
    if os.path.exists(SYSTEM_ROLES):
        with open(SYSTEM_ROLES, "rt") as f:
            system_roles = ci_dict(yaml.safe_load(f.read()))
        _system_roles = {}
        for _role, data in system_roles.items():
            if not _role.startswith("."):
                _system_roles[_role] = data
        system_roles = _system_roles
        log.info("Loaded system role %s: %s", role, system_roles[role])
        return system_roles[role]
    else:
        log.error(f"System rolls file '{SYSTEM_ROLES}' does not exists.")
        raise LoadSystemRoleException(f"System rolls file '{SYSTEM_ROLES}' does not exists.")


def load_assistant_instructions(role: str):
    print(ASSISTANT_INSTRUCTIONS)
    if os.path.exists(ASSISTANT_INSTRUCTIONS):
        with open(ASSISTANT_INSTRUCTIONS, "rt") as f:
            system_roles = ci_dict(yaml.safe_load(f.read()))
        _system_roles = {}
        for _role, data in system_roles.items():
            if not _role.startswith("."):
                _system_roles[_role] = data
        system_roles = _system_roles
        log.info("Assistant instructions %s: %s", role, system_roles[role])
        return system_roles[role]
    else:
        log.error(f"Assistant instructions file '{ASSISTANT_INSTRUCTIONS}' does not exists.")
        raise LoadSystemRoleException(f"Assistant instructions file '{ASSISTANT_INSTRUCTIONS}' does not exists.")


if __name__ == "__main__":
    print(load_system_role(role="spock"))
    load_assistant_instructions("default")
