from pydantic import BaseModel


class SpaceId(BaseModel):
    id: int


class SpaceBase(BaseModel):
    name: str


class Space(SpaceId, SpaceBase):
    pass


class SpaceCreate(SpaceBase):
    pass

__all__ = ["Space", "SpaceBase", "SpaceCreate"]
