from pydantic import BaseModel
from typing import List


class TagId(BaseModel):
    id: int


class TagIds(BaseModel):
    ids: List[int] | None = None


class TagBase(BaseModel):
    name: str


class Tag(TagId, TagBase):
    pass


class TagCreate(TagBase):
    pass


__all__ = ["Tag", "TagBase", "TagCreate", "TagIds"]
