"""
Api de MasterModels
"""
from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from MasterModels.paginators import CustomPagination
from MasterModels.filters import DynamicModelFilter

### VIEWSET BASE #######################################

class GenericModelViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_class = DynamicModelFilter

    def get_queryset(self):
        # Obtener el modelo desde el serializer para definir el queryset
        model = self.serializer_class.Meta.model
        return model.objects.all()

    def get_filterset_class(self):
        # Establece el modelo en el Meta de DynamicModelFilter
        class CustomFilter(DynamicModelFilter):
            class Meta(DynamicModelFilter.Meta):
                model = self.serializer_class.Meta.model
        return CustomFilter













































