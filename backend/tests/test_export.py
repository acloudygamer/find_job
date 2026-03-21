import pytest
import json
from httpx import AsyncClient


async def setup_full_resume(client: AsyncClient) -> str:
    r = await client.post(
        "/api/resumes", json={"name": "Full Resume", "description": "A full resume"}
    )
    resume_id = r.json()["data"]["id"]

    m1 = await client.post(
        f"/api/resumes/{resume_id}/modules",
        json={
            "module_type": "education",
            "title": "Education",
            "content": {"degree": "BS"},
            "order_index": 0,
        },
    )
    m1_id = m1.json()["data"]["id"]

    await client.post(
        f"/api/modules/{m1_id}/fields",
        json={
            "key": "school_name",
            "value": "MIT",
            "field_type": "text",
            "order_index": 0,
        },
    )
    await client.post(
        f"/api/modules/{m1_id}/fields",
        json={
            "key": "graduation_year",
            "value": "2020",
            "field_type": "text",
            "order_index": 1,
        },
    )

    m2 = await client.post(
        f"/api/resumes/{resume_id}/modules",
        json={
            "module_type": "experience",
            "title": "Work Experience",
            "order_index": 1,
        },
    )
    m2_id = m2.json()["data"]["id"]

    await client.post(
        f"/api/modules/{m2_id}/fields",
        json={
            "key": "company",
            "value": "TechCorp",
            "field_type": "text",
            "order_index": 0,
        },
    )

    return resume_id


@pytest.mark.asyncio
async def test_export_json(client: AsyncClient):
    resume_id = await setup_full_resume(client)
    resp = await client.get(f"/api/resumes/{resume_id}/export?format=json")
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["resume_id"] == resume_id
    assert body["data"]["format"] == "json"
    data = json.loads(body["data"]["content"])
    assert data["name"] == "Full Resume"
    assert data["description"] == "A full resume"
    assert "updated_at" in data
    assert len(data["modules"]) == 2
    assert data["modules"][0]["title"] == "Education"
    assert len(data["modules"][0]["fields"]) == 2
    # Timestamps included in exported data
    assert "created_at" in data["modules"][0]
    assert "updated_at" in data["modules"][0]["fields"][0]


@pytest.mark.asyncio
async def test_export_markdown(client: AsyncClient):
    resume_id = await setup_full_resume(client)
    resp = await client.get(f"/api/resumes/{resume_id}/export?format=markdown")
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["format"] == "markdown"
    content = body["data"]["content"]
    assert "# Full Resume" in content
    assert "## 🎓 Education" in content
    assert "**school_name**: MIT" in content
    assert "## 💼 Work Experience" in content


@pytest.mark.asyncio
async def test_export_default_format_is_json(client: AsyncClient):
    resume_id = await setup_full_resume(client)
    resp = await client.get(f"/api/resumes/{resume_id}/export")
    body = resp.json()
    assert body["data"]["format"] == "json"


@pytest.mark.asyncio
async def test_export_not_found(client: AsyncClient):
    resp = await client.get("/api/resumes/nonexistent/export?format=json")
    body = resp.json()
    assert body["success"] is False
    assert body["error"] == "Resume not found"


@pytest.mark.asyncio
async def test_export_empty_resume(client: AsyncClient):
    r = await client.post("/api/resumes", json={"name": "Empty"})
    resume_id = r.json()["data"]["id"]
    resp = await client.get(f"/api/resumes/{resume_id}/export?format=json")
    body = resp.json()
    data = json.loads(body["data"]["content"])
    assert data["name"] == "Empty"
    assert data["modules"] == []


@pytest.mark.asyncio
async def test_export_unicode(client: AsyncClient):
    r = await client.post("/api/resumes", json={"name": "中文简历 \u7b80\u5386"})
    resume_id = r.json()["data"]["id"]
    resp = await client.get(f"/api/resumes/{resume_id}/export?format=json")
    body = resp.json()
    data = json.loads(body["data"]["content"])
    assert data["name"] == "中文简历 \u7b80\u5386"


# ── Additional coverage tests ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_export_markdown_with_module_content(client: AsyncClient):
    """Markdown export should render module.content dict fields."""
    r = await client.post("/api/resumes", json={"name": "Resume With Content"})
    resume_id = r.json()["data"]["id"]
    m = await client.post(
        f"/api/resumes/{resume_id}/modules",
        json={
            "module_type": "project",
            "title": "My Project",
            "content": {"Tech Stack": "Python, FastAPI", "Role": "Full-stack"},
        },
    )
    module_id = m.json()["data"]["id"]
    await client.post(
        f"/api/modules/{module_id}/fields",
        json={"key": "Stars", "value": "120", "field_type": "text"},
    )
    resp = await client.get(f"/api/resumes/{resume_id}/export?format=markdown")
    body = resp.json()
    content = body["data"]["content"]
    assert "**Tech Stack**: Python, FastAPI" in content
    assert "**Role**: Full-stack" in content
    assert "**Stars**: 120" in content


@pytest.mark.asyncio
async def test_export_markdown_no_description(client: AsyncClient):
    """Resume without description should not render description line."""
    r = await client.post("/api/resumes", json={"name": "No Desc"})
    resume_id = r.json()["data"]["id"]
    resp = await client.get(f"/api/resumes/{resume_id}/export?format=markdown")
    content = resp.json()["data"]["content"]
    lines = content.split("\n")
    assert lines[0] == "# No Desc"
    assert not any("None" in l for l in lines if l.startswith("# "))


@pytest.mark.asyncio
async def test_export_markdown_field_types(client: AsyncClient):
    """URL, date, and list fields render differently."""
    r = await client.post("/api/resumes", json={"name": "Field Types"})
    resume_id = r.json()["data"]["id"]
    m = await client.post(
        f"/api/resumes/{resume_id}/modules",
        json={"module_type": "project", "title": "My Project"},
    )
    module_id = m.json()["data"]["id"]

    await client.post(
        f"/api/modules/{module_id}/fields",
        json={"key": "Website", "value": "https://example.com", "field_type": "url"},
    )
    await client.post(
        f"/api/modules/{module_id}/fields",
        json={"key": "Duration", "value": "2023-01 to 2023-06", "field_type": "date"},
    )
    await client.post(
        f"/api/modules/{module_id}/fields",
        json={"key": "Tech Stack", "value": "Python\nFastAPI\nReact", "field_type": "list"},
    )

    resp = await client.get(f"/api/resumes/{resume_id}/export?format=markdown")
    content = resp.json()["data"]["content"]
    # URL rendered as markdown link with icon
    assert "🔗 [https://example.com](https://example.com)" in content
    # Date rendered with calendar icon
    assert "📅 2023-01 to 2023-06" in content
    # List rendered as nested bullet points
    assert "  - Python" in content
    assert "  - FastAPI" in content
    assert "  - React" in content


@pytest.mark.asyncio
async def test_export_markdown_with_created_date(client: AsyncClient):
    """Created date appears in resume header."""
    r = await client.post("/api/resumes", json={"name": "With Date"})
    resume_id = r.json()["data"]["id"]
    resp = await client.get(f"/api/resumes/{resume_id}/export?format=markdown")
    content = resp.json()["data"]["content"]
    assert "> Created:" in content
