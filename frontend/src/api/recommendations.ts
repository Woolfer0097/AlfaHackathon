import { httpClient } from './http';
import type { Recommendation } from '../types';

export const recommendationsApi = {
  getRecommendations: async (clientId: number): Promise<Recommendation[]> => {
    const response = await httpClient.get<Recommendation[]>(`/clients/${clientId}/recommendations`);
    return response.data;
  },
};

