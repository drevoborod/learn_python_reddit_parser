from enum import StrEnum

from pydantic import BaseModel


class RedditEntityKinds(StrEnum):
    account = "t2"
    comment = "t1"
    link = "t3"
    subreddit = "t5"


class RedditEntity(BaseModel, use_enum_values=True):
    id: str
    created: float
    name: str
    author: str
    score: int
    kind: RedditEntityKinds
