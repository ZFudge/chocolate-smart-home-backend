from typing import Tuple

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound

from chocolate_smart_home import crud, schemas


tags_router = APIRouter(prefix="/tags")


@tags_router.get("/", response_model=Tuple[schemas.Tag, ...])
def get_tags_data():
    tags_data = crud.get_tags()
    return tuple(map(schemas.to_schema, tags_data))


@tags_router.get("/{tag_id}", response_model=schemas.Tag)
def get_tag_data(tag_id: int):
    try:
        tag = crud.get_tag_by_id(tag_id)
        return schemas.to_schema(tag)
    except NoResultFound:
        detail = f"No Tag with an id of {tag_id} found."
        raise HTTPException(status_code=404, detail=detail)


@tags_router.post("/", response_model=schemas.Tag)
def create_tag(tag_data: schemas.TagBase):
    try:
        tag = crud.create_tag(tag_data)
        return schemas.to_schema(tag)
    except IntegrityError as e:
        raise HTTPException(status_code=500, detail=e.orig.diag.message_detail)


@tags_router.put("/{tag_id}", response_model=schemas.Tag)
def update_tag(tag_id: int, tag: schemas.TagBase):
    try:
        updated_tag = crud.update_tag(tag_id, tag.name)
        return schemas.Tag(id=updated_tag.id, name=updated_tag.name)
    except NoResultFound as e:
        raise HTTPException(status_code=500, detail=e.args[0])


@tags_router.delete("/{tag_id}", response_model=None, status_code=204)
def delete_tag(tag_id: int):
    try:
        crud.delete_tag(tag_id)
    except NoResultFound as e:
        raise HTTPException(status_code=500, detail=e.args[0])
