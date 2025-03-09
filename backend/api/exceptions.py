from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.views import exception_handler


def not_found(exc, context):
    if isinstance(exc, (Http404, NotFound)):
        response = exception_handler(exc, (Http404, NotFound))
        response.data = {'detail': 'Страница не найдена.'}
        return response
    return exception_handler(exc, context)
