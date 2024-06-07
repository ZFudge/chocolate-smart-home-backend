from typing import Tuple

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound

import chocolate_smart_home.schemas.utils as schema_utils
from chocolate_smart_home import crud, schemas


spaces_router = APIRouter(prefix="/spaces")


@spaces_router.get("/", response_model=Tuple[schemas.Space, ...])
def get_spaces_data():
    spaces_data = crud.get_spaces()
    return tuple(map(schema_utils.space_to_schema, spaces_data))


@spaces_router.get("/{space_id}", response_model=schemas.Space)
def get_space_data(space_id: int):
    try:
        space = crud.get_space_by_id(space_id)
        return schema_utils.space_to_schema(space)
    except NoResultFound:
        detail = f"No Space with an id of {space_id} found."
        raise HTTPException(status_code=404, detail=detail)


@spaces_router.post("/", response_model=schemas.Space)
def create_space(space_data: schemas.SpaceBase):
    try:
        space = crud.create_space(space_data)
        return schema_utils.space_to_schema(space)
    except IntegrityError as e:
        raise HTTPException(status_code=500, detail=e.orig.diag.message_detail)


@spaces_router.put("/{space_id}", response_model=schemas.Space)
def update_space(space_id: int, space: schemas.SpaceBase):
    try:
        updated_space = crud.update_space(space_id, space.name)
        return schemas.Space(id=updated_space.id, name=updated_space.name)
    except NoResultFound as e:
        raise HTTPException(status_code=500, detail=e.args[0])


@spaces_router.delete("/{space_id}", response_model=None, status_code=204)
def delete_space(space_id: int):
    try:
        crud.delete_space(space_id)
    except NoResultFound as e:
        raise HTTPException(status_code=500, detail=e.args[0])
