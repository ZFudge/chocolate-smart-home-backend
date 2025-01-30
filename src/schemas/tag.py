from pydantic import BaseModel


class TagId(BaseModel):
    id: int


class TagBase(BaseModel):
    name: str


class Tag(TagId, TagBase):
    pass


class TagCreate(TagBase):
    pass


__all__ = ["Tag", "TagBase", "TagCreate"]
