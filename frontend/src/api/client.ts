import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Response interceptor: unwrap ApiResponse envelope
apiClient.interceptors.response.use(
  (response) => {
    if (response.data && 'success' in response.data) {
      if (!response.data.success) {
        return Promise.reject(new Error(response.data.error || 'API Error'));
      }
      // Return the unwrapped data with the full response object for header access
      return { ...response, data: response.data.data };
    }
    return response;
  },
  (error) => Promise.reject(error)
);
