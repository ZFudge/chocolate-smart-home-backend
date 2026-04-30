import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound

from src import crud, schemas

logger = logging.getLogger(__name__)

tags_router = APIRouter(prefix="/tags")


@tags_router.get("/", response_model=tuple[schemas.Tag, ...])
def get_tags():
    try:
        return tuple(
            [
                schemas.Tag(id=tag.id, name=tag.name)
                for tag in crud.get_tags()
                if tag is not None
            ]
        )
    except Exception as e:
        logger.error("Error getting tags: %s", e)
        raise HTTPException(status_code=500, detail="Failed to get tags.")


@tags_router.get("/{tag_id}", response_model=schemas.Tag | None)
def get_tag_by_id(tag_id: int):
    try:
        tag = crud.get_tag_by_id(tag_id)
        return schemas.Tag(id=tag.id, name=tag.name) if tag else None
    except Exception as e:
        logger.error("Error getting tag by id %s: %s", tag_id, e)
        raise HTTPException(
            status_code=500, detail="Failed to get tag by id %s." % tag_id
        )


@tags_router.post("/", response_model=schemas.Tag)
def create_tag(new_tag: schemas.TagBase):
    try:
        tag = crud.create_tag(new_tag.name)
        if tag is None:
            raise ValueError
        return schemas.Tag(id=tag.id, name=tag.name)
    except IntegrityError:
        raise HTTPException(
            status_code=500, detail='Tag with name "%s" already exists.' % new_tag.name
        )
    except Exception as e:
        logger.error("Error creating tag %s: %s", new_tag.name, e)
        raise HTTPException(
            status_code=500,
            detail='Failed to create tag with name of "%s".' % new_tag.name,
        )


@tags_router.patch("/", response_model=schemas.Tag)
def patch_tag(patch_tag: schemas.TagPatch):
    try:
        updated_tag = crud.patch_tag(patch_tag)
        return schemas.Tag(id=updated_tag.id, name=updated_tag.name)
    except NoResultFound as e:
        raise HTTPException(status_code=500, detail=str(e.args[0]))
    except Exception as e:
        logger.error("Error patching tag %s: %s", patch_tag.id, e)
        raise HTTPException(
            status_code=500, detail="Failed to patch tag of id %s." % patch_tag.id
        )


@tags_router.delete("/{tag_id}", response_model=None, status_code=204)
def delete_tag(tag_id: int):
    try:
        crud.delete_tag(tag_id)
    except NoResultFound as e:
        raise HTTPException(status_code=500, detail=str(e.args[0]))
    except Exception as e:
        logger.error("Error deleting tag %s: %s", tag_id, e)
        raise HTTPException(
            status_code=500, detail="Failed to delete tag of id %s." % tag_id
        )
