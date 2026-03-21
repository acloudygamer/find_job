import pytest
from httpx import AsyncClient


async def create_module(client: AsyncClient) -> tuple[str, str]:
    r = await client.post("/api/resumes", json={"name": "R"})
    resume_id = r.json()["data"]["id"]
    m = await client.post(
        f"/api/resumes/{resume_id}/modules",
        json={"module_type": "education", "title": "Edu"},
    )
    return resume_id, m.json()["data"]["id"]


@pytest.mark.asyncio
async def test_create_field(client: AsyncClient):
    _, module_id = await create_module(client)
    resp = await client.post(
        f"/api/modules/{module_id}/fields",
        json={
            "key": "school_name",
            "value": "MIT",
            "field_type": "text",
            "order_index": 0,
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["key"] == "school_name"
    assert body["data"]["value"] == "MIT"
    assert body["data"]["module_id"] == module_id


@pytest.mark.asyncio
async def test_create_field_module_not_found(client: AsyncClient):
    resp = await client.post(
        "/api/modules/nonexistent/fields",
        json={"key": "k", "value": "v"},
    )
    body = resp.json()
    assert body["success"] is False
    assert body["error"] == "Module not found"


@pytest.mark.asyncio
async def test_list_fields(client: AsyncClient):
    _, module_id = await create_module(client)
    for i in range(3):
        await client.post(
            f"/api/modules/{module_id}/fields",
            json={"key": f"key{i}", "value": f"val{i}", "order_index": i},
        )

    resp = await client.get(f"/api/modules/{module_id}/fields")
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) == 3


@pytest.mark.asyncio
async def test_list_fields_empty(client: AsyncClient):
    _, module_id = await create_module(client)
    resp = await client.get(f"/api/modules/{module_id}/fields")
    body = resp.json()
    assert body["data"] == []


@pytest.mark.asyncio
async def test_update_field(client: AsyncClient):
    _, module_id = await create_module(client)
    create_resp = await client.post(
        f"/api/modules/{module_id}/fields",
        json={"key": "old_key", "value": "old_val", "field_type": "text"},
    )
    field_id = create_resp.json()["data"]["id"]

    resp = await client.put(
        f"/api/fields/{field_id}",
        json={"key": "new_key", "value": "new_val", "field_type": "url"},
    )
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["key"] == "new_key"
    assert body["data"]["value"] == "new_val"
    assert body["data"]["field_type"] == "url"


@pytest.mark.asyncio
async def test_update_field_not_found(client: AsyncClient):
    resp = await client.put("/api/fields/nonexistent-id", json={"value": "x"})
    body = resp.json()
    assert body["success"] is False
    assert body["error"] == "Field not found"


@pytest.mark.asyncio
async def test_delete_field(client: AsyncClient):
    _, module_id = await create_module(client)
    create_resp = await client.post(
        f"/api/modules/{module_id}/fields",
        json={"key": "k", "value": "v"},
    )
    field_id = create_resp.json()["data"]["id"]

    resp = await client.delete(f"/api/fields/{field_id}")
    assert resp.status_code == 200

    get_resp = await client.get(f"/api/modules/{module_id}/fields")
    assert get_resp.json()["data"] == []


@pytest.mark.asyncio
async def test_delete_field_not_found(client: AsyncClient):
    resp = await client.delete("/api/fields/nonexistent-id")
    body = resp.json()
    assert body["success"] is False
    assert body["error"] == "Field not found"


@pytest.mark.asyncio
async def test_reorder_fields(client: AsyncClient):
    _, module_id = await create_module(client)
    ids = []
    for i in range(3):
        r = await client.post(
            f"/api/modules/{module_id}/fields",
            json={"key": f"k{i}", "value": f"v{i}", "order_index": i},
        )
        ids.append(r.json()["data"]["id"])

    resp = await client.patch(
        "/api/fields/reorder",
        json={
            "items": [
                {"id": ids[2], "order_index": 0},
                {"id": ids[0], "order_index": 1},
                {"id": ids[1], "order_index": 2},
            ]
        },
    )
    assert resp.status_code == 200

    list_resp = await client.get(f"/api/modules/{module_id}/fields")
    fields = list_resp.json()["data"]
    assert fields[0]["id"] == ids[2]
    assert fields[1]["id"] == ids[0]
    assert fields[2]["id"] == ids[1]


@pytest.mark.asyncio
async def test_field_special_characters(client: AsyncClient):
    _, module_id = await create_module(client)
    resp = await client.post(
        f"/api/modules/{module_id}/fields",
        json={"key": "emoji_key", "value": "test<>\"'&value", "field_type": "text"},
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["value"] == "test<>\"'&value"


# ── Additional coverage tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_field_partial_value_only(client: AsyncClient):
    """Update only value, leaving key and type unchanged."""
    _, module_id = await create_module(client)
    create_resp = await client.post(
        f"/api/modules/{module_id}/fields",
        json={"key": "company", "value": "Old Co", "field_type": "text"},
    )
    field_id = create_resp.json()["data"]["id"]
    resp = await client.put(f"/api/fields/{field_id}", json={"value": "New Co"})
    body = resp.json()
    assert body["data"]["value"] == "New Co"
    assert body["data"]["key"] == "company"
    assert body["data"]["field_type"] == "text"


@pytest.mark.asyncio
async def test_update_field_partial_key_only(client: AsyncClient):
    _, module_id = await create_module(client)
    create_resp = await client.post(
        f"/api/modules/{module_id}/fields",
        json={"key": "old_key", "value": "val", "field_type": "text"},
    )
    field_id = create_resp.json()["data"]["id"]
    resp = await client.put(f"/api/fields/{field_id}", json={"key": "new_key"})
    body = resp.json()
    assert body["data"]["key"] == "new_key"
    assert body["data"]["value"] == "val"
