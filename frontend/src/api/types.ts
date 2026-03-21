// Auto-generated from backend/app/api/schemas.py
// API Contract COMPLETE marker: 2026-03-21

// ============================================================
// Resume Types
// ============================================================

export interface ResumeBase {
  name: string;
  description: string | null;
}

export interface ResumeCreate extends ResumeBase {
  // All fields inherited from ResumeBase
}

export interface ResumeUpdate {
  name?: string | null;
  description?: string | null;
}

export interface ResumeResponse extends ResumeBase {
  id: string;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

// ============================================================
// Module Types
// ============================================================

export interface ModuleBase {
  module_type: string;
  title: string;
  content: Record<string, unknown>;
  order_index: number;
}

export interface ModuleCreate extends ModuleBase {
  // All fields inherited from ModuleBase
}

export interface ModuleUpdate {
  module_type?: string | null;
  title?: string | null;
  content?: Record<string, unknown> | null;
  order_index?: number | null;
}

export interface ModuleResponse extends ModuleBase {
  id: string;
  resume_id: string;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

// ============================================================
// Field Types
// ============================================================

export interface FieldBase {
  key: string;
  value: string;
  field_type: string;
  order_index: number;
}

export interface FieldCreate extends FieldBase {
  // All fields inherited from FieldBase
}

export interface FieldUpdate {
  key?: string | null;
  value?: string | null;
  field_type?: string | null;
  order_index?: number | null;
}

export interface FieldResponse extends FieldBase {
  id: string;
  module_id: string;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

// ============================================================
// Export Types
// ============================================================

export interface ExportResponse {
  resume_id: string;
  resume_name: string;
  format: string;
  content: string;
}

// ============================================================
// Pagination & Meta
// ============================================================

export interface PaginationMeta {
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface PaginatedData<T> {
  data: T[];
  meta: PaginationMeta;
}

// ============================================================
// Unified API Response
// ============================================================

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  error: string | null;
}

// ============================================================
// Reorder Types
// ============================================================

export interface ReorderItem {
  id: string;
  order_index: number;
}

export interface ReorderModulesRequest {
  items: ReorderItem[];
}

export interface ReorderFieldsRequest {
  items: ReorderItem[];
}

// ============================================================
// Export Format
// ============================================================

export type ExportFormat = 'json' | 'markdown';

// ============================================================
// GitHub Types
// ============================================================

export interface GitHubRepo {
  name: string;
  full_name: string;
  description: string | null;
  html_url: string;
  language: string | null;
  stargazers_count: number;
  forks_count: number;
  updated_at: string;
  pushed_at: string;
}

export interface ReadmeContent {
  content: string;
  size: number;
  truncated: boolean;
}

export interface GeneratedModuleData {
  title: string;
  content: Record<string, unknown>;
  fields: Array<{
    key: string;
    value: string;
    field_type: string;
  }>;
}
