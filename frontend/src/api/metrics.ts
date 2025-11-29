import { httpClient } from './http';
import type { ModelMetrics } from '../types';

export const metricsApi = {
  getModelMetrics: async (): Promise<ModelMetrics> => {
    const response = await httpClient.get<ModelMetrics>('/metrics');
    return response.data;
  },
};

