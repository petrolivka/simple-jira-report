from pydantic import BaseModel
from datetime import datetime


class Sprint(BaseModel):
    id: int
    name: str
    start: datetime
    end: datetime
    status: str


class Epic(BaseModel):
    key: str
    summary: str
    created: datetime
    status: str
    description: str | None
    color: str


class Issue(BaseModel):
    key: str
    summary: str
    status: str
    created: datetime
    parent: Epic | None
    sprints: list[str] | None
