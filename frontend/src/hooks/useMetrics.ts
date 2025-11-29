import { useQuery } from '@tanstack/react-query';
import { metricsApi } from '../api/metrics';
import type { ModelMetrics } from '../types';

export const useModelMetrics = () => {
  return useQuery<ModelMetrics>({
    queryKey: ['model-metrics'],
    queryFn: metricsApi.getModelMetrics,
  });
};

