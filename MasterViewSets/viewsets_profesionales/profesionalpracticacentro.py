from MasterViewSets.universal import *

from MasterModels.modelos_profesionales import ProfesionalPracticaCentro

from MasterSerializers.serializers_profesionales import ProfesionalPracticaCentroSerializer

class ProfesionalPracticaCentroViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = ProfesionalPracticaCentro.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ProfesionalPracticaCentroSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in ProfesionalPracticaCentro._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = ProfesionalPracticaCentro
    
    filterset_class = FilterClass