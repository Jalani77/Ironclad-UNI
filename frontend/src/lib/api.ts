import axios from 'axios';
import { AuditReport, Substitution, Course, Student } from '@/types';

const api = axios.create({
  // IMPORTANT: use same-origin so this works in port-forwarded/cloud dev.
  // Next.js rewrites proxy `/api/*` to the backend.
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export const studentApi = {
  list: async (): Promise<Student[]> => {
    const response = await api.get<Student[]>('/api/students');
    return response.data;
  },
};

export default api;
