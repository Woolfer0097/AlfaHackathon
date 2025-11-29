import { useState } from 'react';
import {
  Box,
  Container,
  Autocomplete,
  TextField,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useClients } from '../hooks/useClients';
import { useRecommendations } from '../hooks/useRecommendations';

const productTypeLabels: Record<string, string> = {
  credit: 'Кредит',
  credit_card: 'Кредитная карта',
  deposit: 'Вклад',
  insurance: 'Страхование',
};

const getProductTypeColor = (type: string) => {
  switch (type) {
    case 'credit':
      return 'primary';
    case 'credit_card':
      return 'secondary';
    case 'deposit':
      return 'success';
    case 'insurance':
      return 'info';
    default:
      return 'default';
  }
};

export const RecommendationsPage = () => {
  const [selectedClientId, setSelectedClientId] = useState<number | null>(null);
  const [selectedRecommendation, setSelectedRecommendation] = useState<any>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data: clients, isLoading: clientsLoading, error: clientsError } = useClients();
  const { data: recommendations, isLoading: recommendationsLoading } = useRecommendations(selectedClientId);

  const handleOpenDialog = (recommendation: any) => {
    setSelectedRecommendation(recommendation);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedRecommendation(null);
  };

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Рекомендации продуктов
      </Typography>

      <Box sx={{ mb: 4 }}>
        <Autocomplete
          options={clients || []}
          getOptionLabel={(option) => `${option.full_name} (ID: ${option.id})`}
          loading={clientsLoading}
          onChange={(_, value) => setSelectedClientId(value?.id || null)}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Выберите клиента"
              placeholder="Начните вводить имя..."
            />
          )}
        />
      </Box>

      {clientsError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Ошибка загрузки списка клиентов
        </Alert>
      )}

      {!selectedClientId && (
        <Alert severity="info">
          Выберите клиента из списка для просмотра рекомендаций
        </Alert>
      )}

      {selectedClientId && (
        <>
          {recommendationsLoading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : recommendations && recommendations.length > 0 ? (
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 3 }}>
              {recommendations.map((recommendation) => (
                <Card key={recommendation.id} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                      <Typography variant="h6" component="div">
                        {recommendation.product_name}
                      </Typography>
                      <Chip
                        label={productTypeLabels[recommendation.product_type] || recommendation.product_type}
                        color={getProductTypeColor(recommendation.product_type) as any}
                        size="small"
                      />
                    </Box>

                    {recommendation.limit && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        Лимит: {new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(recommendation.limit)}
                      </Typography>
                    )}

                    {recommendation.rate && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Ставка: {recommendation.rate}%
                      </Typography>
                    )}

                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {recommendation.reason}
                    </Typography>

                    <Button
                      variant="outlined"
                      size="small"
                      fullWidth
                      onClick={() => handleOpenDialog(recommendation)}
                    >
                      Подробнее
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </Box>
          ) : (
            <Alert severity="info">Рекомендации не найдены для выбранного клиента</Alert>
          )}
        </>
      )}

      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{selectedRecommendation?.product_name}</DialogTitle>
        <DialogContent>
          {selectedRecommendation && (
            <Box>
              <Box sx={{ mb: 2 }}>
                <Chip
                  label={productTypeLabels[selectedRecommendation.product_type] || selectedRecommendation.product_type}
                  color={getProductTypeColor(selectedRecommendation.product_type) as any}
                  sx={{ mb: 2 }}
                />
              </Box>
              {selectedRecommendation.limit && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  <strong>Лимит:</strong>{' '}
                  {new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(selectedRecommendation.limit)}
                </Typography>
              )}
              {selectedRecommendation.rate && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  <strong>Ставка:</strong> {selectedRecommendation.rate}%
                </Typography>
              )}
              <Typography variant="body2" sx={{ mb: 2 }}>
                <strong>Причина рекомендации:</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {selectedRecommendation.reason}
              </Typography>
              {selectedRecommendation.description && (
                <>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Описание:</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {selectedRecommendation.description}
                  </Typography>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Закрыть</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

