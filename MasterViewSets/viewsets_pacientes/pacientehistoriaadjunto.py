from MasterViewSets.universal import *

from MasterModels.modelos_pacientes import PacienteHistoriaAdjunto

from MasterSerializers.serializers_pacientes import PacienteHistoriaAdjuntoSerializer

class PacienteHistoriaAdjuntoViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = PacienteHistoriaAdjunto.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = PacienteHistoriaAdjuntoSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in PacienteHistoriaAdjunto._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = PacienteHistoriaAdjunto
    
    filterset_class = FilterClass