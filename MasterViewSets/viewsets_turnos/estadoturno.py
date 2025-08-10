from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from MasterModels.modelos_turnos.estadoturno import EstadoTurno
from MasterSerializers.serializers_turnos.estadoturno import EstadoTurnoSerializer

class EstadoTurnoViewSet(viewsets.ModelViewSet):
    queryset = EstadoTurno.objects.all()
    serializer_class = EstadoTurnoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['codigo', 'nombre', 'disabled']
    ordering_fields = ['id', 'codigo', 'nombre', 'created_at']
    ordering = ['codigo']