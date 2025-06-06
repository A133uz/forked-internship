# TF-IDF App (v1.1.0)
Докеризованное Django REST API для подсчета tf-idf показателей загруженного документа. Эта версия содержит важные изменения, включая документацию OpenAPI, поддержку Docker Compose и конфигурируемые переменные окружения.

---

## Структура проекта
- `testtask/` 
- `lesta_api/` — API
- `testapp/` — Основное приложение
- `urls.py` — Конфигурация URL
- `manage.py` — файл запуска Django CLI 
- `Dockerfile` — Определяет Docker образ
- `docker-compose.yml` — Конфигурация мульти-контейнера
- `.env` — Переменные окружения (не версионирована)
- `requirements.txt` — Python зависимости
- `README.md` — Документация проекта
- `changelog.md` — Список изменения версий 

---

## 🚀 Запуск приложения

### Необходимо

- Установленный Docker и Docker Compose на вашей машине

### Запуск с помощью Docker Compose

```bash
docker-compose up --build
 ```

### Локальный запуск
```bash
python -m venv venv
source venv/bin/activate # MacOS/Linux
venv/scripts/activate # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---
## Конфигурируемые параметры (.env)
 - `DEBUG`
 - `SECRET_KEY`
 - `DB_ENGINE`
 - `DB_NAME`
 - `DB_USER`
 - `DB_PASSWORD`
 - `DB_HOST`
 - `DB_PORT`
 - `ALLOWED_HOSTS`
---
## Эндпойнты
- `/status` возвращает { stauts : OK } если приложение работает исправно. Отсутствие ответа указывает на проблемы
- `/metrics` возвращает 4 метрики: максимальное время обработки (max_time_processed), минимальное время обработки (min_time_processed), среднее время обработки (avg_time_processed) и среднее кол-во слов в документе (avg_word_count)
-  `/version` возвращает текущую версию приложения в виде JSON
---
## Версия
Текущая - v1.1.0 
Предыдущая - v1.0.0
Изменения можно посмотреть [тут](./changelog.md)
       




    

