from MasterViewSets.universal import *

from MasterModels.modelos_pacientes import Paciente

from MasterSerializers.serializers_pacientes import PacienteSerializer

class PacienteViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = Paciente.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = PacienteSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in Paciente._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = Paciente
    
    filterset_class = FilterClass