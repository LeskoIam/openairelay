import logging

from fastapi import HTTPException
from openai import OpenAI
from openai.types.beta import Thread

from .config import OPENAI_ASSISTANT_ID

log = logging.getLogger("airelay")
openai_client = OpenAI()


def get_ai_response(prompt: str, system_role: str | None = None):
    """Return AI response based on prompt and optional system role.

    :param prompt:
    :param system_role:
    :return:
    """
    default_system_role = (
        "You are Riker (first officer aka number one), a comedian on board the USS Enterprise."
        "You call this ship 'Tuji Grm 6'."
        "In two sentences, report to me, captain Jean-Luc Picard, about the following."
        "Please do it in slovenian language."
    )
    # default_system_role = "You are a scientist with keen eye for details. As such your responses are full of detail."
    if system_role is not None:
        default_system_role = system_role
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": default_system_role},
            {"role": "user", "content": f"{prompt}"},
        ],
    )

    return completion.choices[0].message.content


def get_new_thread() -> Thread:
    """Get new Assistant thread.

    :return: Thread object
    """
    return openai_client.beta.threads.create()


def get_ai_assistant_response(prompt: str, thread_id: str | None = None) -> tuple[str, str]:
    """Return AI assistant response based on prompt and instructions.

    :param prompt:
    :param thread_id:
    :return:
    """
    if OPENAI_ASSISTANT_ID is None:
        raise HTTPException(status_code=503, detail="OPENAI_ASSISTANT_ID is not defined in environment")
    log.info("OPENAI_ASSISTANT_ID: %s", OPENAI_ASSISTANT_ID)
    assistant = openai_client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)
    if thread_id is None:
        log.info("No thread_id defined, creating new thread.")
        thread = get_new_thread()
        thread_id = thread.id
    log.info(thread_id)

    openai_client.beta.threads.messages.create(thread_id=thread_id, role="user", content=prompt)
    run = openai_client.beta.threads.runs.create_and_poll(thread_id=thread_id, assistant_id=assistant.id)

    if run.status == "completed":
        messages = openai_client.beta.threads.messages.list(thread_id=thread_id)
        response = []
        for message in messages.data:
            if message.role == "assistant":
                for content in message.content:
                    if content.type == "text":
                        response.append(content.text.value)
        return response[0], thread_id
    else:
        raise HTTPException(status_code=504, detail="Run did not complete")
