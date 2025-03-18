from MasterViewSets.universal import *

from MasterModels.modelos_pacientes import PacienteTelefono

from MasterSerializers.serializers_pacientes import PacienteTelefonoSerializer

class PacienteTelefonoViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = PacienteTelefono.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = PacienteTelefonoSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in PacienteTelefono._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = PacienteTelefono
    
    filterset_class = FilterClass