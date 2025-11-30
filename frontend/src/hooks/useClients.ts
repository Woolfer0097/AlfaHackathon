import { useQuery } from '@tanstack/react-query';
import { clientsApi } from '../api/clients';
import type { Client } from '../types';

export const useClients = () => {
  return useQuery<Client[]>({
    queryKey: ['clients'],
    queryFn: () => clientsApi.getClients(),
  });
};

export const useClientsPaginated = (limit: number, offset: number, search?: string) => {
  return useQuery<Client[]>({
    queryKey: ['clients', 'paginated', limit, offset, search],
    queryFn: () => clientsApi.getClients(limit, offset, search),
  });
};

export const useClientsCount = (search?: string) => {
  return useQuery<number>({
    queryKey: ['clients', 'count', search],
    queryFn: () => clientsApi.getClientsCount(search),
  });
};

export const useClient = (id: number | null) => {
  return useQuery<Client>({
    queryKey: ['client', id],
    queryFn: () => clientsApi.getClient(id!),
    enabled: id !== null && id !== undefined,
  });
};

