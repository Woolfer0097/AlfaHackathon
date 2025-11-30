import { useQuery } from '@tanstack/react-query';
import { predictionApi } from '../api/prediction';
import type { IncomePrediction, ShapResponse } from '../types';

export const useClientIncome = (clientId: number | null) => {
  return useQuery<IncomePrediction>({
    queryKey: ['client-income', clientId],
    queryFn: () => predictionApi.getClientIncome(clientId!),
    enabled: clientId !== null && clientId !== undefined,
  });
};

export const useClientShap = (clientId: number | null) => {
  return useQuery<ShapResponse>({
    queryKey: ['client-shap', clientId],
    queryFn: () => predictionApi.getClientShap(clientId!),
    enabled: clientId !== null && clientId !== undefined,
  });
};

