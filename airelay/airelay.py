import logging
from contextlib import asynccontextmanager
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, SQLModel, create_engine, select

from .load_system_roles import LoadSystemRoleException, load_system_role
from .logging_config import configure_logging
from .models import SavedThread
from .openairelay_client import get_ai_assistant_response, get_ai_response, get_new_thread

# Get a logger object
configure_logging()
log = logging.getLogger("airelay")

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB on startup."""
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="airelay/static"), name="static")
templates = Jinja2Templates(directory="airelay/templates")

#                        #############
# ######################## DB config ##########################
#                        #############

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    """Create all DB."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Create session context"""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


#                           #######
# ########################### API #############################
#                           #######


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", context={"request": request})


@app.get("/api/v1/threads", response_model=list[SavedThread])
def list_saved_threads(session: SessionDep):
    """List all saved threads.

    :param session:
    :return:
    """
    saved_sessions = session.exec(select(SavedThread)).all()
    return saved_sessions


@app.get("/api/v1/threads/{name}", response_model=SavedThread)
def get_thread_by_name(session: SessionDep, name):
    """Return saved thread by its name.

    :param session:
    :param name:
    :return:
    """
    try:
        thread = session.exec(select(SavedThread).where(SavedThread.name == name)).one()
    except NoResultFound as exc:
        log.info("Thread %s not found", name)
        raise HTTPException(status_code=404, detail=f"Role {name} not found") from exc
    return thread


@app.post("/api/v1/threads/", response_model=SavedThread)
def create_thread(thread: SavedThread, session: SessionDep):
    """Create new thread.

    :param thread:
    :param session:
    :return:
    """
    db_thread = SavedThread.model_validate(thread)
    new_thread = get_new_thread()
    db_thread.thread_id = new_thread.id

    session.add(db_thread)
    session.commit()
    session.refresh(db_thread)
    log.info("Created new thread with id %s", new_thread.id)
    return db_thread


# Roles
@app.get("/api/v1/roles/")
def list_roles():
    """List all roles.

    :return:
    """
    system_roles = load_system_role("__ALL__")
    return {"msg": system_roles}


@app.get("/api/v1/roles/{role}")
def show_role(role: str):
    """Show role.

    :param role:
    :return:
    """
    try:
        system_role = load_system_role(role)
    except LoadSystemRoleException as exc:
        log.info("Role %s not found", role)
        raise HTTPException(status_code=404, detail=f"Role {role} not found") from exc
    return {"msg": system_role}


@app.post("/api/v1/roles/{role}/{prompt}")
def respond_as_role(role: str, prompt: str):
    """Get response from openAI chatbot as a role.

    :param role:
    :param prompt:
    :return:
    """
    system_role = load_system_role(role)["description"]
    log.info("system role: %s", system_role)
    response = get_ai_response(prompt=prompt, system_role=system_role)

    return {"msg": response, "system": {"role": role}}


# Assistant
@app.post("/api/v1/assistant/{prompt}/{thread_name}")
def respond_as_assistant(prompt: str, thread_name: str, session: SessionDep, create: bool = False):
    """Get response from openAI chatbot as assistant.

    :param prompt:
    :return:
    """
    log.info("Assistant prompt: %s", prompt)
    if create:
        log.info("New thread '%s' will be created", thread_name)
        response, thread_id = get_ai_assistant_response(prompt=prompt, thread_id=None)
    else:
        try:
            thread = session.exec(select(SavedThread).where(SavedThread.name == thread_name)).one()
            log.info("Thread '%s' found", thread_name)
        except NoResultFound as exc:
            log.info("Thread '%s' not found", thread_name)
            try:
                thread = session.exec(select(SavedThread).where(SavedThread.name == "default")).one()
                log.info("Thread 'default' found")
            except NoResultFound:
                log.warning(
                    "'default' thread not found. Set default thread id with environment variable "
                    "'VALID_THREAD_ID'. E.g.: 'thread_kxEvEGnowayaligatorA9Twg'"
                )
                raise HTTPException(
                    status_code=404, detail=f"'{thread_name}' and 'default' thread not found in database"
                ) from exc
        thread_id = thread.thread_id
        log.info("Existing thread %s will be used", thread)
        response, thread_id = get_ai_assistant_response(prompt=prompt, thread_id=thread_id)

    return {"msg": response, "system": {"thread_id": thread_id}}


# fastapi run airelay/airelay.py --host=0.0.0.0 --port=8088 --reload
