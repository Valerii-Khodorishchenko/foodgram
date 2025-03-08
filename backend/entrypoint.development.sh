python manage.py collectstatic
cp -r /temporary_media/. /app/media
rm -rf /temporary_media
python manage.py runserver 0.0.0.0:8000
