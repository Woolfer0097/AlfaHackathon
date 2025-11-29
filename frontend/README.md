# Frontend - Альфа-Банк ML Демо

React приложение для демонстрации ML модели прогнозирования дохода клиентов.

## Технологии

- React 19 + TypeScript
- Material-UI (MUI) v7
- Recharts для графиков
- React Query для работы с API
- React Router для навигации
- Axios для HTTP запросов

## Установка и запуск

### Локальная разработка

1. Установите зависимости:
```bash
npm install
```

2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

3. Укажите URL бэкенда в `.env`:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

4. Запустите dev сервер:
```bash
npm run dev
```

Приложение будет доступно по адресу `http://localhost:5173`

### Сборка для production

```bash
npm run build
```

Собранные файлы будут в папке `dist/`

## Структура проекта

```
src/
├── api/              # API клиенты
│   ├── http.ts       # Axios инстанс
│   ├── clients.ts    # API клиентов
│   ├── prediction.ts # API прогнозов
│   ├── recommendations.ts
│   └── metrics.ts
├── hooks/            # React Query хуки
│   ├── useClients.ts
│   ├── usePrediction.ts
│   ├── useRecommendations.ts
│   └── useMetrics.ts
├── layout/           # Компоненты layout
│   └── MainLayout.tsx
├── pages/            # Страницы приложения
│   ├── ClientPage.tsx
│   ├── RecommendationsPage.tsx
│   └── MonitoringPage.tsx
├── types/            # TypeScript типы
│   └── index.ts
├── theme.ts          # MUI тема
└── App.tsx           # Главный компонент
```

## Демо-сценарий

1. **Открыть страницу "Клиент"**
   - Выбрать клиента из списка
   - Просмотреть информацию о клиенте (ФИО, возраст, город, сегмент, продукты, риск-скор)

2. **Просмотреть прогноз дохода**
   - Увидеть предсказанный доход с диапазоном
   - Визуализация позиции прогноза в диапазоне

3. **Изучить SHAP объяснения**
   - Текстовое объяснение
   - График влияния признаков
   - Waterfall разбивка (базовый доход + вклады признаков)
   - Force plot (признаки, тянущие вверх/вниз)
   - Таблица с детальной информацией

4. **Перейти на страницу "Рекомендации"**
   - Выбрать того же клиента
   - Просмотреть рекомендованные продукты
   - Открыть детали продукта

5. **Проверить мониторинг модели**
   - Метрики качества (WMAE, количество записей, предсказаний)
   - График истории экспериментов
   - График ошибок по сегментам

## API Endpoints

Приложение ожидает следующие endpoints:

- `GET /api/v1/clients` - список клиентов
- `GET /api/v1/clients/:id` - информация о клиенте
- `GET /api/v1/clients/:id/income` - прогноз дохода
- `GET /api/v1/clients/:id/shap` - SHAP объяснения
- `GET /api/v1/clients/:id/recommendations` - рекомендации
- `GET /api/v1/metrics` - метрики модели

## Переменные окружения

- `VITE_API_BASE_URL` - базовый URL API (по умолчанию: `http://localhost:8000/api/v1`)
