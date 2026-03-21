import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.api.schemas import ApiResponse, ExportResponse
from app.repositories.resume_repo import ResumeRepository
from app.repositories.module_repo import ModuleRepository
from app.repositories.field_repo import FieldRepository
from app.database import ModuleDB, FieldDB

router = APIRouter(tags=["export"])


@router.get("/resumes/{resume_id}/export", response_model=ApiResponse[ExportResponse])
async def export_resume(
    resume_id: str,
    format: str = Query("json", pattern="^(json|markdown)$"),
    db: AsyncSession = Depends(get_db),
):
    resume_repo = ResumeRepository(db)
    resume = await resume_repo.get_by_id(resume_id)
    if not resume:
        return ApiResponse.fail("Resume not found")

    module_repo = ModuleRepository(db)
    field_repo = FieldRepository(db)

    modules_result = await db.execute(
        select(ModuleDB)
        .where(ModuleDB.resume_id == resume_id)
        .order_by(ModuleDB.order_index)
    )
    modules = list(modules_result.scalars().all())

    export_data = {
        "id": resume.id,
        "name": resume.name,
        "description": resume.description,
        "created_at": resume.created_at.isoformat(),
        "updated_at": resume.updated_at.isoformat(),
        "modules": [],
    }

    for module in modules:
        fields_result = await db.execute(
            select(FieldDB)
            .where(FieldDB.module_id == module.id)
            .order_by(FieldDB.order_index)
        )
        fields = list(fields_result.scalars().all())

        module_data = {
            "module_type": module.module_type,
            "title": module.title,
            "content": module.content or {},
            "created_at": module.created_at.isoformat(),
            "updated_at": module.updated_at.isoformat(),
            "fields": [
                {
                    "key": f.key,
                    "value": f.value,
                    "field_type": f.field_type,
                    "created_at": f.created_at.isoformat(),
                    "updated_at": f.updated_at.isoformat(),
                }
                for f in fields
            ],
        }
        export_data["modules"].append(module_data)

    if format == "json":
        content = json.dumps(export_data, ensure_ascii=False, indent=2)
    else:
        content = _render_markdown(export_data)

    return ApiResponse.ok(
        ExportResponse(
            resume_id=resume.id,
            resume_name=resume.name,
            format=format,
            content=content,
        )
    )


def _render_markdown(data: dict) -> str:
    lines = []

    # ── Header ──────────────────────────────────────────────────────────────
    lines.append(f"# {data['name']}")
    lines.append("")
    if data.get("description"):
        lines.append(f"_{data['description']}_")
        lines.append("")
    if data.get("created_at"):
        from datetime import datetime

        try:
            dt = datetime.fromisoformat(data["created_at"])
            lines.append(f"> Created: {dt.strftime('%Y-%m-%d')}")
            lines.append("")
        except Exception:
            pass

    # ── Modules ─────────────────────────────────────────────────────────────
    for module in data.get("modules", []):
        module_type = module.get("module_type", "")
        type_icon = _MODULE_ICONS.get(module_type, "📄")
        lines.append(f"## {type_icon} {module['title']}")
        lines.append("")

        # content dict fields
        if module.get("content"):
            for k, v in module["content"].items():
                lines.append(f"- **{k}**: {v}")
            lines.append("")

        # regular fields
        if module.get("fields"):
            # Group by field_type
            url_fields = [f for f in module["fields"] if f.get("field_type") == "url"]
            list_fields = [f for f in module["fields"] if f.get("field_type") == "list"]
            date_fields = [f for f in module["fields"] if f.get("field_type") == "date"]
            text_fields = [
                f
                for f in module["fields"]
                if f.get("field_type") not in ("url", "list", "date")
            ]

            for field in text_fields:
                lines.append(f"- **{field['key']}**: {field['value']}")

            for field in date_fields:
                lines.append(f"- **{field['key']}**: 📅 {field['value']}")

            for field in url_fields:
                lines.append(
                    f"- **{field['key']}**: 🔗 [{field['value']}]({field['value']})"
                )

            for field in list_fields:
                items = field["value"].split("\n") if field["value"] else []
                lines.append(f"- **{field['key']}**:")
                for item in items:
                    if item.strip():
                        lines.append(f"  - {item.strip()}")

            lines.append("")

    return "\n".join(lines)


_MODULE_ICONS: dict[str, str] = {
    "education": "🎓",
    "experience": "💼",
    "project": "🚀",
    "skills": "🛠️",
    "about": "👤",
    "custom": "📄",
}
