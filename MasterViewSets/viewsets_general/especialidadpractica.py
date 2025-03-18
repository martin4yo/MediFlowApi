from MasterViewSets.universal import *

from MasterModels.modelos_general import EspecialidadPractica

from MasterSerializers.serializers_general import EspecialidadPracticaSerializer

class EspecialidadPracticaViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = EspecialidadPractica.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = EspecialidadPracticaSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in EspecialidadPractica._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = EspecialidadPractica
    
    filterset_class = FilterClass