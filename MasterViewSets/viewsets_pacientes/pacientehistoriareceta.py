from MasterViewSets.universal import *

from MasterModels.modelos_pacientes import PacienteHistoriaReceta

from MasterSerializers.serializers_pacientes import PacienteHistoriaRecetaSerializer

class PacienteHistoriaRecetaViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = PacienteHistoriaReceta.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = PacienteHistoriaRecetaSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in PacienteHistoriaReceta._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = PacienteHistoriaReceta
    
    filterset_class = FilterClass