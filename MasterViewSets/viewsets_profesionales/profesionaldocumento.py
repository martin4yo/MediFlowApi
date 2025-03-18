from MasterViewSets.universal import *

from MasterModels.modelos_profesionales import ProfesionalDocumento

from MasterSerializers.serializers_profesionales import ProfesionalDocumentoSerializer

class ProfesionalDocumentoViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = ProfesionalDocumento.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ProfesionalDocumentoSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in ProfesionalDocumento._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = ProfesionalDocumento
    
    filterset_class = FilterClass