from typing import Tuple

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from src import crud, schemas

tags_router = APIRouter(prefix="/tags")


@tags_router.get("/", response_model=Tuple[schemas.Tag, ...])
def get_tags():
    try:
        return tuple([
            schemas.Tag(id=tag.id, name=tag.name)
            for tag in crud.get_tags() if tag is not None
        ])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@tags_router.get("/{tag_id}", response_model=schemas.Tag | None)
def get_tag_by_id(tag_id: int):
    try:
        tag = crud.get_tag_by_id(tag_id)
        return schemas.Tag(id=tag.id, name=tag.name) if tag else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.args[0])

@tags_router.post("/", response_model=schemas.Tag)
def create_tag(new_tag: schemas.TagBase):
    try:
        tag = crud.create_tag(new_tag.name)
        if tag is None:
            raise HTTPException(status_code=500, detail="Failed to create tag.")
        return schemas.Tag(id=tag.id, name=tag.name)
    except IntegrityError as e:
        raise HTTPException(status_code=500, detail=f'Tag with name "{new_tag.name}" already exists.')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e.args[0]))

@tags_router.patch("/", response_model=schemas.Tag)
def patch_tag(patch_tag: schemas.TagPatch):
    try:
        updated_tag = crud.patch_tag(patch_tag)
        return schemas.Tag(id=updated_tag.id, name=updated_tag.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e.args[0]))

@tags_router.delete("/{tag_id}", response_model=None, status_code=204)
def delete_tag(tag_id: int):
    try:
        crud.delete_tag(tag_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e.args[0]))
