from MasterViewSets.universal import *

from MasterModels.modelos_general import Centro

from MasterSerializers.serializers_general import CentroSerializer

class CentroViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = Centro.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = CentroSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in Centro._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = Centro
    
    filterset_class = FilterClass