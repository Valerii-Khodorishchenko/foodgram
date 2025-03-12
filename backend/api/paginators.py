from django.conf import settings
from rest_framework.pagination import BasePagination
from rest_framework.response import Response


class LimitPagePagination(BasePagination):
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE', 10)

    def paginate_queryset(self, queryset, request, view=None):
        try:
            page = int(request.query_params.get('page', None))
        except (ValueError, TypeError):
            page = 1
        try:
            limit = int(request.query_params.get('limit', None))
        except (ValueError, TypeError):
            limit = self.page_size
        offset = (page - 1) * limit
        self.request = request
        self.count = queryset.count()
        self.page = page
        self.page_size = limit
        return queryset[offset:offset + limit]

    def get_paginated_response(self, data):
        return Response({
            'count': self.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

    def get_next_link(self):
        if self.page * self.page_size < self.count:
            return self.get_url(self.page + 1)
        return None

    def get_previous_link(self):
        return self.get_url(self.page - 1) if self.page > 1 else None

    def get_url(self, page):
        return (
            self.request.build_absolute_uri(self.request.path)
            + f'?page={page}&limit={self.page_size}'
        )
