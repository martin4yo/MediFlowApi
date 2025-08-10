from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from datetime import datetime

from MasterModels.modelos_turnos.excepcionagenda import ExcepcionAgenda
from MasterSerializers.serializers_turnos.excepcionagenda import ExcepcionAgendaSerializer, ExcepcionAgendaDetailSerializer

class ExcepcionAgendaViewSet(viewsets.ModelViewSet):
    queryset = ExcepcionAgenda.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'idprofesional', 'idcentro', 'tipo', 'afecta_centro_completo', 'disabled'
    ]
    ordering_fields = ['id', 'fecha_inicio', 'fecha_fin', 'created_at']
    ordering = ['fecha_inicio']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ExcepcionAgendaDetailSerializer
        return ExcepcionAgendaSerializer

    @action(detail=False, methods=['get'])
    def por_periodo(self, request):
        """Obtiene excepciones en un período específico"""
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        profesional_id = request.query_params.get('profesional_id')
        centro_id = request.query_params.get('centro_id')

        if not all([fecha_inicio, fecha_fin]):
            return Response(
                {"error": "Faltan parámetros: fecha_inicio, fecha_fin"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filtrar excepciones que se superponen con el período solicitado
        excepciones = self.get_queryset().filter(
            fecha_inicio__lte=fecha_fin,
            fecha_fin__gte=fecha_inicio
        )

        if profesional_id:
            excepciones = excepciones.filter(idprofesional_id=profesional_id)
        
        if centro_id:
            excepciones = excepciones.filter(
                models.Q(idcentro_id=centro_id) |
                models.Q(afecta_centro_completo=True)
            )

        serializer = self.get_serializer(excepciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def feriados(self, request):
        """Obtiene solo los feriados"""
        excepciones = self.get_queryset().filter(tipo='FERIADO')
        serializer = self.get_serializer(excepciones, many=True)
        return Response(serializer.data)