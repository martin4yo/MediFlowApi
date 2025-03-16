from MasterViewSets.universal import *

from MasterModels.modelos_general import Practica

from MasterSerializers.serializers_general import PracticaSerializer

class PracticaViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = Practica.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = PracticaSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in Practica._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = Practica
    
    filterset_class = FilterClass