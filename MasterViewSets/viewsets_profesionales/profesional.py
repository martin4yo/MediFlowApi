from MasterViewSets.universal import *

from MasterModels.modelos_profesionales import Profesional

from MasterSerializers.serializers_profesionales import ProfesionalSerializer

class ProfesionalViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = Profesional.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ProfesionalSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in Profesional._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = Profesional
    
    filterset_class = FilterClass