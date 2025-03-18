from MasterViewSets.universal import *

from MasterModels.modelos_general import CoberturaPlan

from MasterSerializers.serializers_general import CoberturaPlanSerializer

class CoberturaPlanViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = CoberturaPlan.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = CoberturaPlanSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in CoberturaPlan._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = CoberturaPlan
    
    filterset_class = FilterClass