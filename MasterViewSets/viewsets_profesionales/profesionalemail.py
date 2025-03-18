from MasterViewSets.universal import *

from MasterModels.modelos_profesionales import ProfesionalEmail

from MasterSerializers.serializers_profesionales import ProfesionalEmailSerializer

class ProfesionalEmailViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = ProfesionalEmail.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ProfesionalEmailSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in ProfesionalEmail._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = ProfesionalEmail
    
    filterset_class = FilterClass