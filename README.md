Демо: https://drive.google.com/file/d/1tpATHR0WWo7jBQMt4bf0R6YgJ9uLwhao/view?usp=sharing

# Alfa Hackathon ML Platform

Платформа для скоринга клиентов банка: ML-модель CatBoost, REST API на FastAPI, витрина мониторинга на React и Nginx-прокси. Проект решает две задачи:
- прогноз дохода клиента, объяснение вклада признаков (SHAP) и хранение истории предсказаний;
- мониторинг качества модели и визуализация метрик для продуктовой команды.


# Команда "..."
Data Scientist Котиев Батыр
Data Analyst Горбачев Фёдор
Backend+DevOPS Кочегаров Данила

## Демо и ML-ноутбук
- Продуктовый стенд: http://31.59.40.65/
- Google Colab с исследованием и обучением модели: https://colab.research.google.com/drive/1T4Mu5kMdsjLVTixKBAu-zR_vfEAbhPA-?usp=sharing
- Видео-демо: https://drive.google.com/file/d/1tpATHR0WWo7jBQMt4bf0R6YgJ9uLwhao/view?usp=sharing

## Архитектура и стек
| Слой | Технологии и версии |
| --- | --- |
| Backend API | Python 3.12, FastAPI 0.104.1, SQLAlchemy 2.x, Pydantic 2.5, Uvicorn 0.24, PostgreSQL 16, CatBoost ≥1.2 |
| ML сервис | CatBoost бинарь `ML/income_model_v3.cbm`, описания признаков и метрики (`ML/model_meta.json`, `metrics.json`, `training_metrics.json`) |
| Frontend | Node.js ≥20, npm ≥10, React 19.2, React Router 7.9, React Query 5.90, Material UI 7.3, Recharts 3.5, Vite 7.2, TypeScript 5.9 |
| Инфраструктура | Docker 25+, docker-compose, Nginx 1.27, PostgreSQL volume, .env через Pydantic Settings |

## Структура репозитория
```
.
├── app/                        # Backend FastAPI-приложение
│   ├── api/                    # Маршруты v1: health, clients, metrics, predictions, recommendations
│   ├── core/                   # Конфиг, логирование, ORM-движок
│   ├── models/                 # SQLAlchemy-модели (клиенты, логи предсказаний, описания признаков)
│   ├── schemas/                # Pydantic-схемы ответов и запросов
│   ├── services/               # Бизнес-логика: загрузка ML-модели, сервис клиентов, рекомендации
│   └── main.py                 # Создание FastAPI-приложения, middleware, регистрация роутов
├── frontend/                   # Витрина аналитики на React
│   ├── src/api/                # Axios-клиент и хуки React Query
│   ├── src/pages/              # ClientPage, MonitoringPage, RecommendationsPage
│   └── Dockerfile              # Сборка Vite-приложения
├── ML/                         # ML-артефакты (датасеты, catboost *.cbm, метрики, описания фичей)
├── nginx/                      # Конфигурация реверс-прокси и проксирование /api → backend
├── scripts/                    # Утилиты загрузки CSV в БД и модификации схемы
├── docker-compose.yml          # Композиция: postgres + app + frontend builder + nginx
├── Dockerfile                  # Сборка backend-образа
├── requirements.txt            # Библиотеки backend (см. версии ниже)
└── main.py                     # Точка входа `python main.py`
```

## Переменные окружения
| Ключ | Значение по умолчанию | Описание |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/hackathon` | Строка подключения для SQLAlchemy, переопределяется в docker-compose |
| `MODEL_PATH` | `ML/income_model_v3.cbm` | CatBoost-модель |
| `MODEL_META_PATH` | `ML/model_meta.json` | Метаданные фичей для explainability |
| `METRICS_PATH` | `ML/metrics.json` | Актуальные метрики модели |
| `TRAINING_METRICS_PATH` | `ML/training_metrics.json` | История обучения |
| `LOG_LEVEL` | `INFO` | Глобальный уровень логирования |
| `LOG_FILE` | `logs/app.log` | Путь до файла логов |
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` (dev) / `/api/v1` (prod) | Конфигурация фронтенда для вызова API |

Создайте `.env` по необходимости (на локальном запуске он автоматически читается `app/core/config.py`).

## Требования к окружению
- Python 3.12
- Node.js ≥ 20.0 и npm ≥ 10.0 (для разработки фронтенда без Docker)
- PostgreSQL 16 (для локального запуска без Compose)
- Docker 25+ и docker-compose (для быстрой установки)

### Версии backend-библиотек
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
numpy>=1.26.0
pandas>=2.0.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
catboost>=1.2.0
```

## Подготовка данных
1. Настройте подключение к PostgreSQL через переменную `DATABASE_URL` или `.env`.
2. Загрузите признаки клиентов (CSV в формате `;` и UTF-8) в таблицу `client_features`:
   ```bash
   python scripts/load_csv_to_db.py --csv ML/hackathon_income_test.csv --drop-table
   ```
3. Для описаний признаков выполните:
   ```bash
   python scripts/load_csv_to_db.py --load-descriptions --descriptions ML/features_description.csv --skip-client-data --drop-table
   ```
4. При необходимости добавьте поля `actual_income` и `prediction_error` в лог предсказаний:
   ```bash
   python scripts/add_prediction_metrics_fields.py
   ```

## Локальный запуск без Docker
### Backend (FastAPI)
```bash
python -m venv .venv
.venv\Scripts\activate          # PowerShell
pip install --upgrade pip
pip install -r requirements.txt

# Настройка переменных окружения (пример PowerShell)
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/hackathon"
$env:MODEL_PATH="ML/income_model_v3.cbm"

python scripts/load_csv_to_db.py --csv ML/hackathon_income_test.csv
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API будет доступен на `http://localhost:8000`, документация — `/docs` и `/redoc`.

### Frontend (Vite)
```bash
cd frontend
npm install
set VITE_API_BASE_URL=http://localhost:8000/api/v1   # Windows CMD, используйте export в bash
npm run dev
```
Dashboard доступен на `http://localhost:5173`. Для продакшн-сборки используйте `npm run build` (артефакт появится в `frontend/dist`).

## Запуск через Docker Compose
```bash
# Полная сборка всех сервисов
docker-compose up --build -d

# Просмотр статуса
docker-compose ps

# Логи отдельных сервисов
docker-compose logs -f app
docker-compose logs -f frontend
```
Сервисы:
- `postgres`: Персистентное хранилище (volume `postgres_data`).
- `app`: Backend (монтирует `./ML` как read-only, пишет логи в `./logs`).
- `frontend`: Сборка React-приложения и публикация `dist` в volume `frontend_dist`.
- `nginx`: Раздаёт фронт `http://localhost/` и проксирует API на `/api/v1`.

Остановка и очистка:
```bash
docker-compose down          # остановить сервисы
docker-compose down -v       # дополнительно удалить volumes (включая БД и dist)
```

## Проверка и диагностика
- Проверка готовности API: `curl http://localhost:8000/api/v1/health`
- Получение списка клиентов: `curl http://localhost:8000/api/v1/clients`
- Просмотр последних предсказаний: `curl http://localhost:8000/api/v1/metrics/predictions/recent`
- Проверка SHAP: `curl http://localhost:8000/api/v1/clients/123/shap`
- Мониторинг логов: `tail -f logs/app.log`

## Основные API-эндпоинты
| Метод | Путь | Описание |
| --- | --- | --- |
| GET | `/api/v1/health` | Проверка статуса приложения и БД |
| GET | `/api/v1/clients` | Постраничный список клиентов с фильтрами |
| GET | `/api/v1/clients/{client_id}` | Детали клиента и признаки |
| GET | `/api/v1/clients/{client_id}/income` | Предсказанный доход и доверительный интервал |
| GET | `/api/v1/clients/{client_id}/shap` | Top-N вклад признаков (SHAP) с описаниями |
| GET | `/api/v1/clients/{client_id}/recommendations` | Банковские предложения и инсайты |
| GET | `/api/v1/metrics/model` | Текущие метрики модели и динамика |
| GET | `/api/v1/metrics/predictions/recent` | Последние предсказания и ошибки |
| GET | `/api/v1/metrics/shap` | Аггрегированные важности признаков |

Все схемы ответов описаны в `/docs` (Swagger UI) и `/redoc`.

## ML-артефакты
- `ML/hackathon_income_train.csv`, `ML/hackathon_income_test.csv` — обучающая и тестовая выборки.
- `ML/income_model_v3.cbm` — CatBoost-регрессор.
- `ML/model_meta.json` — полный список признаков и нормировок.
- `ML/metrics.json`, `ML/training_metrics.json` — оффлайн- и онлайновые метрики (RMSE, MAE, MAPE и т.д.).
- `ML/features_description.csv` — человеко-читаемые описания для вывода в frontend.

# Архитектура решения
```
Input Features  (~N признаков после очистки)
    └ данные train/test, признаки из features_description.csv

             ↓
┌───────────────────────────────────────────────┐
│ ЭТАП 0: Подготовка данных                    │
│   • чтение CSV (train/test/features)        │
│   • приведение типов (numeric-like → float) │
│   • обработка дат dt / period_last_act_ad   │
│   • генерация временных фич                 │
│   • дроп фичей с огромной долей NaN         │
│   • CatBoost-FI + дроп малоинформативных    │
└───────────────────────────────────────────────┘

             ↓
┌───────────────────────────────────────────────┐
│ ЭТАП 1: Работа с таргетом                    │
│   • расчёт квантилей 0.1% и 99.9%           │
│   • клиппинг таргета за пределами диапазона │
│   • бинарный флаг is_target_clipped         │
│   • лог-преобразование: y_log = log1p(y)    │
└───────────────────────────────────────────────┘

             ↓
┌───────────────────────────────────────────────┐
│ ЭТАП 2: Time-based CV (CatBoost, лог-таргет) │
│   • сортировка по дате dt                    │
│   • TimeSeriesSplit (5 фолдов)              │
│   • обучение CatBoostRegressor на log1p(y)  │
│   • OOF-предсказания в рублях               │
│   • метрики: WMAE, MAE, RMSE, MAPE, SMAPE   │
│   • разбор качества по квантилям таргета    │
└───────────────────────────────────────────────┘

             ↓
┌───────────────────────────────────────────────┐
│ ЭТАП 3: Holdout по времени                   │
│   • 85% старых дат → train                   │
│   • 15% свежих дат → holdout                │
│   • CatBoostRegressor (лог-таргет)          │
│   • LGBMRegressor (лог-таргет, те же фичи)  │
│   • holdout-предсказания двух моделей       │
└───────────────────────────────────────────────┘

             ↓
┌───────────────────────────────────────────────┐
│ ЭТАП 4: Ансамбль CatBoost + LGBM             │
│   • перебор alpha ∈ [0.0 … 1.0] с шагом 0.05 │
│   • blend_log = alpha * CB + (1-alpha) * LGBM│
│   • метрика WMAE в рублях на holdout        │
│   • выбор лучшего ENS_ALPHA_LOG             │
└───────────────────────────────────────────────┘

             ↓
┌───────────────────────────────────────────────┐
│ ЭТАП 5: Финальное обучение и сабмит          │
│   • переиспользуем обученные LOG-модели     │
│   • предикт ансамбля на тесте (лог-простран.)│
│   • обратное преобразование: expm1          │
│   • формируем submission_ens_log_time.csv   │
│   • сохраняем модели и метаданные           │
└───────────────────────────────────────────────┘

             ↓
Predicted Income (оценка дохода клиента)

```
