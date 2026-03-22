import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.config import settings
from app.api.schemas import ApiResponse

router = APIRouter(prefix="/github", tags=["github"])


class GitHubOwner(BaseModel):
    login: str
    html_url: str


class GitHubRepo(BaseModel):
    name: str
    full_name: str
    owner: GitHubOwner
    description: Optional[str]
    html_url: str
    language: Optional[str]
    stargazers_count: int
    forks_count: int
    updated_at: str
    pushed_at: str


class GenerateModuleRequest(BaseModel):
    repo_name: str
    readme_content: str


class GeneratedModuleData(BaseModel):
    title: str
    content: dict
    fields: list


@router.get("/repos", response_model=ApiResponse[list[GitHubRepo]])
async def list_repos(
    username: str = Query(..., description="GitHub username"),
    exclude_forks: bool = Query(True),
    token: Optional[str] = Query(None),
):
    """List a user's GitHub repositories, excluding forks by default."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"https://api.github.com/users/{username}/repos",
            headers=headers,
            params={"sort": "updated", "per_page": 100, "type": "owner"},
        )

    if resp.status_code == 404:
        return ApiResponse.fail(f"GitHub user '{username}' not found")
    if resp.status_code == 403:
        return ApiResponse.fail(
            "GitHub API rate limit exceeded. Please provide a token."
        )
    if resp.status_code != 200:
        return ApiResponse.fail(f"GitHub API error: {resp.status_code}")

    raw = resp.json()
    repos = []
    for r in raw:
        if exclude_forks and r.get("fork"):
            continue
        repos.append(
            GitHubRepo(
                name=r["name"],
                full_name=r["full_name"],
                owner=GitHubOwner(
                    login=r.get("owner", {}).get("login", ""),
                    html_url=r.get("owner", {}).get("html_url", ""),
                ),
                description=r.get("description"),
                html_url=r["html_url"],
                language=r.get("language"),
                stargazers_count=r.get("stargazers_count", 0),
                forks_count=r.get("forks_count", 0),
                updated_at=r.get("updated_at", ""),
                pushed_at=r.get("pushed_at", ""),
            )
        )

    return ApiResponse.ok(repos)


@router.get("/readme", response_model=ApiResponse[dict])
async def get_readme(
    owner: str = Query(...),
    repo: str = Query(...),
    token: Optional[str] = Query(None),
):
    """Fetch the README content for a repository."""
    headers = {
        "Accept": "application/vnd.github.raw+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/readme",
            headers=headers,
        )

    if resp.status_code == 404:
        return ApiResponse.fail(f"README not found for {owner}/{repo}")
    if resp.status_code == 403:
        return ApiResponse.fail("GitHub API rate limit exceeded")
    if resp.status_code != 200:
        return ApiResponse.fail(f"GitHub API error: {resp.status_code}")

    content = resp.text
    # Truncate if too long (Claude has context limits)
    truncated = content[:15000] if len(content) > 15000 else content

    return ApiResponse.ok(
        {
            "content": truncated,
            "size": len(content),
            "truncated": len(content) > 15000,
        }
    )


@router.post("/generate-module", response_model=ApiResponse[GeneratedModuleData])
async def generate_module_from_readme(
    req: GenerateModuleRequest,
):
    """Use Claude to parse README and generate structured module data."""
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key:
        return ApiResponse.fail(
            "ANTHROPIC_API_KEY not configured. Set it in backend/.env"
        )

    prompt = f"""You are a resume builder assistant. Given a GitHub project's README, extract structured information for a resume "Project Experience" module.

Project: {req.repo_name}

README:
---
{req.readme_content}
---

Respond ONLY with valid JSON matching this schema:
{{
  "title": "Project Name (use the repo name or a cleaned version)",
  "content": {{"role": "Your role", "highlights": "1-2 sentence summary"}},
  "fields": [
    {{"key": "GitHub", "value": "URL to repo", "field_type": "url"}},
    {{"key": "Tech Stack", "value": "Comma-separated technologies mentioned", "field_type": "text"}},
    {{"key": "Description", "value": "1-2 sentence project description", "field_type": "text"}},
    {{"key": "Highlights", "value": "Key achievements or features (2-3 bullet points, newline separated)", "field_type": "list"}}
  ]
}}

Rules:
- Use English for all keys and values
- If README is empty or unreadable, return minimal data with the repo name as title
- Tech Stack: extract from package.json, requirements.txt, imports, or README mentions
- Description: summarize what the project does in 1-2 sentences
- Highlights: extract key features, achievements, or interesting technical details
- Stars and forks: if mentioned in README, include them
- field_type must be one of: text, url, date, list

Respond with ONLY the JSON, no markdown code blocks, no explanation."""

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.ANTHROPIC_BASE_URL}/v1/messages",
            headers={
                "Authorization": f"Bearer {api_key}",
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.CLAUDE_MODEL,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
        )

    if resp.status_code != 200:
        return ApiResponse.fail(f"Claude API error: {resp.status_code} {resp.text}")

    data = resp.json()
    try:
        # MiniMax format: content is a list of {type: "thinking"|"text", text: ...}
        content_list = data.get("content", [])
        text = ""
        for item in content_list:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "")
                break
        # Fallback: choices format (standard OpenAI-compatible)
        if not text:
            choices = data.get("choices", [])
            if isinstance(choices, list) and choices:
                text = choices[0].get("message", {}).get("content") or choices[0].get(
                    "text", ""
                )

        import json

        result = json.loads(text.strip())
        return ApiResponse.ok(GeneratedModuleData(**result))
    except (KeyError, json.JSONDecodeError, IndexError) as e:
        return ApiResponse.fail(f"Failed to parse Claude response: {e}\nRaw: {data}")
