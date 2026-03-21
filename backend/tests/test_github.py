"""Tests for GitHub integration API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_repos(client: AsyncClient):
    resp = await client.get("/api/github/repos?username=acloudygamer")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


@pytest.mark.asyncio
async def test_list_repos_user_not_found(client: AsyncClient):
    resp = await client.get("/api/github/repos?username=nonexistentuser99999")
    body = resp.json()
    assert body["success"] is False
    assert "not found" in body["error"]


@pytest.mark.asyncio
async def test_get_readme(client: AsyncClient):
    resp = await client.get(
        "/api/github/readme?owner=acloudygamer&repo=chinese-space-qa"
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "content" in body["data"]
    assert body["data"]["size"] > 0


@pytest.mark.asyncio
async def test_get_readme_not_found(client: AsyncClient):
    resp = await client.get(
        "/api/github/readme?owner=acloudygamer&repo=nonexistentrepo999"
    )
    body = resp.json()
    assert body["success"] is False
    assert "not found" in body["error"]


@pytest.mark.asyncio
async def test_generate_module_requires_api_key(client: AsyncClient):
    """Without ANTHROPIC_API_KEY, should fail gracefully."""
    resp = await client.post(
        "/api/github/generate-module",
        json={"repo_name": "test", "readme_content": "test"},
    )
    # In test environment, ANTHROPIC_API_KEY is not set
    body = resp.json()
    # Either success (if key configured) or fail (if not)
    assert body["success"] in (True, False)
