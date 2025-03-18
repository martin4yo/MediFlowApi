from MasterViewSets.universal import *

from MasterModels.modelos_general import PracticaPlan

from MasterSerializers.serializers_general import PracticaPlanSerializer

class PracticaPlanViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = PracticaPlan.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = PracticaPlanSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in PracticaPlan._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = PracticaPlan
    
    filterset_class = FilterClass