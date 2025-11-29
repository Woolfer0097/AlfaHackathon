# Альфа-Банк ML Hackathon - Income Prediction API

Система для предсказания дохода клиентов на основе ML модели CatBoost.

## Архитектура

- **Backend**: FastAPI + SQLAlchemy + CatBoost
- **Frontend**: React + TypeScript + Material-UI
- **Database**: PostgreSQL
- **Web Server**: Nginx

## Быстрый старт

### 1. Загрузка данных в БД

```bash
# Активировать venv (если используете)
source venv/bin/activate.fish  # для fish shell
# или
source venv/bin/activate  # для bash

# Загрузить CSV в БД
python scripts/load_csv_to_db.py --csv ML/hackathon_income_test.csv --drop-table
```

### 2. Запуск через Docker Compose

```bash
# Собрать и запустить все сервисы
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

Сервисы будут доступны:
- Frontend: http://localhost
- Backend API: http://localhost/api/v1
- API Docs: http://localhost/docs
- PostgreSQL: localhost:5432

### 3. Локальная разработка

#### Backend

```bash
# Установить зависимости
pip install -r requirements.txt

# Настроить .env (скопировать из .env.example)
cp .env.example .env

# Запустить сервер
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Установить зависимости
npm install

# Настроить .env
cp .env.example .env

# Запустить dev сервер
npm run dev
```

## Структура проекта

```
.
├── app/                    # Backend приложение
│   ├── api/v1/            # API эндпоинты
│   ├── core/              # Конфигурация, БД, логирование
│   ├── models/            # SQLAlchemy модели
│   ├── schemas/           # Pydantic схемы
│   └── services/          # Бизнес-логика (ML, клиенты)
├── frontend/              # React приложение
├── ML/                    # ML модель и данные
│   ├── catboost_income_model.cbm
│   ├── model_meta.json
│   ├── metrics.json
│   └── hackathon_income_test.csv
├── scripts/               # Скрипты загрузки данных
├── nginx/                 # Nginx конфигурация
└── docker-compose.yml     # Docker Compose конфигурация
```

## API Эндпоинты

- `GET /api/v1/health` - проверка здоровья сервиса
- `GET /api/v1/clients` - список клиентов (с пагинацией)
- `GET /api/v1/clients/{id}` - данные клиента
- `GET /api/v1/clients/{id}/income` - предсказание дохода
- `GET /api/v1/clients/{id}/shap` - SHAP объяснения
- `GET /api/v1/clients/{id}/recommendations` - рекомендации продуктов
- `GET /api/v1/metrics` - метрики модели

## Переменные окружения

См. `.env.example` для примера конфигурации.

## Примечания

- CSV файлы должны быть в кодировке windows-1251
- Модель и метаданные находятся в папке `ML/`
- Метрики модели обновляются ML командой в `ML/metrics.json`
