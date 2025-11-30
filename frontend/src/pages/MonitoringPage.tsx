import {
  Container,
  Typography,
  Paper,
  Box,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useModelMetrics } from '../hooks/useMetrics';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import RemoveIcon from '@mui/icons-material/Remove';

const formatNumber = (value: number) => {
  return new Intl.NumberFormat('ru-RU', {
    maximumFractionDigits: 2,
  }).format(value);
};

const formatDate = (dateString: string) => {
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ru-RU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  } catch {
    return dateString;
  }
};

export const MonitoringPage = () => {
  const { data: metrics, isLoading, error } = useModelMetrics();

  if (isLoading) {
    return (
      <Container maxWidth="xl">
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl">
        <Alert severity="error">Ошибка загрузки метрик модели</Alert>
      </Container>
    );
  }

  if (!metrics) {
    return (
      <Container maxWidth="xl">
        <Alert severity="info">Метрики недоступны</Alert>
      </Container>
    );
  }

  // Use MAE for charts if available, otherwise fall back to WMAE
  const experimentsData = metrics.experiments.map((exp) => ({
    name: exp.name,
    mae: exp.mae ?? exp.wmae, // Use MAE if available, otherwise WMAE
    wmae: exp.wmae, // Keep WMAE for reference
  }));

  const segmentErrorsData = metrics.segment_errors.map((seg) => ({
    segment: seg.segment,
    mae: seg.mae ?? seg.wmae, // Use MAE if available, otherwise WMAE
    wmae: seg.wmae, // Keep WMAE for reference
  }));

  // Training runs data
  const trainingRuns = metrics.training_runs || [];
  const latestRun = trainingRuns.length > 0 ? trainingRuns[trainingRuns.length - 1] : null;
  const previousRun = trainingRuns.length > 1 ? trainingRuns[trainingRuns.length - 2] : null;

  // Calculate trends
  const getTrend = (current: number, previous: number | null) => {
    if (!previous) return { icon: <RemoveIcon />, color: 'text.secondary', change: 0 };
    const change = ((current - previous) / previous) * 100;
    if (change < 0) {
      return { icon: <ArrowDownwardIcon />, color: 'success.main', change: Math.abs(change) };
    } else if (change > 0) {
      return { icon: <ArrowUpwardIcon />, color: 'error.main', change };
    }
    return { icon: <RemoveIcon />, color: 'text.secondary', change: 0 };
  };

  const rmseTrend = latestRun && previousRun ? getTrend(latestRun.rmse, previousRun.rmse) : null;
  const maeTrend = latestRun && previousRun ? getTrend(latestRun.mae, previousRun.mae) : null;
  const r2Trend = latestRun && previousRun ? getTrend(latestRun.r2, previousRun.r2) : null;

  // For time series chart - reverse to show chronological order
  const trainingRunsChartData = [...trainingRuns]
    .reverse()
    .map((run) => ({
      date: formatDate(run.trained_at),
      rmse: run.rmse,
      mae: run.mae,
      r2: run.r2,
    }));

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Мониторинг модели
      </Typography>

      {/* Training Metrics Header Cards */}
      {latestRun && (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3, mb: 4 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              RMSE (последний запуск)
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h4" color="primary">
                {formatNumber(latestRun.rmse)}
              </Typography>
              {rmseTrend && (
                <Box sx={{ display: 'flex', alignItems: 'center', color: rmseTrend.color }}>
                  {rmseTrend.icon}
                  <Typography variant="caption">
                    {rmseTrend.change > 0 ? `${formatNumber(rmseTrend.change)}%` : ''}
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              MAE (последний запуск)
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h4" color="primary">
                {formatNumber(latestRun.mae)}
              </Typography>
              {maeTrend && (
                <Box sx={{ display: 'flex', alignItems: 'center', color: maeTrend.color }}>
                  {maeTrend.icon}
                  <Typography variant="caption">
                    {maeTrend.change > 0 ? `${formatNumber(maeTrend.change)}%` : ''}
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              R² (последний запуск)
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h4" color="primary">
                {formatNumber(latestRun.r2)}
              </Typography>
              {r2Trend && (
                <Box sx={{ display: 'flex', alignItems: 'center', color: r2Trend.color }}>
                  {r2Trend.icon}
                  <Typography variant="caption">
                    {r2Trend.change > 0 ? `${formatNumber(r2Trend.change)}%` : ''}
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Обучено записей
            </Typography>
            <Typography variant="h4" color="primary">
              {new Intl.NumberFormat('ru-RU').format(latestRun.train_samples)}
            </Typography>
          </Paper>
        </Box>
      )}

      {/* General Metrics Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 3, mb: 4 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            WMAE (валидация)
          </Typography>
          <Typography variant="h4" color="primary">
            {metrics.wmae_validation.toFixed(4)}
          </Typography>
        </Paper>
        <Paper sx={{ p: 3 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Обучено записей
          </Typography>
          <Typography variant="h4" color="primary">
            {new Intl.NumberFormat('ru-RU').format(metrics.training_records)} /{' '}
            {new Intl.NumberFormat('ru-RU').format(metrics.validation_records)}
          </Typography>
        </Paper>
        <Paper sx={{ p: 3 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Предсказаний за период
          </Typography>
          <Typography variant="h4" color="primary">
            {new Intl.NumberFormat('ru-RU').format(metrics.predictions_count)}
          </Typography>
        </Paper>
      </Box>

      {/* Training Runs Time Series Chart */}
      {trainingRunsChartData.length > 0 && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            История обучения модели
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={trainingRunsChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" angle={-45} textAnchor="end" height={100} />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="rmse"
                stroke="#EF3124"
                name="RMSE"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="mae"
                stroke="#1976d2"
                name="MAE"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="r2"
                stroke="#2e7d32"
                name="R²"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      )}

      {/* Training Runs Table */}
      {trainingRuns.length > 0 && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            История запусков обучения
          </Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Версия модели</TableCell>
                  <TableCell>Дата обучения</TableCell>
                  <TableCell align="right">Обучающих записей</TableCell>
                  <TableCell align="right">Валидационных записей</TableCell>
                  <TableCell align="right">RMSE</TableCell>
                  <TableCell align="right">MAE</TableCell>
                  <TableCell align="right">R²</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {[...trainingRuns].reverse().map((run, idx) => (
                  <TableRow key={idx} hover>
                    <TableCell>
                      <Chip label={run.model_version} size="small" />
                    </TableCell>
                    <TableCell>{formatDate(run.trained_at)}</TableCell>
                    <TableCell align="right">
                      {new Intl.NumberFormat('ru-RU').format(run.train_samples)}
                    </TableCell>
                    <TableCell align="right">
                      {new Intl.NumberFormat('ru-RU').format(run.valid_samples)}
                    </TableCell>
                    <TableCell align="right">{formatNumber(run.rmse)}</TableCell>
                    <TableCell align="right">{formatNumber(run.mae)}</TableCell>
                    <TableCell align="right">{formatNumber(run.r2)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {/* Existing Charts */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 3 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            История экспериментов
          </Typography>
          {experimentsData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={experimentsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="mae"
                  stroke="#EF3124"
                  name="MAE"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <Alert severity="info">Нет данных об экспериментах</Alert>
          )}
        </Paper>

        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Ошибки по сегментам
          </Typography>
          {segmentErrorsData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={segmentErrorsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="segment" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="mae" fill="#EF3124" name="MAE" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <Alert severity="info">Нет данных по сегментам</Alert>
          )}
        </Paper>
      </Box>

      {metrics.experiments.length > 1 && (
        <Box sx={{ mt: 4 }}>
          <Alert severity="info">
            По мере добавления фич и настройки модели WMAE снизился с{' '}
            {metrics.experiments[0].wmae.toFixed(4)} до{' '}
            {metrics.experiments[metrics.experiments.length - 1].wmae.toFixed(4)}.
          </Alert>
        </Box>
      )}
    </Container>
  );
};
