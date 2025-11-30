import { httpClient } from './http';
import type { Client } from '../types';

export const clientsApi = {
  getClients: async (limit?: number, offset?: number, search?: string): Promise<Client[]> => {
    const params = new URLSearchParams();
    if (limit !== undefined) params.append('limit', limit.toString());
    if (offset !== undefined) params.append('offset', offset.toString());
    if (search) params.append('search', search);
    
    const queryString = params.toString();
    const url = `/clients${queryString ? `?${queryString}` : ''}`;
    const response = await httpClient.get<Client[]>(url);
    return response.data;
  },

  getClient: async (id: number): Promise<Client> => {
    const response = await httpClient.get<Client>(`/clients/${id}`);
    return response.data;
  },

  getClientsCount: async (search?: string): Promise<number> => {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    const queryString = params.toString();
    const url = `/clients/count${queryString ? `?${queryString}` : ''}`;
    const response = await httpClient.get<{ count: number }>(url);
    return response.data.count;
  },
};

