# TF-IDF App (v2.0.0)
Докеризованное Django REST API для подсчёта tf-idf показателей загруженного документа с расширенной системой управления документами и пользователями. Эта версия включает:

- Новый механизм работы с документами и коллекциями, доступный через API
- Пользовательскую регистрацию, авторизацию и управление сессиями
- Подсчёт статистики по документам и коллекциям
- Полную OpenAPI-документацию
- Поддержку Docker Compose и конфигурируемые переменные окружения

---

## 📁 Структура проекта

- `testtask/`  
- `lesta_api/` — API  
- `testapp/` — Основное приложение  
- `urls.py` — Конфигурация URL  
- `manage.py` — Запуск Django CLI  
- `Dockerfile` — Определение Docker образа  
- `docker-compose.yml` — Конфигурация мультиконтейнерного окружения  
- `.env` — Переменные окружения (не включаются в репозиторий)  
- `requirements.txt` — Python-зависимости  
- `README.md` — Документация проекта  
- `changelog.md` — Журнал изменений  

---

## 📁 Структура таблиц
![image](https://github.com/user-attachments/assets/d7322300-3c15-48fd-ab08-fbcf867a4dd1)


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
- `GET /status` возвращает { stauts : OK } если приложение работает исправно. Отсутствие ответа указывает на проблемы
- `GET /metrics` возвращает 4 метрики: максимальное время обработки (max_time_processed), минимальное время обработки (min_time_processed), среднее время обработки (avg_time_processed) и среднее кол-во слов в документе (avg_word_count)
- `GET /version` возвращает текущую версию приложения в виде JSON
- `POST /register` — регистрация нового аккаунта
- `POST /login` — вход в аккаунт
- `POST /logout` — выход из аккаунта
###  **Для зарегистрированных пользователей**
- `GET /documents/` – Получить список документов   
- `GET /documents/<document_id>` – Получить содержимого документа
- `GET /documents/<document_id>/statistics` — получить статистику по данному документу 
- `DELETE /documents/<document_id>` — получить статистику по данному документу
- `GET /collections/` – получить список коллекций с id и списком входящих в них документов
- `GET /collections/<collection_id>` - получить список id документов, входящих в конкретную коллекцию
- `GET /collections/<collection_id>/statistics` -  получить статистику по коллекции
- `POST /collection/<collection_id>/<document_id>` - добавить документ в коллекцию
- `DELETE /collection/<collection_id>/<document_id>` - удалить документ из коллекции
- `PATCH /user/<user_id>` -  изменение пароля, переданного в теле запроса
- `DELETE /user/<user_id>` - удаление аккаунта. При удалении удаляются все файлы и коллекции аккаунта
---

# 📦 Версии
- Текущая: v2.0.0

- Предыдущая: v1.0.0 (Alpha)
---
Изменения можно посмотреть [тут](./changelog.md)
       




    

