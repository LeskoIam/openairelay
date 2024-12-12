from datetime import datetime

from sqlmodel import Field, SQLModel


class SavedThread(SQLModel, table=True):
    thread_id: str = Field(primary_key=True, nullable=False, default="will be replaced")
    name: str = Field(index=True, unique=True)
    description: str | None = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.now)
