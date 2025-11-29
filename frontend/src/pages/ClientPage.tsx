import { useState } from 'react';
import {
  Box,
  Container,
  Autocomplete,
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
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useClients, useClient } from '../hooks/useClients';
import { useClientIncome, useClientShap } from '../hooks/usePrediction';

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

export const ClientPage = () => {
  const [selectedClientId, setSelectedClientId] = useState<number | null>(null);
  const { data: clients, isLoading: clientsLoading, error: clientsError } = useClients();
  const { data: client, isLoading: clientLoading } = useClient(selectedClientId);
  const { data: income, isLoading: incomeLoading } = useClientIncome(selectedClientId);
  const { data: shap, isLoading: shapLoading } = useClientShap(selectedClientId);

  const getRiskColor = (score: number) => {
    if (score < 0.3) return 'success';
    if (score < 0.7) return 'warning';
    return 'error';
  };

  const chartData = shap?.features.map((f) => ({
    name: f.feature_name,
    value: f.shap_value,
    direction: f.direction,
  })) || [];

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Информация о клиенте
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
          Выберите клиента из списка для просмотра информации
        </Alert>
      )}

      {selectedClientId && (
        <>
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
                      <Typography variant="body1">{client.age} лет</Typography>
                    </Box>
                    <Box sx={{ minWidth: 150 }}>
                      <Typography variant="body2" color="text.secondary">
                        Город
                      </Typography>
                      <Typography variant="body1">{client.city}</Typography>
                    </Box>
                    <Box sx={{ minWidth: 150 }}>
                      <Typography variant="body2" color="text.secondary">
                        Сегмент
                      </Typography>
                      <Typography variant="body1">{client.segment}</Typography>
                    </Box>
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
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar
                          dataKey="value"
                          fill="#EF3124"
                          name="SHAP значение"
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>

                  {shap.base_value !== undefined && (
                    <Paper sx={{ p: 2, bgcolor: 'background.default', mb: 3 }}>
                      <Typography variant="body2" component="div">
                        <Box component="span">Базовый доход: {formatCurrency(shap.base_value)}</Box>
                        {shap.features.map((f, idx) => (
                          <Box key={idx} component="div" sx={{ mt: 0.5 }}>
                            {f.direction === 'positive' ? '+' : '-'} {f.feature_name}:{' '}
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
                        ↓ Тянуть вниз
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {shap.features
                          .filter((f) => f.direction === 'negative')
                          .map((f) => (
                            <Chip
                              key={f.feature_name}
                              label={f.feature_name}
                              color="error"
                              size="small"
                            />
                          ))}
                      </Box>
                    </Box>
                    <Box sx={{ flex: 1, minWidth: 200 }}>
                      <Typography variant="subtitle2" color="success.main" gutterBottom>
                        ↑ Тянуть вверх
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {shap.features
                          .filter((f) => f.direction === 'positive')
                          .map((f) => (
                            <Chip
                              key={f.feature_name}
                              label={f.feature_name}
                              color="success"
                              size="small"
                            />
                          ))}
                      </Box>
                    </Box>
                  </Box>

                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Признак</TableCell>
                          <TableCell>Значение</TableCell>
                          <TableCell>SHAP значение</TableCell>
                          <TableCell>Описание</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {shap.features.map((feature, idx) => (
                          <TableRow key={idx}>
                            <TableCell>{feature.feature_name}</TableCell>
                            <TableCell>{feature.value}</TableCell>
                            <TableCell
                              sx={{
                                color: feature.direction === 'positive' ? 'success.main' : 'error.main',
                              }}
                            >
                              {feature.direction === 'positive' ? '+' : ''}
                              {feature.shap_value.toFixed(2)}
                            </TableCell>
                            <TableCell>{feature.description || '-'}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </>
          ) : null}
        </>
      )}
    </Container>
  );
};

