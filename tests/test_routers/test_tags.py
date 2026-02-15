import pytest

from app.models.tag import Tag

@pytest.mark.asyncio
async def test_list_tags(async_client, db_session):
    db_session.add_all([
        Tag(name="a"),
        Tag(name="b"),
    ])
    await db_session.flush()

    response = await async_client.get("/tags")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "a"

@pytest.mark.asyncio
async def test_get_tag_by_id(async_client, db_session):
    tag = Tag(name="nature")
    db_session.add(tag)
    await db_session.flush()

    response = await async_client.get(f"/tags/{tag.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "nature"

@pytest.mark.asyncio
async def test_get_tag_not_found(async_client):
    response = await async_client.get("/tags/999")

    assert response.status_code == 404