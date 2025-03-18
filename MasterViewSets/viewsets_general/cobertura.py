from MasterViewSets.universal import *

from MasterModels.modelos_general import Cobertura

from MasterSerializers.serializers_general import CoberturaSerializer

class CoberturaViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = Cobertura.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = CoberturaSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in Cobertura._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = Cobertura
    
    filterset_class = FilterClass