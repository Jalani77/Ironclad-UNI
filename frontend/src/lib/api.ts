import axios from 'axios';
import { LoginRequest, AuthResponse, AuditReport, Substitution, Course } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export const authApi = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/api/auth/login', credentials);
    return response.data;
  },
};

export const auditApi = {
  getAuditReport: async (studentId: number): Promise<AuditReport> => {
    const response = await api.get<AuditReport>(`/api/audit/${studentId}`);
    return response.data;
  },
  downloadPDF: async (studentId: number): Promise<Blob> => {
    const response = await api.get(`/api/audit/${studentId}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export const substitutionApi = {
  list: async (studentId?: number): Promise<Substitution[]> => {
    const url = studentId ? `/api/substitutions?student_id=${studentId}` : '/api/substitutions';
    const response = await api.get<Substitution[]>(url);
    return response.data;
  },
  create: async (substitution: Omit<Substitution, 'id'>): Promise<Substitution> => {
    const response = await api.post<Substitution>('/api/substitutions', substitution);
    return response.data;
  },
  update: async (id: number, data: Partial<Substitution>): Promise<Substitution> => {
    const response = await api.put<Substitution>(`/api/substitutions/${id}`, data);
    return response.data;
  },
  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/substitutions/${id}`);
  },
};

export const courseApi = {
  list: async (): Promise<Course[]> => {
    const response = await api.get<Course[]>('/api/courses');
    return response.data;
  },
};

export default api;
