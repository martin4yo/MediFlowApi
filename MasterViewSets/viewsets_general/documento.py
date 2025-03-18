from MasterViewSets.universal import *

from MasterModels.modelos_general import Documento

from MasterSerializers.serializers_general import DocumentoSerializer

class DocumentoViewSet(GenericModelViewSet):
    """
    ViewSet de Modulos
    """
    queryset = Documento.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = DocumentoSerializer

    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]

     # Habilitar todos los campos para ordenamiento
    ordering_fields = [field.name for field in Documento._meta.fields]
    ordering = ['id']  # Orden por defecto (clave primaria)
    
    class FilterClass(DynamicModelFilter):
        class Meta(DynamicModelFilter.Meta):
            model = Documento
    
    filterset_class = FilterClass