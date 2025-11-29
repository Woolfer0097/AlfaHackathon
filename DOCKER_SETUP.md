# Docker Setup Guide

## Быстрый старт

### 1. Загрузка данных в БД (перед запуском Docker)

```bash
# Создать и активировать venv
python3 -m venv venv
source venv/bin/activate.fish  # для fish
# или source venv/bin/activate  # для bash

# Установить зависимости
pip install -r requirements.txt

# Загрузить данные
python scripts/load_csv_to_db.py --csv ML/hackathon_income_test.csv --drop-table
```

**Важно**: Убедитесь, что PostgreSQL запущен и доступен на `localhost:5432` перед загрузкой данных.

### 2. Запуск через Docker Compose

```bash
# Собрать и запустить все сервисы
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

### 3. Доступ к сервисам

После запуска все сервисы будут доступны:

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/v1
- **API Docs (Swagger)**: http://localhost/docs
- **API Docs (ReDoc)**: http://localhost/redoc
- **PostgreSQL**: localhost:5432 (user: postgres, password: postgres, db: hackathon)

## Структура сервисов

1. **postgres** - PostgreSQL база данных
2. **app** - FastAPI backend приложение
3. **frontend** - React frontend (собирается в Docker)
4. **nginx** - Web сервер, проксирует запросы к API и отдает статику frontend

## Переменные окружения

Backend читает переменные из `.env` файла или из environment variables в docker-compose.yml.

Frontend использует `VITE_API_BASE_URL` при сборке (передается через build args).

## Troubleshooting

### Проблема: Frontend не подключается к API

Проверьте:
1. Что `VITE_API_BASE_URL` правильно установлен при сборке frontend
2. Что nginx правильно проксирует `/api/` запросы
3. Что backend доступен на `app:8000` внутри Docker сети

### Проблема: База данных не подключается

Проверьте:
1. Что `DATABASE_URL` в docker-compose.yml указывает на `postgres:5432` (не localhost!)
2. Что PostgreSQL контейнер запущен и здоров
3. Что данные загружены в БД

### Проблема: Модель не загружается

Проверьте:
1. Что папка `ML/` смонтирована в контейнер (volume в docker-compose.yml)
2. Что файлы модели существуют: `ML/catboost_income_model.cbm`, `ML/model_meta.json`

## Остановка сервисов

```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить volumes (удалит данные БД!)
docker-compose down -v
```

