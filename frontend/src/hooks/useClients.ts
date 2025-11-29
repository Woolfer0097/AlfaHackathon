import { useQuery } from '@tanstack/react-query';
import { clientsApi } from '../api/clients';
import type { Client } from '../types';

export const useClients = () => {
  return useQuery<Client[]>({
    queryKey: ['clients'],
    queryFn: clientsApi.getClients,
  });
};

export const useClient = (id: number | null) => {
  return useQuery<Client>({
    queryKey: ['client', id],
    queryFn: () => clientsApi.getClient(id!),
    enabled: !!id,
  });
};

