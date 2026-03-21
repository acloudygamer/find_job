import { apiClient } from './client';
import type {
  ModuleCreate,
  ModuleUpdate,
  ModuleResponse,
  ReorderModulesRequest,
} from './types';

export const moduleApi = {
  /** GET /api/resumes/:resumeId/modules — List modules for a resume */
  list: async (resumeId: string): Promise<ModuleResponse[]> => {
    const response = await apiClient.get<ModuleResponse[]>(
      `/resumes/${resumeId}/modules`
    );
    return response.data;
  },

  /** GET /api/modules/:id — Get a single module */
  get: async (id: string): Promise<ModuleResponse> => {
    const response = await apiClient.get<ModuleResponse>(`/modules/${id}`);
    return response.data;
  },

  /** POST /api/resumes/:resumeId/modules — Create a new module */
  create: async (
    resumeId: string,
    data: ModuleCreate
  ): Promise<ModuleResponse> => {
    const response = await apiClient.post<ModuleResponse>(
      `/resumes/${resumeId}/modules`,
      data
    );
    return response.data;
  },

  /** PATCH /api/modules/:id — Update a module */
  update: async (
    id: string,
    data: ModuleUpdate
  ): Promise<ModuleResponse> => {
    const response = await apiClient.patch<ModuleResponse>(`/modules/${id}`, data);
    return response.data;
  },

  /** DELETE /api/modules/:id — Delete a module */
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/modules/${id}`);
  },

  /** POST /api/modules/reorder — Reorder modules */
  reorder: async (data: ReorderModulesRequest): Promise<void> => {
    await apiClient.post('/modules/reorder', data);
  },
};
