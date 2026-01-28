from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class BootstrapTablePagination(LimitOffsetPagination):
    default_limit = 20

    def get_paginated_response(self, data):
        return Response({
            'total': self.count,
            'rows': data,
        })
