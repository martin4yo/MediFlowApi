from MasterViewSets.universal import *

from MasterModels.modelos_general import Persona

from MasterSerializers.serializers_general import PersonaSerializer

class PersonaViewSet(GenericModelViewSet):
    """
    ViewSet de Personas
    """
    serializer_class = PersonaSerializer
    
    queryset = Persona.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in Persona._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = Persona
    
    filterset_class = FilterClass