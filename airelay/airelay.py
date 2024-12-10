# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI

from .config import OPENAI_ASSISTANT_ID
from .load_system_roles import load_assistant_instructions, load_system_role
from .logging_config import configure_logging

# Get a logger object
configure_logging()
log = logging.getLogger("airelay")

load_dotenv()
app = FastAPI()
client = OpenAI()


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
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": default_system_role},
            {"role": "user", "content": f"{prompt}"},
        ],
    )

    return completion.choices[0].message.content


def get_ai_assistant_response(prompt: str, instructions: str | None = None):
    """Return AI assistant response based on prompt and instructions.

    :param prompt:
    :param instructions:
    :return:
    """
    assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)
    thread = client.beta.threads.create()

    client.beta.threads.messages.create(thread_id=thread.id, role="user", content=prompt)
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=instructions,
    )

    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response = []
        for message in messages.data:
            if message.role == "assistant":
                for content in message.content:
                    if content.type == "text":
                        response.append(content.text.value)
        return response[0]
    else:
        return "No assistant data returned"


@app.get("/api/v1/roles/predefined/")
def list_roles():
    """List all predefined roles.

    :return:
    """
    system_roles = load_system_role("__ALL__")
    return {"msg": system_roles}


@app.get("/api/v1/roles/predefined/{role}")
def show_role(role: str):
    """Show predefined role.

    :param role:
    :return:
    """
    system_role = load_system_role(role)
    return {"msg": system_role}


@app.post("/api/v1/roles/predefined/{role}/{prompt}")
def respond_as_role(role: str, prompt: str):
    """Get response from openAI chatbot as a predefined role.

    :param role:
    :param prompt:
    :return:
    """
    system_role = load_system_role(role)["description"]
    log.info("system role: %s", system_role)
    response = get_ai_response(prompt=prompt, system_role=system_role)

    return {"msg": response, "system": {"role": role}}


@app.get("/api/v1/assistant/predefined/")
def list_assistant_instructions():
    """List all defined assistant instructions.

    :return:
    """
    system_roles = load_assistant_instructions("__ALL__")
    return {"msg": system_roles}


@app.get("/api/v1/assistant/predefined/{instructions}")
def show_assistant_instructions(instructions: str):
    """Show single assistant instruction.

    :param instructions:
    :return:
    """
    assistant_instructions = load_assistant_instructions(instructions)
    return {"msg": assistant_instructions}


@app.post("/api/v1/assistant/predefined/{instructions}/{prompt}")
def respond_as_assistant(instructions: str, prompt: str):
    """Get response from openAI chatbot as a predefined assistant.

    :param instructions:
    :param prompt:
    :return:
    """
    instructions = load_assistant_instructions(instructions)["description"]
    log.info("Assistant instructions: %s", instructions)
    response = get_ai_assistant_response(prompt=prompt, instructions=instructions)

    return {"msg": response, "system": {"instructions": instructions}}


# fastapi run airelay/airelay.py --host=0.0.0.0 --port=8088 --reload
