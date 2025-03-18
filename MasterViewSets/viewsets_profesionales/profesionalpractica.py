from MasterViewSets.universal import *

from MasterModels.modelos_profesionales import ProfesionalPractica

from MasterSerializers.serializers_profesionales import ProfesionalPracticaSerializer

class ProfesionalPracticaViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = ProfesionalPractica.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ProfesionalPracticaSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in ProfesionalPractica._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = ProfesionalPractica
    
    filterset_class = FilterClass