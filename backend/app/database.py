from typing import AsyncGenerator

from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.sqlite import JSON as SA_JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
import uuid
from datetime import datetime

from app.config import settings

Base = declarative_base()


class ResumeDB(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    modules = relationship(
        "ModuleDB", back_populates="resume", cascade="all, delete-orphan"
    )


class ModuleDB(Base):
    __tablename__ = "modules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(
        String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False
    )
    module_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(SA_JSON, nullable=True, default=dict)
    order_index = Column(String(10), nullable=False, default="0")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resume = relationship("ResumeDB", back_populates="modules")
    fields = relationship(
        "FieldDB", back_populates="module", cascade="all, delete-orphan"
    )


class FieldDB(Base):
    __tablename__ = "fields"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    module_id = Column(
        String(36), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False
    )
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    field_type = Column(String(20), nullable=False, default="text")
    order_index = Column(String(10), nullable=False, default="0")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    module = relationship("ModuleDB", back_populates="fields")


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
