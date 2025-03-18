from MasterViewSets.universal import *

from MasterModels.modelos_profesionales import ProfesionalTelefono

from MasterSerializers.serializers_profesionales import ProfesionalTelefonoSerializer

class ProfesionalTelefonoViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = ProfesionalTelefono.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ProfesionalTelefonoSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in ProfesionalTelefono._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = ProfesionalTelefono
    
    filterset_class = FilterClass