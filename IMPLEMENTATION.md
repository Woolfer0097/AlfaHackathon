# Реализация ML API для предсказания дохода клиентов

## Выполненные задачи

### 1. Схема БД
- ✅ Создана таблица `client_features` с динамическими колонками на основе `feature_cols` из `model_meta.json`
- ✅ Создана таблица `prediction_logs` для логирования предсказаний
- ✅ Настроено подключение к PostgreSQL через SQLAlchemy

### 2. Загрузка данных
- ✅ Создан скрипт `scripts/load_csv_to_db.py` для загрузки CSV в БД
- ✅ Поддержка кодировки windows-1251 для кириллицы
- ✅ Нормализация типов данных (строки, числа, булевы, категориальные)

### 3. ML сервис
- ✅ Интеграция CatBoost модели
- ✅ Загрузка модели при старте приложения
- ✅ Методы для предсказания дохода (`predict`)
- ✅ Методы для расчета SHAP значений (`get_shap_values`)

### 4. API эндпоинты
- ✅ `GET /api/v1/clients` - список клиентов с пагинацией и фильтрами
- ✅ `GET /api/v1/clients/{client_id}` - данные клиента
- ✅ `GET /api/v1/clients/{client_id}/income` - предсказание дохода
- ✅ `GET /api/v1/clients/{client_id}/shap` - SHAP объяснения
- ✅ `GET /api/v1/clients/{client_id}/recommendations` - рекомендации продуктов
- ✅ `GET /api/v1/metrics` - метрики модели (из metrics.json)

## Использование

### 1. Настройка БД
Установите PostgreSQL и настройте `DATABASE_URL` в `.env` или `app/core/config.py`:
```
database_url = "postgresql://user:password@localhost:5432/hackathon"
```

### 2. Загрузка данных
```bash
python scripts/load_csv_to_db.py --csv ML/hackathon_income_test.csv
```

### 3. Запуск приложения
```bash
uvicorn app.main:app --reload
```

### 4. Метрики
ML команда должна обновлять `ML/metrics.json` с метриками модели. API автоматически читает этот файл.

## Структура проекта

```
app/
  models/          # SQLAlchemy модели БД
  services/        # Бизнес-логика (ML, клиенты)
  api/v1/         # API эндпоинты
  schemas/         # Pydantic схемы
  core/           # Конфигурация, БД, логирование
scripts/           # Скрипты загрузки данных
ML/                # Модель и метаданные
```

## Зависимости
Все зависимости добавлены в `requirements.txt`:
- fastapi, uvicorn
- sqlalchemy, psycopg2-binary
- pandas
- catboost
- numpy, pydantic

