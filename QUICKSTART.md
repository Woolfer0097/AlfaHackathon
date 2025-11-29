# Quick Start Guide

## Шаг 1: Загрузка данных в БД

```bash
# Активировать venv
source venv/bin/activate.fish  # или source venv/bin/activate для bash

# Загрузить CSV в БД (убедитесь, что PostgreSQL запущен)
python scripts/load_csv_to_db.py --csv ML/hackathon_income_test.csv --drop-table
```

## Шаг 2: Запуск через Docker

### Вариант A: Сборка frontend в Docker (рекомендуется)

```bash
# Собрать и запустить все сервисы
docker-compose up --build -d

# Проверить статус
docker-compose ps

# Посмотреть логи
docker-compose logs -f
```

**Если возникают проблемы с сетью при установке npm пакетов:**
- Dockerfile уже настроен с retry логикой
- Попробуйте запустить еще раз: `docker-compose build frontend --no-cache`

### Вариант B: Использовать предсобранный frontend

```bash
# Собрать frontend локально
cd frontend
npm install
VITE_API_BASE_URL=/api/v1 npm run build
cd ..

# Запустить без сборки frontend в Docker
docker-compose -f docker-compose.local.yml up --build -d
```

## Шаг 3: Доступ к приложению

- **Frontend**: http://localhost
- **API**: http://localhost/api/v1
- **API Docs**: http://localhost/docs

## Остановка

```bash
docker-compose down
```

## Полезные команды

```bash
# Пересобрать конкретный сервис
docker-compose build app
docker-compose up -d app

# Посмотреть логи конкретного сервиса
docker-compose logs -f app

# Выполнить команду в контейнере
docker-compose exec app python scripts/load_csv_to_db.py --csv ML/hackathon_income_test.csv --drop-table
```

