from MasterViewSets.universal import *

from MasterModels.modelos_general import Genero

from MasterSerializers.serializers_general import GeneroSerializer

class GeneroViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = Genero.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = GeneroSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in Genero._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = Genero
    
    filterset_class = FilterClass