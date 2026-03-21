import pytest
from httpx import AsyncClient


async def create_resume(client: AsyncClient, name: str = "Test Resume") -> str:
    resp = await client.post("/api/resumes", json={"name": name})
    return resp.json()["data"]["id"]


@pytest.mark.asyncio
async def test_create_module(client: AsyncClient):
    resume_id = await create_resume(client)
    resp = await client.post(
        f"/api/resumes/{resume_id}/modules",
        json={
            "module_type": "education",
            "title": "Education",
            "content": {"degree": "BS"},
            "order_index": 1,
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["module_type"] == "education"
    assert body["data"]["title"] == "Education"
    assert body["data"]["resume_id"] == resume_id


@pytest.mark.asyncio
async def test_create_module_resume_not_found(client: AsyncClient):
    resp = await client.post(
        "/api/resumes/nonexistent/modules",
        json={"module_type": "edu", "title": "X"},
    )
    body = resp.json()
    assert body["success"] is False
    assert body["error"] == "Resume not found"


@pytest.mark.asyncio
async def test_list_modules(client: AsyncClient):
    resume_id = await create_resume(client)
    for i in range(3):
        await client.post(
            f"/api/resumes/{resume_id}/modules",
            json={"module_type": f"type{i}", "title": f"Module {i}", "order_index": i},
        )

    resp = await client.get(f"/api/resumes/{resume_id}/modules")
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) == 3


@pytest.mark.asyncio
async def test_list_modules_empty(client: AsyncClient):
    resume_id = await create_resume(client)
    resp = await client.get(f"/api/resumes/{resume_id}/modules")
    body = resp.json()
    assert body["data"] == []


@pytest.mark.asyncio
async def test_get_module_by_id(client: AsyncClient):
    resume_id = await create_resume(client)
    create_resp = await client.post(
        f"/api/resumes/{resume_id}/modules",
        json={"module_type": "experience", "title": "Exp"},
    )
    module_id = create_resp.json()["data"]["id"]

    resp = await client.get(f"/api/modules/{module_id}")
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["title"] == "Exp"


@pytest.mark.asyncio
async def test_get_module_not_found(client: AsyncClient):
    resp = await client.get("/api/modules/nonexistent-id")
    body = resp.json()
    assert body["success"] is False
    assert body["error"] == "Module not found"


@pytest.mark.asyncio
async def test_update_module(client: AsyncClient):
    resume_id = await create_resume(client)
    create_resp = await client.post(
        f"/api/resumes/{resume_id}/modules",
        json={"module_type": "edu", "title": "Old"},
    )
    module_id = create_resp.json()["data"]["id"]

    resp = await client.put(
        f"/api/modules/{module_id}",
        json={"module_type": "education", "title": "New Title"},
    )
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["title"] == "New Title"
    assert body["data"]["module_type"] == "education"


@pytest.mark.asyncio
async def test_update_module_not_found(client: AsyncClient):
    resp = await client.put("/api/modules/nonexistent-id", json={"title": "X"})
    body = resp.json()
    assert body["success"] is False
    assert body["error"] == "Module not found"


@pytest.mark.asyncio
async def test_delete_module(client: AsyncClient):
    resume_id = await create_resume(client)
    create_resp = await client.post(
        f"/api/resumes/{resume_id}/modules",
        json={"module_type": "edu", "title": "To Delete"},
    )
    module_id = create_resp.json()["data"]["id"]

    resp = await client.delete(f"/api/modules/{module_id}")
    assert resp.status_code == 200

    get_resp = await client.get(f"/api/modules/{module_id}")
    assert get_resp.json()["success"] is False


@pytest.mark.asyncio
async def test_delete_module_not_found(client: AsyncClient):
    resp = await client.delete("/api/modules/nonexistent-id")
    body = resp.json()
    assert body["success"] is False
    assert body["error"] == "Module not found"


@pytest.mark.asyncio
async def test_reorder_modules(client: AsyncClient):
    resume_id = await create_resume(client)
    ids = []
    for i in range(3):
        r = await client.post(
            f"/api/resumes/{resume_id}/modules",
            json={"module_type": f"type{i}", "title": f"M{i}", "order_index": i},
        )
        ids.append(r.json()["data"]["id"])

    resp = await client.patch(
        "/api/modules/reorder",
        json={
            "items": [
                {"id": ids[2], "order_index": 0},
                {"id": ids[0], "order_index": 1},
                {"id": ids[1], "order_index": 2},
            ]
        },
    )
    assert resp.status_code == 200

    list_resp = await client.get(f"/api/resumes/{resume_id}/modules")
    modules = list_resp.json()["data"]
    assert modules[0]["id"] == ids[2]
    assert modules[1]["id"] == ids[0]
    assert modules[2]["id"] == ids[1]


# ── Additional coverage tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_module_partial_title_only(client: AsyncClient):
    """Update only title, leaving other fields unchanged."""
    resume_id = await create_resume(client)
    create_resp = await client.post(
        f"/api/resumes/{resume_id}/modules",
        json={"module_type": "edu", "title": "Old Title", "content": {"foo": "bar"}},
    )
    module_id = create_resp.json()["data"]["id"]
    resp = await client.put(f"/api/modules/{module_id}", json={"title": "New Title Only"})
    body = resp.json()
    assert body["data"]["title"] == "New Title Only"
    assert body["data"]["module_type"] == "edu"


@pytest.mark.asyncio
async def test_update_module_partial_module_type_only(client: AsyncClient):
    resume_id = await create_resume(client)
    create_resp = await client.post(
        f"/api/resumes/{resume_id}/modules",
        json={"module_type": "edu", "title": "Title"},
    )
    module_id = create_resp.json()["data"]["id"]
    resp = await client.put(f"/api/modules/{module_id}", json={"module_type": "experience"})
    body = resp.json()
    assert body["data"]["module_type"] == "experience"
    assert body["data"]["title"] == "Title"
