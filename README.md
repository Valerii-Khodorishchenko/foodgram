# [Foodgram](https://fastfoodgram.sytes.net/)
![Workflow Badge](https://github.com/Valerii-Khodorishchenko/foodgram/actions/workflows/main.yml/badge.svg)


[![Django](https://img.shields.io/badge/Django-3.2.3-092E20?logo=django&logoColor=white)](https://docs.djangoproject.com/en/3.2/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker_compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![CI/CD](https://img.shields.io/badge/CI/CD-GitHub_Actions-2088FF?logo=github-actions&logoColor=white)](https://docs.github.com/en/actions)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.12.4-ff1709?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Djoser](https://img.shields.io/badge/Djoser-2.0.0-FCA121?logo=django&logoColor=white)](https://djoser.readthedocs.io/)
[![Flake8](https://img.shields.io/badge/Flake8-6.0.0-3776AB?logo=python&logoColor=white)](https://flake8.pycqa.org/)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-20.1.0-499848?logo=gunicorn&logoColor=white)](https://docs.gunicorn.org/)
[![Nginx](https://img.shields.io/badge/Nginx-1.25.4-009639?logo=nginx&logoColor=white)](https://nginx.org/)

**Foodgram** — это веб-сервис для публикации и обмена рецептами. Пользователи могут добавлять рецепты в избранное, подписываться на других авторов, а также формировать удобный список покупок на основе выбранных блюд. 

- [Описание](#foodgram)
- [Основные технологии](#основные-технологии)
- [Основной функционал](#основной-функционал)
- [Установка](#установка)
  - [Как заполнить .env](#как-заполнить-env) 
- [Запуск локально в режиме CORS](#запуск-локально-в-режиме-cors) (для разработки и тестирования)
  - [Запуск backend сервера Django](#запуск-backend-сервера-django)
  - [Запуск frontend сервера React](#запуск-frontend-сервера-react)
  - [Остановка, повторный запуск](#приложение-запущено)
- [Запуск локально Docker Compose с общими томами](#запуск-локально-docker-compose-с-общими-томами) (для разработки)
- [API Документация](https://fastfoodgram.sytes.net/api/docs/) 
- [Заполнение .db](#заполнение-db)
  - [Создание суперпользователя](#создание-суперпользователя)
  - [Заполнение .db ингридиентами из .CSV или .JSON файла](#заполнение-db-ингридиентами-из-csv-или-json-файла)
  - [Заполнение .db тегами из .CSV или .JSON файла](#заполнение-db-тегами-из-csv-или-json-файла)
  - [Загрузка фикстур](#загрузка-фикстур)
- [Запуск тестов](#запуск-тестов)
- [Запуск локально Docker Compose](#запуск-локально-docker-compose) (для проверки перед деплоем)
- [Деплой Docker-Compos](#деплой-docker-compos) 
- [Настройка CI/CD через Action GitHub](#настройка-cicd-через-action-github)

## Основные технологии
- **Бэкенд:** Django + Django REST Framework
- **Работа с ползователями** Djoser
- **Фронтенд:** React *(написан не мной)
- **База данных:** PostgreSQL
- **Запуск и проксирование** Gunicorn, Nginx
- **Контейнеризация:** Docker, Docker Compose  
- **CI/CD:** GitHub Actions (линтинг, деплой)
- <details>
  <summary>Еще технологии</summary>

    - Оптимизация: django-debug-toolbar 3.2.3 для анализа и
    оптимизации запросов 
    - drf_yasg, drf_spectacular для [статической](https://fastfoodgram.sytes.net/api/docs/) и [динамической](#приложение-запущено) спецификации API
    - Фильтрация: django-filter 2.4.0
    - Постоянное хранение: PostgreSQL через psycopg2-binary 2.9.3
    - Код-стайл: Flake8 6.0.0 для линтинга кода
    - Конфигурации: python-dotenv 1.0.1 для работы с переменными окружения
</details>

## Основной функционал
- Регистрация и аутентификация пользователей
- Публикация и редактирование рецептов
- Сохранение рецептов в избранное
- Формирование списка покупок
- Подписка на других пользователей

## Установка
>Пример всех команд приведён в ***bash sell***.

Клонируйте репозиторий любым удобным способом, например

```bash
git clone https://github.com/Valerii-Khodorishchenko/foodgram.git
```
Перейти в директорию с клонированым репозиторием.
```bash
cd foodgram
```
Cоздать и активировать виртуальное окружение.<br>
Для Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```
Для Windows:
```bash
py -3.9 -m venv venv
source venv/Scripts/activate
```
>Далее все команды будут представлены для Linux, чтобы они работали в Windows, 
необходимо ```python3``` заменить на ```py```.<br>

Обновить пакетный менеджер ```pip```.
```bash
python3 -m pip install --upgrade pip
```
Установить зависимости.
```bash
pip install -r backend/requirements.txt
```
Создать любым удобным для вас способом, а затем заполнить ```.env``` :
## Как заполнить .env
```bash
# Настройки Django
SECRET_KEY='your-secret-key'
DEBUG=True
ALLOWED_HOSTS=localhost 127.0.0.1 domain.name

# Настройки PostgreSQL
USE_POSTGRES_DB=True  # Если False, блок можно полностью пропустить
POSTGRES_DB=foodgram
POSTGRES_USER=user
POSTGRES_PASSWORD=password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432

# Для создания администратора (необязательный блок)
USERNAME='admin'  # Должн быть уникальным
FIRST_NAME='admin'
LAST_NAME='admin'
EMAIL='admin@gmail.com'  # Должн быть уникальным
PASSWORD='admin_password'
```
- `SECRET_KEY` — секретный ключ для Django. 
<br>Можно сгенерировать:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
- `DEBUG` — указывает, включен ли режим отладки `True`.
- `ALLOWED_HOSTS` — список разрешенных хостов (обязательно отделённых друг от друга пробелом). 
- `USE_POSTGRES_DB` — использовать PostgreSQL `True` или оставить SQLite `False`.
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` — параметры для
подключения к PostgreSQL.
- `DB_HOST`, `DB_PORT` — хост и порт базы данных.

Создать и открыть для заполнения .env можно командой:
```bash
nano .env
```

## Запуск локально в режиме CORS.
### Запуск backend сервера Django:

Выполнить миграции.
```bash
python3 backend/manage.py migrate
```
[**Загрузить фикстуры если необходима заполненная примерами БД**](загрузка-фикстур)

Запустить `backend` сервер.
```bash
python3 backend/manage.py runserver
```
### Запуск frontend сервера React:

Перейти в директорию `frontend/`.
```bash
cd frontend
```
Установить зависимости
```bash
npm install
```
Запустить `frontend` сервер.
```bash
npm run start
```
### Приложение запущено.
Далее приложение самостоятельно откроется в браузере по адресу 
[http://localhost:3000/recipes](http://localhost:3000/recipes) в режиме 
`frontend + backend`

Отдельно для просмотра `backend`-сервера доступны адреса:
- документация к API [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- админ панель [http://localhost:8000/admin/](http://localhost:8000/admin/)
- api [http://localhost:8000/api/](http://localhost:8000/api/)

Для работы над проектом доступна динамическая документация:
- swagger [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/api/swagger/)
- ReDoc [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)


Для остановки `backend`-сервера используйте сочетание клавиш `CTRL+C`

Для остановки `frontend`-сервера используйте сочетание клавиш `CTRL+C`

Для повторного запуска backend необходимо активировать виртуальное окружение и 
запустить сервер командами:
```bash
source venv/bin/activate
```
```bash
python3 backend/manage.py runserver
```
Для повторного запуска `frontend`-сервера необходимо 
- Перейти в директорию `frontend/`
- Запустить `frontend`-сервер.
```bash
npm run start
```
## Запуск локально Docker Compose с общими томами
Запустить Docker Compose командой
```bash
docker compose -f docker-compose.development.yml up --build
```
В этом варианте использования все изменения в проекте сразу попадут в контейнер.

Для остановки
```bash
docker compose -f docker-compose.development.yml down
```

## Заполнение .db
### Создание суперпользователя
Кроме стандартного способа создания суперпользователя(админа) в проекте есть 
возможность создать суперпользователя с помощью команды
```bash
bash superuser.sh
```

### Заполнение .db ингридиентами из .CSV или .JSON файла
В проекте реализована возможность добавления ингридиентов в базу данных 
без дублирования ингридиентов.
Команды для добавления:
```bash
python3 backend/manage.py load_ingredients data/ingredients.csv
```

```bash
python3 backend/manage.py load_ingredients data/ingredients.json
```
-  ```data``` путь к директории с файлами для заполнения ```.db``` 
формате ```.csv``` и ```.json```.

### Заполнение .db тегами из .CSV или .JSON файла
В проекте реализована возможность добавления тегов в базу данных 
без дублирования тегов.
Команды для добавления:
```bash
python3 backend/manage.py load_tags data/tags.csv
```

```bash
python3 backend/manage.py load_tags data/tags.json
```
-  ```data``` путь к директории с файлами для заполнения ```.db```
формате ```.csv``` и ```.json```.

В директории ```data/``` есть образцы файлов ```tags.csv``` и ```tags.json```.

### Загрузка фикстур
Заполненная примерами примерами:
```bash
python3 backend/manage.py loaddata backend/fixtures_db.json
```
Или без примеров, отдельно ингридиенты
```bash
backend/manage.py loaddata backend/ingredient_db.json
```
отдельно тенги:
```bash
backend/manage.py loaddata backend/tag_db.json
```

## Запуск тестов
Инструкция по запуску тестов расположена по ссылке

https://github.com/Valerii-Khodorishchenko/foodgram/blob/main/postman_collection/README.md

## Запуск локально Docker Compose
Для проверки работоспособности проекта перед отправкой на удалённый сервер запустите проект локально
```bash
docker compose -f docker-compose.pre-production.yml up --build
```
Для остановки
```bash
docker compose -f docker-compose.pre-production.yml down
```
## Деплой Docker-Compos
Для сборки собственных образов необходимо иметь аккаунт на https://hub.docker.com/
Сборка собственных образов и отправка на `dockerhub`
```bash
cd backend
docker build --target production -t docker_username/foodgram_backend:production
docker push docker_username/foodgram_backend:production

cd ../frontend
docker build docker_username/foodgram_frontend
docker push docker_username/foodgram_frontend

cd ../gateway
docker build docker_username/foodgram_gateway
docker push docker_username/foodgram_gateway
```

Измените названия образов на собственные в `docker-compose.pre-production.yml` и можно его отправить на ваш удалённый сервер любым удобным образом. В директории с `docker-compose.pre-production.yml` необходимо создать [`.env`](#как-заполнить-env)

## Настройка CI/CD через Action GitHub
Необходимо в репозитории проекта перейти

` Settings -> Security -> Secrets and variable -> Actions -> Secrets`
и создать Secrets
```bash
HOST              # IP-адрес вашего сервера
USER              # имя пользователя сервера
SSH_KEY           # закрытый SSH-ключ
SSH_PASSPHRASE    # (парольная фраза) для SSH-ключа
DOCKER_PASSWORD   # пароль docker
DOCKER_USERNAME   # имя пользователя docker
TELEGRAM_TO       # ID телеграм-аккаунта
TELEGRAM_TOKEN    # токен бота отправляющего сообщение
```
