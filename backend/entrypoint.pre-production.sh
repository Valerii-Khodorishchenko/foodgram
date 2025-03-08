python manage.py makemigrations recipe
python manage.py migrate --no-input
sleep 5
python manage.py collectstatic --no-input
cp -r collected_static/. ../backend_static/backend_static/
python manage.py loaddata fixtures_db.json
gunicorn --bind 0.0.0.0:8000 backend.wsgi
