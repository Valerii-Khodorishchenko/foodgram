Находясь в папке infra, выполните команду docker-compose up. При выполнении 
этой команды контейнер frontend, описанный в docker-compose.yml, подготовит 
файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою 
работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу 
http://localhost/api/docs/ — спецификацию API.

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
- `USE_POSTGRES_DB` — использовать PostgreSQL или оставить SQLite
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` — параметры для
подключения к PostgreSQL.
- `DB_HOST`, `DB_PORT` — хост и порт базы данных.

Создать и открыть для заполнения .env можно командой:
```bash
nano .env
```

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
