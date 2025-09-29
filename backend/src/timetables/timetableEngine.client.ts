import axios, { AxiosInstance } from 'axios';

export interface TimetableEngineGeneratePayload {
  school_id: string;
  academic_year_id: string;
  classes: any[];
  subjects: any[];
  teachers: any[];
  time_slots: any[];
  rooms: any[];
  constraints: any[];
  options: number;
  timeout: number;
  weights: Record<string, number>;
}

export interface TimetableEngineSolution {
  timetable: {
    id: string;
    school_id: string;
    academic_year_id: string;
    status: string;
    metadata?: Record<string, unknown>;
    entries: Array<Record<string, unknown>>;
  };
  total_score: number;
  feasible: boolean;
  conflicts: string[];
  metrics: Record<string, unknown>;
}

export interface TimetableEngineGenerateResponse {
  solutions: TimetableEngineSolution[];
  generation_time: number;
  conflicts?: string[] | null;
  suggestions?: string[] | null;
}

export class TimetableEngineClient {
  private client: AxiosInstance;

  constructor(baseURL = process.env.TIMETABLE_ENGINE_URL || 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      timeout: Number(process.env.TIMETABLE_ENGINE_TIMEOUT || 90000)
    });
  }

  async health() {
    const response = await this.client.get('/health');
    return response.data;
  }

  async generate(payload: TimetableEngineGeneratePayload): Promise<TimetableEngineGenerateResponse> {
    const response = await this.client.post('/generate', payload);
    return response.data;
  }

  async validate(payload: { entities: Record<string, unknown>; constraints: any[] }) {
    const response = await this.client.post('/validate', payload);
    return response.data;
  }
}
