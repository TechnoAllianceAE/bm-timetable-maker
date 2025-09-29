import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000',
  withCredentials: false,
});

apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers = config.headers ?? {};
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export const authAPI = {
  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),
  register: (payload: { name: string; email: string; password: string; role: string }) =>
    apiClient.post('/auth/register', payload),
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  },
};

export const schoolAPI = {
  list: () => apiClient.get('/schools'),
  get: (id: string) => apiClient.get(`/schools/${id}`),
};

export const userAPI = {
  list: () => apiClient.get('/users'),
  get: (id: string) => apiClient.get(`/users/${id}`),
  create: (payload: unknown) => apiClient.post('/users', payload),
};

export const teacherAPI = {
  list: () => apiClient.get('/teachers'),
  get: (id: string) => apiClient.get(`/teachers/${id}`),
};

export const classAPI = {
  list: () => apiClient.get('/classes'),
  get: (id: string) => apiClient.get(`/classes/${id}`),
};

export const roomAPI = {
  list: () => apiClient.get('/rooms'),
  get: (id: string) => apiClient.get(`/rooms/${id}`),
};

interface GenerateTimetablePayload {
  schoolId: string;
  name: string;
  description?: string;
  startDate: string;
  endDate: string;
  periodsPerDay: number;
  daysPerWeek: number;
  periodDuration: number;
  breakDuration: number;
  lunchDuration: number;
  constraints: Record<string, unknown>;
}

export const timetableAPI = {
  list: () => apiClient.get('/timetables'),
  get: (id: string) => apiClient.get(`/timetables/${id}`),
  create: (payload: unknown) => apiClient.post('/timetables', payload),
  delete: (id: string) => apiClient.delete(`/timetables/${id}`),
  activate: (id: string) => apiClient.post(`/timetables/${id}/activate`),
  generate: (payload: GenerateTimetablePayload) => apiClient.post('/timetables/generate', payload),
};

export const timeslotAPI = {
  list: (timetableId: string) => apiClient.get(`/timetables/${timetableId}/entries`),
};

export default apiClient;
