"""Direct repository layer tests to improve coverage."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.database import Base, ResumeDB, ModuleDB, FieldDB
from app.repositories.resume_repo import ResumeRepository
from app.repositories.module_repo import ModuleRepository
from app.repositories.field_repo import FieldRepository
from app.api.schemas import (
    ResumeCreate,
    ResumeUpdate,
    ModuleCreate,
    ModuleUpdate,
    FieldCreate,
    FieldUpdate,
)


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as sess:
        yield sess
    await engine.dispose()


# ── Resume Repository ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_resume_repo_update_partial(db_session):
    """Cover resume update partial field path."""
    repo = ResumeRepository(db_session)
    r = ResumeDB(name="Original", description="Desc")
    db_session.add(r)
    await db_session.flush()

    updated = await repo.update(r, ResumeUpdate(description="New Desc"))
    assert updated.description == "New Desc"
    assert updated.name == "Original"


@pytest.mark.asyncio
async def test_resume_repo_list_order(db_session):
    """Cover list ordering by created_at desc."""
    repo = ResumeRepository(db_session)
    r1 = ResumeDB(name="First")
    r2 = ResumeDB(name="Second")
    db_session.add_all([r1, r2])
    await db_session.flush()

    items, total = await repo.list(page=1, limit=10)
    assert total == 2
    assert [i.name for i in items] == ["Second", "First"]


@pytest.mark.asyncio
async def test_resume_repo_delete(db_session):
    """Cover delete method."""
    repo = ResumeRepository(db_session)
    r = ResumeDB(name="ToDelete")
    db_session.add(r)
    await db_session.flush()
    resume_id = r.id

    await repo.delete(r)
    await db_session.commit()

    found = await db_session.get(ResumeDB, resume_id)
    assert found is None


# ── Module Repository ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_module_repo_create_and_list(db_session):
    """Cover list_by_resume with actual modules."""
    resume = ResumeDB(name="R")
    db_session.add(resume)
    await db_session.flush()

    repo = ModuleRepository(db_session)
    m1 = await repo.create(
        resume.id, ModuleCreate(module_type="edu", title="E", content={}, order_index=0)
    )
    m2 = await repo.create(
        resume.id, ModuleCreate(module_type="exp", title="X", content={}, order_index=1)
    )

    items = await repo.list_by_resume(resume.id)
    assert len(items) == 2
    assert items[0].title == "E"


@pytest.mark.asyncio
async def test_module_repo_update_all_fields(db_session):
    """Cover module update all fields path."""
    resume = ResumeDB(name="R")
    db_session.add(resume)
    await db_session.flush()

    repo = ModuleRepository(db_session)
    m = await repo.create(
        resume.id,
        ModuleCreate(module_type="edu", title="Old", content={}, order_index=0),
    )

    updated = await repo.update(
        m,
        ModuleUpdate(
            module_type="exp", title="New", content={"foo": "bar"}, order_index=5
        ),
    )
    assert updated.module_type == "exp"
    assert updated.title == "New"
    assert updated.content == {"foo": "bar"}


@pytest.mark.asyncio
async def test_module_repo_delete(db_session):
    """Cover module delete."""
    resume = ResumeDB(name="R")
    db_session.add(resume)
    await db_session.flush()

    repo = ModuleRepository(db_session)
    m = await repo.create(
        resume.id, ModuleCreate(module_type="edu", title="E", content={}, order_index=0)
    )
    module_id = m.id

    await repo.delete(m)
    await db_session.commit()

    found = await db_session.get(ModuleDB, module_id)
    assert found is None


@pytest.mark.asyncio
async def test_module_repo_reorder_partial(db_session):
    """Cover reorder with partial update (one module moves)."""
    resume = ResumeDB(name="R")
    db_session.add(resume)
    await db_session.flush()

    repo = ModuleRepository(db_session)
    m1 = await repo.create(
        resume.id, ModuleCreate(module_type="a", title="M1", content={}, order_index=0)
    )
    m2 = await repo.create(
        resume.id, ModuleCreate(module_type="b", title="M2", content={}, order_index=1)
    )
    m3 = await repo.create(
        resume.id, ModuleCreate(module_type="c", title="M3", content={}, order_index=2)
    )

    # Move m1 to end
    await repo.reorder(
        [
            {"id": m1.id, "order_index": 2},
            {"id": m2.id, "order_index": 0},
            {"id": m3.id, "order_index": 1},
        ]
    )
    await db_session.commit()

    items = await repo.list_by_resume(resume.id)
    assert [i.title for i in items] == ["M2", "M3", "M1"]


# ── Field Repository ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_field_repo_create_and_list(db_session):
    """Cover list_by_module."""
    resume = ResumeDB(name="R")
    db_session.add(resume)
    await db_session.flush()

    m_repo = ModuleRepository(db_session)
    m = await m_repo.create(
        resume.id, ModuleCreate(module_type="edu", title="E", content={}, order_index=0)
    )

    repo = FieldRepository(db_session)
    await repo.create(
        m.id, FieldCreate(key="school", value="MIT", field_type="text", order_index=0)
    )
    await repo.create(
        m.id, FieldCreate(key="year", value="2020", field_type="text", order_index=1)
    )

    items = await repo.list_by_module(m.id)
    assert len(items) == 2
    assert items[0].key == "school"


@pytest.mark.asyncio
async def test_field_repo_update_all_fields(db_session):
    """Cover field update all fields."""
    resume = ResumeDB(name="R")
    db_session.add(resume)
    await db_session.flush()

    m_repo = ModuleRepository(db_session)
    m = await m_repo.create(
        resume.id, ModuleCreate(module_type="edu", title="E", content={}, order_index=0)
    )
    m_obj = m

    repo = FieldRepository(db_session)
    f = await repo.create(
        m_obj.id, FieldCreate(key="old", value="old", field_type="text", order_index=0)
    )

    updated = await repo.update(
        f, FieldUpdate(key="new_key", value="new_val", field_type="url", order_index=5)
    )
    assert updated.key == "new_key"
    assert updated.value == "new_val"
    assert updated.field_type == "url"


@pytest.mark.asyncio
async def test_field_repo_delete(db_session):
    """Cover field delete."""
    resume = ResumeDB(name="R")
    db_session.add(resume)
    await db_session.flush()

    m_result = await db_session.execute(select(ModuleDB))
    m_obj = None  # noqa: F841

    m = ModuleDB(
        resume_id=resume.id, module_type="edu", title="E", content={}, order_index="0"
    )
    db_session.add(m)
    await db_session.flush()
    module_id = m.id

    repo = FieldRepository(db_session)
    f = await repo.create(
        module_id, FieldCreate(key="k", value="v", field_type="text", order_index=0)
    )
    field_id = f.id

    await repo.delete(f)
    await db_session.commit()

    found = await db_session.get(FieldDB, field_id)
    assert found is None


@pytest.mark.asyncio
async def test_field_repo_reorder_partial(db_session):
    """Cover reorder with non-contiguous indices."""
    resume = ResumeDB(name="R")
    db_session.add(resume)
    await db_session.flush()

    m = ModuleDB(
        resume_id=resume.id, module_type="edu", title="E", content={}, order_index="0"
    )
    db_session.add(m)
    await db_session.flush()
    module_id = m.id

    repo = FieldRepository(db_session)
    f1 = await repo.create(
        module_id, FieldCreate(key="k1", value="v1", field_type="text", order_index=0)
    )
    f2 = await repo.create(
        module_id, FieldCreate(key="k2", value="v2", field_type="text", order_index=1)
    )
    f3 = await repo.create(
        module_id, FieldCreate(key="k3", value="v3", field_type="text", order_index=2)
    )

    await repo.reorder(
        [
            {"id": f3.id, "order_index": 0},
            {"id": f1.id, "order_index": 1},
            {"id": f2.id, "order_index": 10},
        ]
    )
    await db_session.commit()

    items = await repo.list_by_module(module_id)
    assert [i.key for i in items] == ["k3", "k1", "k2"]
