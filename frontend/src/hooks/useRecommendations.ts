import { useQuery } from '@tanstack/react-query';
import { recommendationsApi } from '../api/recommendations';
import type { Recommendation } from '../types';

export const useRecommendations = (clientId: number | null) => {
  return useQuery<Recommendation[]>({
    queryKey: ['recommendations', clientId],
    queryFn: () => recommendationsApi.getRecommendations(clientId!),
    enabled: !!clientId,
  });
};

