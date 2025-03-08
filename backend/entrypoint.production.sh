python manage.py collectstatic --no-input
cp -r collected_static/. ../backend_static/backend_static/
gunicorn --bind 0.0.0.0:8000 backend.wsgi
