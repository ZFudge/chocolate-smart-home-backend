from src import crud, schemas


def test_crud_get_tags_returns_tags(populated_test_db):
    tags = crud.get_tags()
    assert len(tags) == 3
    assert tags[0].id == 1
    assert tags[0].name == "Main Tag"
    assert tags[1].id == 2
    assert tags[1].name == "Other Tag"
    assert tags[2].id == 3
    assert tags[2].name == "Third Tag"


def test_crud_get_tag_by_id_returns_tag(populated_test_db):
    assert crud.get_tag_by_id(1).name == "Main Tag"


def test_crud_get_tags_by_ids(populated_test_db):
    tags = crud.get_tags_by_ids([1, 2])
    assert len(tags) == 2
    assert tags[0].name == "Main Tag"
    assert tags[1].name == "Other Tag"


def test_crud_get_tag_by_id_returns_none(empty_test_db):
    assert crud.get_tag_by_id(123) is None


def test_crud_get_tag_by_name_returns_tag(populated_test_db):
    assert crud.get_tag_by_name("Main Tag").name == "Main Tag"


def test_crud_get_tag_by_name_returns_none(empty_test_db):
    assert crud.get_tag_by_name("Non-existent Tag Name") is None


def test_crud_create_tag(empty_test_db):
    tag = crud.create_tag("New Tag")
    assert tag.name == "New Tag"
    assert crud.get_tag_by_name("New Tag").name == "New Tag"


def test_crud_delete_tag(populated_test_db):
    crud.delete_tag(1)
    assert crud.get_tag_by_id(1) is None


def test_crud_patch_tag(populated_test_db):
    tag = crud.patch_tag(schemas.TagPatch(id=1, name="Updated Tag"))
    assert tag.name == "Updated Tag"
    assert crud.get_tag_by_id(1).name == "Updated Tag"
