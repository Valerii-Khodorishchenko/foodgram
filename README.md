# Запуск backend, frontend серверов в режиме CORS.

Пример всех команд приведён в ***bash sell***.

1. Форкнуть репозиторий.
2. Клонировать репозиторий любым удобным способом, например:
```bash
git clone https://github.com/yourusername/foodgram.git
# yourusername - имя вашего аккаунта на GitHub
```
3. Перейти в директорию с клонированым репозиторием.
```bash
cd foodgram
```
4. Создать любым удобным для вас способом, а затем заполнить ```.env``` :
### Как заполнить ```.env``` :
```nano
SECRET_KEY='your-secret-key'
DEBUG=True
ALLOWED_HOSTS=localhost 127.0.0.1 domain.name

USE_POSTGRES_DB=True
POSTGRES_DB=foodgram
POSTGRES_USER=user
POSTGRES_PASSWORD=password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
```
- `SECRET_KEY` — секретный ключ для Django.
- `DEBUG` — указывает, включен ли режим отладки.
- `ALLOWED_HOSTS` — список разрешенных хостов.
- `USE_POSTGRES_DB` — использовать PostgreSQL или оставить SQLite.
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` — параметры для
подключения к PostgreSQL.
- `DB_HOST`, `DB_PORT` — хост и порт базы данных.

Создать и открыть для заполнения .env можно командой:
```bash
nano .env
```
### 5. Запуск backend сервера:
 - Cоздать и активировать виртуальное окружение.
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
Далее все команды будут представлены для Linux, чтобы они работали в Windows, 
необходимо ```python3``` заменить на ```py```.
- Обновить пакетный менеджер ```pip```.
```bash
python3 -m pip install --upgrade pip
```
- Установить зависимости.
```bash
pip install -r backend/requirements.txt
```
- Выполнить миграции.
```bash
python3 backend/manage.py migrate
```
- Запустить сервер.
```bash
python3 backend/manage.py runserver
```

### 6. Запуск frontend сервера:

- Перейти в директорию ```frontend/```.
``` bash
cd frontend
```
- Запустить ```frontend``` сервер.
```bash
npm run start
```
### Приложение запущено.
Далее приложение самостоятельно откроется в браузере по адресу 
http://localhost:3000/recipes в режиме ```frontend + backend```

Отдельно для просмотра ```backend``` сервера доступны адреса:
- админ панель http://localhost:8000/admin/
- api http://localhost:8000/api/

Для остановки ```backend``` сервера используйте сочетание клавиш ```CTRL+C```

Для остановки ```frontend``` сервера используйте сочетание клавиш ```CTRL+C```

Для повторного запуска backend необходимо активировать виртуальное окружение и 
запустить сервер командами:
```bash
source venv/bin/activate
```
```bash
python3 backend/manage.py runserver
```
Для повторного запуска ```frontend``` сервера необходимо повторить пункт №6


### Как заполнить db ингридиентами из .CSV или .JSON файла
В проекте реализована возможность добавления ингридиентов в базу данных 
без дублирования ингридиентов.
Команды для добавления:
```bash
python manage.py load_ingredients path_to_file/ingredients.csv
```

```bash
python manage.py load_ingredients path_to_file/ingredients.json
```
-  ```path_to_file``` путь к директории с файлами для заполнения db формате
```.csv``` и ```.json```

# Просмотр спецификации API и frontend веб-приложения
Находясь в папке infra, выполните команду docker-compose up. При выполнении 
этой команды контейнер frontend, описанный в docker-compose.yml, подготовит 
файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою 
работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу 
http://localhost/api/docs/ — спецификацию API.