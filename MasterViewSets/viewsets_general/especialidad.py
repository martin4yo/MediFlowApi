from MasterViewSets.universal import *

from MasterModels.modelos_general import Especialidad

from MasterSerializers.serializers_general import EspecialidadSerializer

class EspecialidadViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = Especialidad.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = EspecialidadSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in Especialidad._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = Especialidad
    
    filterset_class = FilterClass