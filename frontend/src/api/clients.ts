import { httpClient } from './http';
import type { Client } from '../types';

export const clientsApi = {
  getClients: async (): Promise<Client[]> => {
    const response = await httpClient.get<Client[]>('/clients');
    return response.data;
  },

  getClient: async (id: number): Promise<Client> => {
    const response = await httpClient.get<Client>(`/clients/${id}`);
    return response.data;
  },
};

