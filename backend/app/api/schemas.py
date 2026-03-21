# === API CONTRACT ===
# This file is the single source of truth for all API data models.
# Frontend should only import from this file.
# Models: Resume*, Module*, Field*, ApiResponse
# Created at: 2026-03-21
# Agent 1 (Backend + TDD) COMPLETED
# === API CONTRACT COMPLETE ===

from datetime import datetime
from typing import Any, Generic, TypeVar, Optional, List

from pydantic import BaseModel, Field

T = TypeVar("T")


# ============================================================
# Resume Schemas
# ============================================================


class ResumeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ResumeResponse(ResumeBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# Module Schemas
# ============================================================


class ModuleBase(BaseModel):
    module_type: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[dict[str, Any]] = Field(default_factory=dict)
    order_index: int = 0


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(BaseModel):
    module_type: Optional[str] = Field(None, min_length=1, max_length=50)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[dict[str, Any]] = None
    order_index: Optional[int] = None


class ModuleResponse(ModuleBase):
    id: str
    resume_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReorderItem(BaseModel):
    id: str
    order_index: int


class ReorderModulesRequest(BaseModel):
    items: List[ReorderItem]


# ============================================================
# Field Schemas
# ============================================================


class FieldBase(BaseModel):
    key: str = Field(..., min_length=1, max_length=255)
    value: str = Field(...)
    field_type: str = Field(default="text", max_length=20)
    order_index: int = 0


class FieldCreate(FieldBase):
    pass


class FieldUpdate(BaseModel):
    key: Optional[str] = Field(None, min_length=1, max_length=255)
    value: Optional[str] = None
    field_type: Optional[str] = Field(None, max_length=20)
    order_index: Optional[int] = None


class FieldResponse(FieldBase):
    id: str
    module_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReorderFieldsRequest(BaseModel):
    items: List[ReorderItem]


# ============================================================
# Export Schemas
# ============================================================


class ExportResponse(BaseModel):
    resume_id: str
    resume_name: str
    format: str
    content: str


# ============================================================
# Pagination & Meta
# ============================================================


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int


class PaginatedData(BaseModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta


# ============================================================
# Unified API Response
# ============================================================


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, data: T) -> "ApiResponse[T]":
        return cls(success=True, data=data, error=None)

    @classmethod
    def fail(cls, error: str) -> "ApiResponse":
        return cls(success=False, data=None, error=error)
