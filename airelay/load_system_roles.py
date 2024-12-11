# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
import logging
import os

import yaml

from .config import SYSTEM_ROLES

log = logging.getLogger("airelay")


class LoadSystemRoleException(Exception):
    pass


class LoadAssistantInstructionsException(Exception):
    pass


def load_system_role(role: str):
    """Load system role configuration file.

    :param role:
    :return:
    """
    _all = role == "__ALL__"
    log.debug("config file path: '%s'", SYSTEM_ROLES)
    log.debug("getting role: '%s'", role)
    if os.path.exists(SYSTEM_ROLES):
        with open(SYSTEM_ROLES, "rt") as f:
            system_roles = yaml.safe_load(f.read())
        _system_roles = {}
        for _role, data in system_roles.items():
            if not _role.startswith(".") or _all:
                _system_roles[_role] = data
        system_roles = _system_roles

        if _all:
            return system_roles
        if role not in system_roles:
            log.info("System role %s not found in %s", role, system_roles)
            raise LoadSystemRoleException(f"System role {role} not found in {system_roles}")
        log.info("Loaded system role %s: %s", role, system_roles[role])
        return system_roles[role]
    else:
        log.error("System rolls file '%s' does not exists.", SYSTEM_ROLES)
        raise LoadSystemRoleException(f"System rolls file '{SYSTEM_ROLES}' does not exists.")


if __name__ == "__main__":
    print(load_system_role(role="spock"))
