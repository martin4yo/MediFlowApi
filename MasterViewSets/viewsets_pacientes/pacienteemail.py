from MasterViewSets.universal import *

from MasterModels.modelos_pacientes import PacienteEmail

from MasterSerializers.serializers_pacientes import PacienteEmailSerializer

class PacienteEmailViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = PacienteEmail.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = PacienteEmailSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in PacienteEmail._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = PacienteEmail
    
    filterset_class = FilterClass