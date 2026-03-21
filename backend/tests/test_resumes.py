import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_resume(client: AsyncClient):
    resp = await client.post(
        "/api/resumes",
        json={"name": "My Resume", "description": "A sample resume"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["name"] == "My Resume"
    assert data["description"] == "A sample resume"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_resume_minimal(client: AsyncClient):
    resp = await client.post("/api/resumes", json={"name": "Minimal"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["data"]["description"] is None


@pytest.mark.asyncio
async def test_create_resume_empty_name_fails(client: AsyncClient):
    resp = await client.post("/api/resumes", json={"name": ""})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_resume_missing_name_fails(client: AsyncClient):
    resp = await client.post("/api/resumes", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_resumes_empty(client: AsyncClient):
    resp = await client.get("/api/resumes")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["data"] == []
    assert body["data"]["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_list_resumes_pagination(client: AsyncClient):
    for i in range(25):
        await client.post("/api/resumes", json={"name": f"Resume {i}"})

    resp = await client.get("/api/resumes?page=1&limit=10")
    body = resp.json()
    assert body["data"]["meta"]["total"] == 25
    assert body["data"]["meta"]["page"] == 1
    assert body["data"]["meta"]["limit"] == 10
    assert body["data"]["meta"]["total_pages"] == 3
    assert len(body["data"]["data"]) == 10

    resp = await client.get("/api/resumes?page=2&limit=10")
    body = resp.json()
    assert len(body["data"]["data"]) == 10

    resp = await client.get("/api/resumes?page=3&limit=10")
    body = resp.json()
    assert len(body["data"]["data"]) == 5


@pytest.mark.asyncio
async def test_get_resume_by_id(client: AsyncClient):
    create_resp = await client.post("/api/resumes", json={"name": "Find Me"})
    resume_id = create_resp.json()["data"]["id"]

    resp = await client.get(f"/api/resumes/{resume_id}")
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["name"] == "Find Me"
    assert body["data"]["id"] == resume_id


@pytest.mark.asyncio
async def test_get_resume_not_found(client: AsyncClient):
    resp = await client.get("/api/resumes/nonexistent-id")
    body = resp.json()
    assert body["success"] is False
    assert body["error"] == "Resume not found"


@pytest.mark.asyncio
async def test_update_resume(client: AsyncClient):
    create_resp = await client.post("/api/resumes", json={"name": "Old Name"})
    resume_id = create_resp.json()["data"]["id"]

    resp = await client.put(
        f"/api/resumes/{resume_id}",
        json={"name": "New Name", "description": "Updated"},
    )
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["name"] == "New Name"
    assert body["data"]["description"] == "Updated"


@pytest.mark.asyncio
async def test_update_resume_partial(client: AsyncClient):
    create_resp = await client.post(
        "/api/resumes", json={"name": "Original", "description": "Desc"}
    )
    resume_id = create_resp.json()["data"]["id"]

    resp = await client.put(f"/api/resumes/{resume_id}", json={"name": "Only Name"})
    body = resp.json()
    assert body["data"]["name"] == "Only Name"
    assert body["data"]["description"] == "Desc"


@pytest.mark.asyncio
async def test_update_resume_not_found(client: AsyncClient):
    resp = await client.put("/api/resumes/nonexistent-id", json={"name": "X"})
    body = resp.json()
    assert body["success"] is False
    assert body["error"] == "Resume not found"


@pytest.mark.asyncio
async def test_delete_resume(client: AsyncClient):
    create_resp = await client.post("/api/resumes", json={"name": "To Delete"})
    resume_id = create_resp.json()["data"]["id"]

    resp = await client.delete(f"/api/resumes/{resume_id}")
    assert resp.status_code == 200

    get_resp = await client.get(f"/api/resumes/{resume_id}")
    assert get_resp.json()["success"] is False


@pytest.mark.asyncio
async def test_delete_resume_not_found(client: AsyncClient):
    resp = await client.delete("/api/resumes/nonexistent-id")
    body = resp.json()
    assert body["success"] is False
    assert body["error"] == "Resume not found"


@pytest.mark.asyncio
async def test_resume_unicode_name(client: AsyncClient):
    resp = await client.post("/api/resumes", json={"name": "简历设计器 \u4e2d\u6587"})
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "简历设计器 \u4e2d\u6587"


# ── Additional coverage tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_pagination_limit_max(client: AsyncClient):
    for i in range(5):
        await client.post("/api/resumes", json={"name": f"R{i}"})
    resp = await client.get("/api/resumes?limit=100")
    body = resp.json()
    assert len(body["data"]["data"]) == 5
    assert body["data"]["meta"]["total"] == 5


@pytest.mark.asyncio
async def test_list_pagination_page_beyond_total(client: AsyncClient):
    for i in range(3):
        await client.post("/api/resumes", json={"name": f"R{i}"})
    resp = await client.get("/api/resumes?page=100")
    body = resp.json()
    assert body["data"]["data"] == []


@pytest.mark.asyncio
async def test_delete_resume_cascade_modules(client: AsyncClient):
    """Deleting a resume should cascade-delete its modules."""
    r = await client.post("/api/resumes", json={"name": "Cascade Test"})
    resume_id = r.json()["data"]["id"]
    m = await client.post(
        f"/api/resumes/{resume_id}/modules",
        json={"module_type": "edu", "title": "Edu"},
    )
    module_id = m.json()["data"]["id"]
    await client.delete(f"/api/resumes/{resume_id}")
    get_m = await client.get(f"/api/modules/{module_id}")
    assert get_m.json()["success"] is False
