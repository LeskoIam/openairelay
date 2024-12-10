# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
import logging
import os

import yaml

from .config import ASSISTANT_INSTRUCTIONS, SYSTEM_ROLES

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
        log.info("Loaded system role %s: %s", role, system_roles[role])
        return system_roles[role]
    else:
        log.error(f"System rolls file '{SYSTEM_ROLES}' does not exists.")
        raise LoadSystemRoleException(f"System rolls file '{SYSTEM_ROLES}' does not exists.")


def load_assistant_instructions(instruction_name: str):
    """Load assistant instructions configuration file.

    :param instruction_name:
    :return:
    """
    _all = instruction_name == "__ALL__"
    if os.path.exists(ASSISTANT_INSTRUCTIONS):
        with open(ASSISTANT_INSTRUCTIONS, "rt") as f:
            assistant_instructions = yaml.safe_load(f.read())
        _assistant_instructions = {}
        for _instruction_name, _instruction_description in assistant_instructions.items():
            if not _instruction_name.startswith(".") or _all:
                _assistant_instructions[_instruction_name] = _instruction_description
        assistant_instructions = _assistant_instructions

        if _all:
            return assistant_instructions
        log.info("Assistant instructions %s: %s", instruction_name, assistant_instructions[instruction_name])
        return assistant_instructions[instruction_name]
    else:
        log.error(f"Assistant instructions file '{ASSISTANT_INSTRUCTIONS}' does not exists.")
        raise LoadAssistantInstructionsException(
            f"Assistant instructions file '{ASSISTANT_INSTRUCTIONS}' does not exists."
        )


if __name__ == "__main__":
    print(load_system_role(role="spock"))
    load_assistant_instructions("default")
