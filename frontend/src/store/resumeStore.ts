import { create } from 'zustand';
import {
  resumeApi,
  moduleApi,
  fieldApi,
  exportApi,
  type ResumeResponse,
  type ModuleResponse,
  type FieldResponse,
  type ResumeCreate,
  type ResumeUpdate,
  type ModuleCreate,
  type ModuleUpdate,
  type FieldCreate,
  type FieldUpdate,
  type ExportFormat,
} from '../api';

interface ResumeState {
  resumes: ResumeResponse[];
  currentResume: ResumeResponse | null;
  currentModules: ModuleResponse[];
  currentFields: FieldResponse[];
  loading: boolean;
  error: string | null;

  // Resume actions
  fetchResumes: () => Promise<void>;
  createResume: (data: ResumeCreate) => Promise<ResumeResponse>;
  updateResume: (id: string, data: ResumeUpdate) => Promise<void>;
  deleteResume: (id: string) => Promise<void>;
  setCurrentResume: (resume: ResumeResponse | null) => void;

  // Module actions
  fetchModules: (resumeId: string) => Promise<void>;
  createModule: (resumeId: string, data: ModuleCreate) => Promise<ModuleResponse>;
  updateModule: (id: string, data: ModuleUpdate) => Promise<void>;
  deleteModule: (id: string) => Promise<void>;

  // Field actions
  fetchFields: (moduleId: string) => Promise<void>;
  createField: (moduleId: string, data: FieldCreate) => Promise<FieldResponse>;
  updateField: (id: string, data: FieldUpdate) => Promise<void>;
  deleteField: (id: string) => Promise<void>;

  // Export
  exportResume: (id: string, format: ExportFormat) => Promise<string>;

  // UI state
  clearError: () => void;
}

export const useResumeStore = create<ResumeState>((set, get) => ({
  resumes: [],
  currentResume: null,
  currentModules: [],
  currentFields: [],
  loading: false,
  error: null,

  // ── Resume ────────────────────────────────────────────────

  fetchResumes: async () => {
    set({ loading: true, error: null });
    try {
      const resumes = await resumeApi.list();
      set({ resumes, loading: false });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to fetch resumes',
        loading: false,
      });
    }
  },

  createResume: async (data) => {
    set({ loading: true, error: null });
    try {
      const resume = await resumeApi.create(data);
      set((state) => ({
        resumes: [resume, ...state.resumes],
        loading: false,
      }));
      return resume;
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to create resume',
        loading: false,
      });
      throw err;
    }
  },

  updateResume: async (id, data) => {
    set({ loading: true, error: null });
    try {
      const updated = await resumeApi.update(id, data);
      set((state) => ({
        resumes: state.resumes.map((r) => (r.id === id ? updated : r)),
        currentResume:
          state.currentResume?.id === id ? updated : state.currentResume,
        loading: false,
      }));
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to update resume',
        loading: false,
      });
      throw err;
    }
  },

  deleteResume: async (id) => {
    set({ loading: true, error: null });
    try {
      await resumeApi.delete(id);
      set((state) => ({
        resumes: state.resumes.filter((r) => r.id !== id),
        currentResume:
          state.currentResume?.id === id ? null : state.currentResume,
        loading: false,
      }));
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to delete resume',
        loading: false,
      });
      throw err;
    }
  },

  setCurrentResume: (resume) => set({ currentResume: resume }),

  // ── Module ─────────────────────────────────────────────────

  fetchModules: async (resumeId) => {
    set({ loading: true, error: null });
    try {
      const modules = await moduleApi.list(resumeId);
      set({ currentModules: modules, loading: false });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to fetch modules',
        loading: false,
      });
    }
  },

  createModule: async (resumeId, data) => {
    set({ loading: true, error: null });
    try {
      const module = await moduleApi.create(resumeId, data);
      set((state) => ({
        currentModules: [...state.currentModules, module],
        loading: false,
      }));
      return module;
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to create module',
        loading: false,
      });
      throw err;
    }
  },

  updateModule: async (id, data) => {
    set({ loading: true, error: null });
    try {
      const updated = await moduleApi.update(id, data);
      set((state) => ({
        currentModules: state.currentModules.map((m) =>
          m.id === id ? updated : m
        ),
        loading: false,
      }));
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to update module',
        loading: false,
      });
      throw err;
    }
  },

  deleteModule: async (id) => {
    set({ loading: true, error: null });
    try {
      await moduleApi.delete(id);
      set((state) => ({
        currentModules: state.currentModules.filter((m) => m.id !== id),
        loading: false,
      }));
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to delete module',
        loading: false,
      });
      throw err;
    }
  },

  // ── Field ──────────────────────────────────────────────────

  fetchFields: async (moduleId) => {
    set({ loading: true, error: null });
    try {
      const fields = await fieldApi.list(moduleId);
      set({ currentFields: fields, loading: false });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to fetch fields',
        loading: false,
      });
    }
  },

  createField: async (moduleId, data) => {
    set({ loading: true, error: null });
    try {
      const field = await fieldApi.create(moduleId, data);
      set((state) => ({
        currentFields: [...state.currentFields, field],
        loading: false,
      }));
      return field;
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to create field',
        loading: false,
      });
      throw err;
    }
  },

  updateField: async (id, data) => {
    set({ loading: true, error: null });
    try {
      const updated = await fieldApi.update(id, data);
      set((state) => ({
        currentFields: state.currentFields.map((f) =>
          f.id === id ? updated : f
        ),
        loading: false,
      }));
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to update field',
        loading: false,
      });
      throw err;
    }
  },

  deleteField: async (id) => {
    set({ loading: true, error: null });
    try {
      await fieldApi.delete(id);
      set((state) => ({
        currentFields: state.currentFields.filter((f) => f.id !== id),
        loading: false,
      }));
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to delete field',
        loading: false,
      });
      throw err;
    }
  },

  // ── Export ─────────────────────────────────────────────────

  exportResume: async (id, format) => {
    set({ loading: true, error: null });
    try {
      const result = await exportApi.export(id, format);
      set({ loading: false });
      return result.content;
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to export resume',
        loading: false,
      });
      throw err;
    }
  },

  // ── UI ────────────────────────────────────────────────────

  clearError: () => set({ error: null }),
}));
