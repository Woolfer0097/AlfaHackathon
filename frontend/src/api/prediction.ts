import { httpClient } from './http';
import type { IncomePrediction, ShapResponse } from '../types';

export const predictionApi = {
  getClientIncome: async (clientId: number): Promise<IncomePrediction> => {
    const response = await httpClient.get<IncomePrediction>(`/clients/${clientId}/income`);
    return response.data;
  },

  getClientShap: async (clientId: number): Promise<ShapResponse> => {
    const response = await httpClient.get<ShapResponse>(`/clients/${clientId}/shap`);
    return response.data;
  },
};

