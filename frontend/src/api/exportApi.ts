import { apiClient } from './client';
import type { ExportResponse, ExportFormat } from './types';

export const exportApi = {
  /** POST /api/export/:resumeId — Export a resume */
  export: async (
    resumeId: string,
    format: ExportFormat
  ): Promise<ExportResponse> => {
    const response = await apiClient.post<ExportResponse>(
      `/export/${resumeId}`,
      { format }
    );
    return response.data;
  },
};
