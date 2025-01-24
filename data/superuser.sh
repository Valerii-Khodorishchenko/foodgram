#!/bin/bash

case "$OSTYPE" in
    msys*)    python=python ;;
    cygwin*)  python=python ;;
    *)        python=python3 ;;
esac

PATH_TO_MANAGE_PY=$(find -name "manage.py" -not -path "*/env" -not -path "*/venv" -not -path "*/.git");
BASE_DIR="$(dirname "${PATH_TO_MANAGE_PY}")";

echo "Ищем .env в директории: $(pwd)"

status=$?;
if [ $status -ne 0 ]; then
    echo "Запускай из директории проекта";
    exit $status;
fi


if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env файл не найден!";
    exit 1;
fi

cd $BASE_DIR
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='$USERNAME').exists():
    User.objects.create_superuser(username='$USERNAME', email='$EMAIL', password='$PASSWORD', first_name='$FIRST_NAME', last_name='$LAST_NAME');
    print('Суперпользователь успешно создан.');
else:
    print('Суперпользователь уже существует.');
"
