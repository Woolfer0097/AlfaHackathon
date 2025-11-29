import {
  Container,
  Typography,
  Paper,
  Box,
  Alert,
  CircularProgress,
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

  const experimentsData = metrics.experiments.map((exp) => ({
    name: exp.name,
    wmae: exp.wmae,
  }));

  const segmentErrorsData = metrics.segment_errors.map((seg) => ({
    segment: seg.segment,
    wmae: seg.wmae,
  }));

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Мониторинг модели
      </Typography>

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

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 3 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            История экспериментов
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={experimentsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="wmae"
                stroke="#EF3124"
                name="WMAE"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </Paper>

        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Ошибки по сегментам
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={segmentErrorsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="segment" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="wmae" fill="#EF3124" name="WMAE" />
            </BarChart>
          </ResponsiveContainer>
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

