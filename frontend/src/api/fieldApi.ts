import { apiClient } from './client';
import type {
  FieldCreate,
  FieldUpdate,
  FieldResponse,
  ReorderFieldsRequest,
} from './types';

export const fieldApi = {
  /** GET /api/modules/:moduleId/fields — List fields for a module */
  list: async (moduleId: string): Promise<FieldResponse[]> => {
    const response = await apiClient.get<FieldResponse[]>(
      `/modules/${moduleId}/fields`
    );
    return response.data;
  },

  /** GET /api/fields/:id — Get a single field */
  get: async (id: string): Promise<FieldResponse> => {
    const response = await apiClient.get<FieldResponse>(`/fields/${id}`);
    return response.data;
  },

  /** POST /api/modules/:moduleId/fields — Create a new field */
  create: async (
    moduleId: string,
    data: FieldCreate
  ): Promise<FieldResponse> => {
    const response = await apiClient.post<FieldResponse>(
      `/modules/${moduleId}/fields`,
      data
    );
    return response.data;
  },

  /** PATCH /api/fields/:id — Update a field */
  update: async (id: string, data: FieldUpdate): Promise<FieldResponse> => {
    const response = await apiClient.patch<FieldResponse>(`/fields/${id}`, data);
    return response.data;
  },

  /** DELETE /api/fields/:id — Delete a field */
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/fields/${id}`);
  },

  /** POST /api/fields/reorder — Reorder fields */
  reorder: async (data: ReorderFieldsRequest): Promise<void> => {
    await apiClient.post('/fields/reorder', data);
  },
};
