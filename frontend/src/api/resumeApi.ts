import { apiClient } from './client';
import type {
  ResumeCreate,
  ResumeUpdate,
  ResumeResponse,
  PaginatedData,
} from './types';

export const resumeApi = {
  /** GET /api/resumes — List all resumes */
  list: async (): Promise<ResumeResponse[]> => {
    const response = await apiClient.get<PaginatedData<ResumeResponse>>('/resumes');
    return response.data.data;
  },

  /** GET /api/resumes/:id — Get a single resume */
  get: async (id: string): Promise<ResumeResponse> => {
    const response = await apiClient.get<ResumeResponse>(`/resumes/${id}`);
    return response.data;
  },

  /** POST /api/resumes — Create a new resume */
  create: async (data: ResumeCreate): Promise<ResumeResponse> => {
    const response = await apiClient.post<ResumeResponse>('/resumes', data);
    return response.data;
  },

  /** PATCH /api/resumes/:id — Update a resume */
  update: async (id: string, data: ResumeUpdate): Promise<ResumeResponse> => {
    const response = await apiClient.patch<ResumeResponse>(`/resumes/${id}`, data);
    return response.data;
  },

  /** DELETE /api/resumes/:id — Delete a resume */
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/resumes/${id}`);
  },
};
