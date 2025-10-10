import axios from 'axios';

// Use relative path to leverage Next.js rewrites and avoid CORS
const getBaseURL = () => {
  // Use relative path when in browser to use Next.js proxy
  if (typeof window !== 'undefined') {
    return '/api/v1';
  }
  // Use full URL on server-side
  return 'http://localhost:5000/api/v1';
};

const apiClient = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Engine API client for Timetable Engine v3.5
const getEngineURL = () => {
  if (typeof window !== 'undefined') {
    return 'http://localhost:8000';  // FastAPI server
  }
  return 'http://localhost:8000';
};

const engineClient = axios.create({
  baseURL: getEngineURL(),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,  // 30 second timeout for generation requests
});

apiClient.interceptors.request.use((config) => {
  console.log('=== Axios Request Interceptor ===');
  console.log('Request URL:', config.url);
  console.log('Request method:', config.method);
  console.log('Request baseURL:', config.baseURL);
  console.log('Full URL:', config.baseURL + config.url);
  console.log('Request headers:', config.headers);
  console.log('Request data:', config.data);

  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers = config.headers ?? {};
      config.headers.Authorization = `Bearer ${token}`;
      console.log('Added auth token to request');
    }
  }
  return config;
}, (error) => {
  console.error('Request interceptor error:', error);
  return Promise.reject(error);
});

// Engine client interceptors
engineClient.interceptors.request.use((config) => {
  console.log('=== Engine API Request ===');
  console.log('Request URL:', config.url);
  console.log('Request method:', config.method);
  console.log('Full URL:', config.baseURL + config.url);
  
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers = config.headers ?? {};
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
}, (error) => {
  console.error('Engine request interceptor error:', error);
  return Promise.reject(error);
});

engineClient.interceptors.response.use((response) => {
  console.log('=== Engine API Response ===');
  console.log('Response status:', response.status);
  console.log('Response data:', response.data);
  return response;
}, (error) => {
  console.error('=== Engine API Error ===');
  console.error('Error:', error);
  if (error.response) {
    console.error('Error response status:', error.response.status);
    console.error('Error response data:', error.response.data);
  }
  return Promise.reject(error);
});

apiClient.interceptors.response.use((response) => {
  console.log('=== Axios Response Interceptor ===');
  console.log('Response status:', response.status);
  console.log('Response data:', response.data);
  console.log('Response headers:', response.headers);
  return response;
}, (error) => {
  console.error('=== Axios Response Error Interceptor ===');
  console.error('Error:', error);
  if (error.response) {
    console.error('Error response status:', error.response.status);
    console.error('Error response data:', error.response.data);
    console.error('Error response headers:', error.response.headers);
  } else if (error.request) {
    console.error('No response received. Request:', error.request);
  } else {
    console.error('Error setting up request:', error.message);
  }
  return Promise.reject(error);
});

export const authAPI = {
  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),
  register: (payload: {
    email: string;
    password: string;
    role: string;
    schoolId: string;
    profile?: {
      firstName: string;
      lastName: string;
      phone?: string;
    };
  }) =>
    apiClient.post('/auth/register', payload),
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/auth/login';
    }
  },
};

export const schoolAPI = {
  list: () => apiClient.get('/schools'),
  get: (id: string) => apiClient.get(`/schools/${id}`),
  create: (data: any) => apiClient.post('/schools', data),
  update: (id: string, data: any) => apiClient.put(`/schools/${id}`, data),
  delete: (id: string) => apiClient.delete(`/schools/${id}`),
  deleteSchoolData: (id: string) => apiClient.delete(`/schools/${id}/data`),
};

export const userAPI = {
  list: () => apiClient.get('/users'),
  get: (id: string) => apiClient.get(`/users/${id}`),
  create: (payload: unknown) => apiClient.post('/users', payload),
  update: (id: string, data: unknown) => apiClient.put(`/users/${id}`, data),
  delete: (id: string) => apiClient.delete(`/users/${id}`),
};

export const teacherAPI = {
  list: () => apiClient.get('/teachers'),
  get: (id: string) => apiClient.get(`/teachers/${id}`),
  create: (data: any) => apiClient.post('/teachers', data),
  update: (id: string, data: any) => apiClient.put(`/teachers/${id}`, data),
  delete: (id: string) => apiClient.delete(`/teachers/${id}`),
};

export const classAPI = {
  list: (limit?: number) => apiClient.get('/classes', { params: { limit: limit || 100 } }),
  get: (id: string) => apiClient.get(`/classes/${id}`),
  create: (data: any) => apiClient.post('/classes', data),
  update: (id: string, data: any) => apiClient.put(`/classes/${id}`, data),
  delete: (id: string) => apiClient.delete(`/classes/${id}`),
};

export const subjectAPI = {
  list: () => apiClient.get('/subjects'),
  get: (id: string) => apiClient.get(`/subjects/${id}`),
  create: (data: any) => apiClient.post('/subjects', data),
  update: (id: string, data: any) => apiClient.put(`/subjects/${id}`, data),
  delete: (id: string) => apiClient.delete(`/subjects/${id}`),
};

export const roomAPI = {
  list: (limit?: number) => apiClient.get('/rooms', { params: { limit: limit || 100 } }),
  get: (id: string) => apiClient.get(`/rooms/${id}`),
  create: (data: any) => apiClient.post('/rooms', data),
  update: (id: string, data: any) => apiClient.put(`/rooms/${id}`, data),
  delete: (id: string) => apiClient.delete(`/rooms/${id}`),
};

export const academicYearAPI = {
  list: (schoolId?: string) => apiClient.get('/academic-years', { params: { schoolId } }),
  get: (id: string) => apiClient.get(`/academic-years/${id}`),
  create: (data: any) => apiClient.post('/academic-years', data),
  update: (id: string, data: any) => apiClient.put(`/academic-years/${id}`, data),
  delete: (id: string) => apiClient.delete(`/academic-years/${id}`),
};

interface GenerateTimetablePayload {
  schoolId: string;
  academicYearId: string;
  name?: string;
  engineVersion?: string;
  constraints?: Record<string, unknown>;
}

export const timetableAPI = {
  list: () => apiClient.get('/timetables'),
  get: (id: string) => apiClient.get(`/timetables/${id}`),
  create: (payload: unknown) => apiClient.post('/timetables', payload),
  update: (id: string, data: any) => apiClient.put(`/timetables/${id}`, data),
  delete: (id: string) => apiClient.delete(`/timetables/${id}`),
  activate: (id: string) => apiClient.post(`/timetables/${id}/activate`),
  deactivate: (id: string) => apiClient.post(`/timetables/${id}/deactivate`),
  
  // NEW: Timetable Engine v3.5 API Integration
  generate: (payload: GenerateTimetablePayload) =>
    apiClient.post('/timetables/generate', payload, {
      // Treat 400 as a valid response (constraint validation errors are expected)
      validateStatus: (status) => status < 500,
    }),
  
  // NEW: Engine API endpoints
  engineGenerate: (payload: GenerateTimetablePayload) =>
    engineClient.post('/api/v1/timetables/generate', payload),
  
  getGenerationStatus: (sessionId: string) =>
    engineClient.get(`/api/v1/timetables/generate/${sessionId}/status`),
  
  getGenerationResult: (sessionId: string) =>
    engineClient.get(`/api/v1/timetables/${sessionId}/result`),
  
  getTimetableView: (timetableId: string) =>
    engineClient.get(`/api/v1/timetables/${timetableId}/view`),
  
  listSessions: () => engineClient.get('/api/v1/sessions'),
  
  cleanupSession: (sessionId: string) =>
    engineClient.delete(`/api/v1/sessions/${sessionId}`),
  
  getSystemStats: () => engineClient.get('/api/v1/system/stats'),
  
  getSummary: (id: string) => apiClient.get(`/timetables/${id}/summary`),
};

export const timeslotAPI = {
  list: (timetableId: string) => apiClient.get(`/timetables/${timetableId}/entries`),
};

export default apiClient;
