import { useState } from 'react';
import {
  Box,
  Container,
  TextField,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
  Stack,
  Pagination,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';
import { useClientsPaginated, useClient, useClientsCount } from '../hooks/useClients';
import { useClientIncome, useClientShap } from '../hooks/usePrediction';
import { useRecommendations } from '../hooks/useRecommendations';

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0,
  }).format(value);
};

const formatCurrencyShort = (value: number) => {
  return `${Math.round(value / 1000)} тыс. ₽`;
};

const ITEMS_PER_PAGE = 50;

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

export const ClientPage = () => {
  const [selectedClientId, setSelectedClientId] = useState<number | null>(null);
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRecommendation, setSelectedRecommendation] = useState<any>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const offset = (page - 1) * ITEMS_PER_PAGE;
  
  // Use server-side pagination
  const { data: paginatedClients, isLoading: clientsLoading, error: clientsError } = useClientsPaginated(
    ITEMS_PER_PAGE,
    offset,
    searchQuery.trim() || undefined
  );
  
  // Get total count for pagination
  const { data: totalCount = 0 } = useClientsCount(searchQuery.trim() || undefined);
  const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE);

  const { data: client, isLoading: clientLoading } = useClient(selectedClientId);
  const { data: income, isLoading: incomeLoading } = useClientIncome(selectedClientId);
  const { data: shap, isLoading: shapLoading } = useClientShap(selectedClientId);
  const { data: recommendations, isLoading: recommendationsLoading } = useRecommendations(selectedClientId);

  const getRiskColor = (score: number) => {
    // Adjusted thresholds: lower risk scores are now considered "good"
    // < 40% = low risk (green)
    // 40-70% = medium risk (yellow)
    // >= 70% = high risk (red)
    if (score < 0.4) return 'success';
    if (score < 0.7) return 'warning';
    return 'error';
  };

  // Prepare chart data showing cumulative income impact (waterfall effect)
  // Shows how each feature affects income starting from base_value
  const chartData = (() => {
    if (!shap || shap.base_value === undefined) return [];
    
    const baseValue = shap.base_value;
    // Sort features by absolute SHAP value (most important first) for better visualization
    const sortedFeatures = [...shap.features].sort(
      (a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value)
    );
    
    // Calculate cumulative income: each bar shows income after adding this feature's impact
    let cumulativeIncome = baseValue;
    return sortedFeatures.map((f) => {
      cumulativeIncome += f.shap_value;
      const impact = f.shap_value; // SHAP impact value for this feature
      
      return {
        name: f.description || f.feature_name,
        income: cumulativeIncome, // Cumulative income after this feature
        impact: impact, // Impact of this feature
        baseValue: baseValue, // Base value for reference
        direction: f.direction,
      };
    });
  })();

  const handleOpenDialog = (recommendation: any) => {
    setSelectedRecommendation(recommendation);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedRecommendation(null);
  };

  const handleClientClick = (clientId: number) => {
    setSelectedClientId(clientId);
    // Scroll to top of detail view
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Клиенты
      </Typography>

      {/* Search and Client Cards Section */}
      {selectedClientId === null && (
        <>
          <Box sx={{ mb: 4 }}>
            <TextField
              fullWidth
              label="Поиск клиентов"
              placeholder="Введите имя, ID или город..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPage(1); // Reset to first page on search
              }}
              sx={{ mb: 3 }}
            />
          </Box>

          {clientsError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              Ошибка загрузки списка клиентов
            </Alert>
          )}

          {clientsLoading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: {
                    xs: '1fr',
                    sm: 'repeat(2, 1fr)',
                    md: 'repeat(3, 1fr)',
                    lg: 'repeat(5, 1fr)',
                  },
                  gap: 2,
                  mb: 4,
                }}
              >
                {(paginatedClients || []).filter((client) => client.id !== 0).map((client) => (
                  <Card
                    key={client.id}
                    sx={{
                      height: '100%',
                      cursor: 'pointer',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: 4,
                      },
                    }}
                    onClick={() => handleClientClick(client.id)}
                  >
                    <CardContent>
                      <Typography variant="h6" gutterBottom noWrap>
                        {client.full_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        ID: {client.id}
                      </Typography>
                      {client.city && (
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {client.city}
                        </Typography>
                      )}
                      {client.age && (
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {client.age} лет
                        </Typography>
                      )}
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Риск-скор
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={client.risk_score * 100}
                          sx={{ height: 6, borderRadius: 1, mb: 1 }}
                          color={getRiskColor(client.risk_score) as any}
                        />
                        <Typography variant="caption" color="text.secondary">
                          {(client.risk_score * 100).toFixed(0)}%
                        </Typography>
                      </Box>
                      {client.incomeValue && (
                        <Typography variant="body2" sx={{ mt: 1, fontWeight: 'medium' }}>
                          {formatCurrencyShort(client.incomeValue)}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </Box>

              {totalPages > 1 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
                  <Pagination
                    count={totalPages}
                    page={page}
                    onChange={(_, value) => setPage(value)}
                    color="primary"
                    size="large"
                  />
                </Box>
              )}

              {(!paginatedClients || paginatedClients.length === 0) && !clientsLoading && (
                <Alert severity="info">
                  Клиенты не найдены. Попробуйте изменить поисковый запрос.
                </Alert>
              )}
            </>
          )}
        </>
      )}

      {/* Client Detail View */}
      {selectedClientId !== null && (
        <>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="outlined"
              onClick={() => setSelectedClientId(null)}
              sx={{ mb: 2 }}
            >
              ← Назад к списку клиентов
            </Button>
          </Box>

          {clientLoading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : client ? (
            <Card sx={{ mb: 4 }}>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  {client.full_name}
                </Typography>
                <Stack spacing={2} sx={{ mt: 1 }}>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                    <Box sx={{ minWidth: 150 }}>
                      <Typography variant="body2" color="text.secondary">
                        Возраст
                      </Typography>
                      <Typography variant="body1">
                        {client.age !== null && client.age !== undefined ? `${client.age} лет` : 'Не указан'}
                      </Typography>
                    </Box>
                    {client.gender && (
                      <Box sx={{ minWidth: 150 }}>
                        <Typography variant="body2" color="text.secondary">
                          Пол
                        </Typography>
                        <Typography variant="body1">{client.gender}</Typography>
                      </Box>
                    )}
                    <Box sx={{ minWidth: 150 }}>
                      <Typography variant="body2" color="text.secondary">
                        Город
                      </Typography>
                      <Typography variant="body1">{client.city || 'Не указан'}</Typography>
                    </Box>
                    {client.adminarea && (
                      <Box sx={{ minWidth: 200 }}>
                        <Typography variant="body2" color="text.secondary">
                          Регион
                        </Typography>
                        <Typography variant="body1">{client.adminarea}</Typography>
                      </Box>
                    )}
                    <Box sx={{ minWidth: 150 }}>
                      <Typography variant="body2" color="text.secondary">
                        Сегмент
                      </Typography>
                      <Typography variant="body1">{client.segment || 'Не указан'}</Typography>
                    </Box>
                    {client.incomeValue !== null && client.incomeValue !== undefined && (
                      <Box sx={{ minWidth: 200 }}>
                        <Typography variant="body2" color="text.secondary">
                          Текущий доход
                        </Typography>
                        <Typography variant="body1">{formatCurrency(client.incomeValue)}</Typography>
                      </Box>
                    )}
                    {client.incomeValueCategory && (
                      <Box sx={{ minWidth: 150 }}>
                        <Typography variant="body2" color="text.secondary">
                          Категория дохода
                        </Typography>
                        <Typography variant="body1">{client.incomeValueCategory}</Typography>
                      </Box>
                    )}
                    <Box sx={{ minWidth: 200, flexGrow: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Риск-скор
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={client.risk_score * 100}
                          sx={{ flexGrow: 1, height: 8, borderRadius: 1 }}
                          color={getRiskColor(client.risk_score) as any}
                        />
                        <Typography variant="body2">
                          {(client.risk_score * 100).toFixed(0)}%
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      Продукты
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {client.products.map((product) => (
                        <Chip key={product} label={product} size="small" />
                      ))}
                    </Box>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          ) : null}

          {incomeLoading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : income ? (
            <Card sx={{ mb: 4 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Прогноз дохода
                </Typography>
                <Box sx={{ mt: 3, mb: 2 }}>
                  <Typography variant="h3" color="primary" fontWeight="bold">
                    {formatCurrency(income.predicted_income)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Диапазон: {formatCurrency(income.lower_bound)} – {formatCurrency(income.upper_bound)}
                  </Typography>
                </Box>
                <Box sx={{ mt: 3 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Позиция прогноза в диапазоне
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={
                      ((income.predicted_income - income.lower_bound) /
                        (income.upper_bound - income.lower_bound)) *
                      100
                    }
                    sx={{ height: 10, borderRadius: 1 }}
                  />
                </Box>
              </CardContent>
            </Card>
          ) : null}

          {shapLoading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : shap ? (
            <>
              <Card sx={{ mb: 4 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Объяснение прогноза (SHAP)
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    {shap.text_explanation}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    График показывает влияние каждой фичи на итоговый доход. Каждый столбец показывает доход после учета влияния соответствующей фичи (кумулятивно от базового дохода).
                  </Typography>

                  <Box sx={{ mb: 4 }}>
                    <ResponsiveContainer width="100%" height={400}>
                      <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="name"
                          angle={-45}
                          textAnchor="end"
                          height={120}
                          interval={0}
                        />
                        <YAxis 
                          tickFormatter={(value) => formatCurrencyShort(value)}
                        />
                        {shap?.base_value !== undefined && (
                          <ReferenceLine 
                            y={shap.base_value} 
                            stroke="#666" 
                            strokeDasharray="3 3" 
                            label={{ value: "Базовый доход", position: "right" }}
                          />
                        )}
                        <Tooltip 
                          formatter={(value: number, name: string, props: any) => {
                            if (name === 'income') {
                              const impact = props.payload.impact;
                              const sign = impact >= 0 ? '+' : '';
                              return [
                                `${formatCurrency(value)}\nВлияние: ${sign}${formatCurrencyShort(Math.abs(impact))}`,
                                'Доход после влияния'
                              ];
                            }
                            return value;
                          }}
                          labelFormatter={(label) => label}
                          contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)' }}
                        />
                        <Legend />
                        <Bar
                          dataKey="income"
                          name="Доход (кумулятивно)"
                        >
                          {chartData.map((entry: any, index: number) => (
                            <Cell 
                              key={`cell-${index}`} 
                              fill={entry.impact >= 0 ? '#2e7d32' : '#d32f2f'} 
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                    {shap?.base_value !== undefined && (
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1, textAlign: 'center' }}>
                        Базовый доход: {formatCurrency(shap.base_value)}
                      </Typography>
                    )}
                  </Box>

                  {shap.base_value !== undefined && (
                    <Paper sx={{ p: 2, bgcolor: 'background.default', mb: 3 }}>
                      <Typography variant="body2" component="div">
                        <Box component="span">Базовый доход: {formatCurrency(shap.base_value)}</Box>
                        {shap.features.map((f, idx) => (
                          <Box key={idx} component="div" sx={{ mt: 0.5 }}>
                            {f.direction === 'positive' ? '+' : '-'} {f.description || f.feature_name}:{' '}
                            {formatCurrencyShort(Math.abs(f.shap_value))}
                          </Box>
                        ))}
                        <Box component="div" sx={{ mt: 1, fontWeight: 'bold' }}>
                          = Итог: {income ? formatCurrency(income.predicted_income) : ''}
                        </Box>
                      </Typography>
                    </Paper>
                  )}

                  <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
                    <Box sx={{ flex: 1, minWidth: 200 }}>
                      <Typography variant="subtitle2" color="error" gutterBottom>
                        ↓ -доход
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {shap.features
                          .filter((f) => f.direction === 'negative')
                          .map((f) => (
                            <Chip
                              key={f.feature_name}
                              label={f.description || f.feature_name}
                              color="error"
                              size="small"
                              title={f.feature_name}
                            />
                          ))}
                      </Box>
                    </Box>
                    <Box sx={{ flex: 1, minWidth: 200 }}>
                      <Typography variant="subtitle2" color="success.main" gutterBottom>
                        ↑ +доход
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {shap.features
                          .filter((f) => f.direction === 'positive')
                          .map((f) => (
                            <Chip
                              key={f.feature_name}
                              label={f.description || f.feature_name}
                              color="success"
                              size="small"
                              title={f.feature_name}
                            />
                          ))}
                      </Box>
                    </Box>
                  </Box>

                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Признак (описание)</TableCell>
                          <TableCell>Значение</TableCell>
                          <TableCell>SHAP значение</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {shap.features.map((feature, idx) => (
                          <TableRow key={idx}>
                            <TableCell>
                              <Typography variant="body2" component="div">
                                {feature.description || (
                                  <span style={{ color: '#d32f2f' }}>
                                    {feature.feature_name} (описание отсутствует)
                                  </span>
                                )}
                              </Typography>
                              {feature.description && (
                                <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                                  {feature.feature_name}
                                </Typography>
                              )}
                            </TableCell>
                            <TableCell>{feature.value}</TableCell>
                            <TableCell
                              sx={{
                                color: feature.direction === 'positive' ? 'success.main' : 'error.main',
                              }}
                            >
                              {feature.direction === 'positive' ? '+' : ''}
                              {feature.shap_value.toFixed(2)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </>
          ) : null}

          {/* Recommendations Section */}
          {recommendationsLoading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : recommendations && recommendations.length > 0 ? (
            <Card sx={{ mb: 4 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Рекомендации продуктов
                </Typography>
                <Box
                  sx={{
                    display: 'grid',
                    gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' },
                    gap: 3,
                    mt: 1,
                  }}
                >
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
                            Лимит: {formatCurrency(recommendation.limit)}
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
              </CardContent>
            </Card>
          ) : recommendations && recommendations.length === 0 ? (
            <Card sx={{ mb: 4 }}>
              <CardContent>
                <Alert severity="info">Рекомендации не найдены для выбранного клиента</Alert>
              </CardContent>
            </Card>
          ) : null}
        </>
      )}

      {/* Recommendation Detail Dialog */}
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
                  {formatCurrency(selectedRecommendation.limit)}
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
