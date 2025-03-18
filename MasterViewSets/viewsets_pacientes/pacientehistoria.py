from MasterViewSets.universal import *

from MasterModels.modelos_pacientes import PacienteHistoria

from MasterSerializers.serializers_pacientes import PacienteHistoriaSerializer

class PacienteHistoriaViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = PacienteHistoria.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = PacienteHistoriaSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in PacienteHistoria._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = PacienteHistoria
    
    filterset_class = FilterClass