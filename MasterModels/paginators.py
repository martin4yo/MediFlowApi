from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_page_size(self, request):
        page_size = super().get_page_size(request)
        if page_size is not None and page_size < 1:
            raise ValidationError({'page_size': 'El tamaño de página debe ser mayor a 0.'})
        return page_size
