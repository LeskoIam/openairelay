# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
from datetime import datetime

from sqlmodel import Field, SQLModel


class SavedThread(SQLModel, table=True):
    thread_id: str = Field(primary_key=True, nullable=False, default="will be replaced")
    name: str = Field(index=True, unique=True)
    description: str | None = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.now)
