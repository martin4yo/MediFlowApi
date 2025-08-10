from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta

from MasterModels.modelos_turnos.turno import Turno
from MasterSerializers.serializers_turnos.turno import TurnoSerializer, TurnoDetailSerializer, TurnoCreateSerializer

class TurnoViewSet(viewsets.ModelViewSet):
    queryset = Turno.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'idpaciente', 'idprofesional', 'idcentro', 'idespecialidadpractica',
        'idestadoturno', 'fecha', 'es_particular', 'disabled'
    ]
    ordering_fields = ['id', 'fecha', 'hora', 'created_at']
    ordering = ['fecha', 'hora']

    def get_serializer_class(self):
        if self.action == 'create':
            return TurnoCreateSerializer
        elif self.action == 'retrieve':
            return TurnoDetailSerializer
        return TurnoSerializer

    def perform_create(self, serializer):
        """Al crear un turno, establecer estado inicial y calcular duración"""
        from MasterModels.modelos_turnos.estadoturno import EstadoTurno
        
        estado_solicitado = EstadoTurno.objects.filter(codigo='SOLICITADO').first()
        if not estado_solicitado:
            # Crear estado por defecto si no existe
            estado_solicitado = EstadoTurno.objects.create(
                codigo='SOLICITADO',
                nombre='Solicitado',
                descripcion='Turno solicitado pendiente de confirmación',
                color='#FCD34D'  # Amarillo
            )
        
        # Obtener duración de la práctica
        especialidad_practica = serializer.validated_data['idespecialidadpractica']
        duracion = especialidad_practica.idpractica.duracion_estimada_minutos or 30
        
        serializer.save(
            idestadoturno=estado_solicitado,
            duracion_minutos=duracion,
            fecha_solicitud=timezone.now()
        )

    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """Confirma un turno"""
        turno = self.get_object()
        
        if turno.idestadoturno.codigo != 'SOLICITADO':
            return Response(
                {"error": "Solo se pueden confirmar turnos en estado SOLICITADO"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from MasterModels.modelos_turnos.estadoturno import EstadoTurno
        estado_confirmado = EstadoTurno.objects.filter(codigo='CONFIRMADO').first()
        
        if not estado_confirmado:
            return Response(
                {"error": "Estado CONFIRMADO no existe en el sistema"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        turno.idestadoturno = estado_confirmado
        turno.fecha_confirmacion = timezone.now()
        turno.save()
        
        # TODO: Enviar email de confirmación al paciente
        
        serializer = self.get_serializer(turno)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancela un turno"""
        turno = self.get_object()
        
        if not turno.puede_cancelar:
            return Response(
                {"error": "Este turno no puede ser cancelado en su estado actual"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from MasterModels.modelos_turnos.estadoturno import EstadoTurno
        estado_cancelado = EstadoTurno.objects.filter(codigo='CANCELADO').first()
        
        if not estado_cancelado:
            return Response(
                {"error": "Estado CANCELADO no existe en el sistema"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        motivo = request.data.get('motivo', '')
        turno.idestadoturno = estado_cancelado
        turno.fecha_cancelacion = timezone.now()
        turno.observaciones_recepcion = f"Cancelado: {motivo}"
        turno.save()
        
        serializer = self.get_serializer(turno)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def marcar_presente(self, request, pk=None):
        """Marca al paciente como presente (en espera)"""
        turno = self.get_object()
        
        from MasterModels.modelos_turnos.estadoturno import EstadoTurno
        estado_espera = EstadoTurno.objects.filter(codigo='EN_ESPERA').first()
        
        if not estado_espera:
            return Response(
                {"error": "Estado EN_ESPERA no existe en el sistema"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        turno.idestadoturno = estado_espera
        turno.fecha_llegada = timezone.now()
        turno.save()
        
        serializer = self.get_serializer(turno)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def iniciar_atencion(self, request, pk=None):
        """Inicia la atención del turno"""
        turno = self.get_object()
        
        from MasterModels.modelos_turnos.estadoturno import EstadoTurno
        estado_atencion = EstadoTurno.objects.filter(codigo='EN_ATENCION').first()
        
        if not estado_atencion:
            return Response(
                {"error": "Estado EN_ATENCION no existe en el sistema"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        turno.idestadoturno = estado_atencion
        turno.fecha_inicio_atencion = timezone.now()
        turno.save()
        
        serializer = self.get_serializer(turno)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def finalizar_atencion(self, request, pk=None):
        """Finaliza la atención del turno"""
        turno = self.get_object()
        
        if turno.idestadoturno.codigo != 'EN_ATENCION':
            return Response(
                {"error": "Solo se pueden finalizar turnos EN_ATENCION"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from MasterModels.modelos_turnos.estadoturno import EstadoTurno
        estado_atendido = EstadoTurno.objects.filter(codigo='ATENDIDO').first()
        
        if not estado_atendido:
            return Response(
                {"error": "Estado ATENDIDO no existe en el sistema"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        observaciones = request.data.get('observaciones_profesional', '')
        turno.idestadoturno = estado_atendido
        turno.fecha_fin_atencion = timezone.now()
        turno.observaciones_profesional = observaciones
        turno.save()
        
        serializer = self.get_serializer(turno)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def agenda_dia(self, request):
        """Obtiene la agenda del día para un centro específico"""
        centro_id = request.query_params.get('centro_id')
        fecha = request.query_params.get('fecha', timezone.now().date().strftime('%Y-%m-%d'))
        
        if not centro_id:
            return Response(
                {"error": "Falta parámetro: centro_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        turnos = self.get_queryset().filter(
            idcentro_id=centro_id,
            fecha=fecha
        ).exclude(idestadoturno__codigo='CANCELADO').order_by('hora')
        
        serializer = self.get_serializer(turnos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_paciente(self, request):
        """Obtiene todos los turnos de un paciente"""
        paciente_id = request.query_params.get('paciente_id')
        if not paciente_id:
            return Response(
                {"error": "Falta parámetro: paciente_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        turnos = self.get_queryset().filter(idpaciente_id=paciente_id).order_by('-fecha', '-hora')
        serializer = self.get_serializer(turnos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_profesional(self, request):
        """Obtiene todos los turnos de un profesional"""
        profesional_id = request.query_params.get('profesional_id')
        fecha = request.query_params.get('fecha')
        
        if not profesional_id:
            return Response(
                {"error": "Falta parámetro: profesional_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        turnos = self.get_queryset().filter(idprofesional_id=profesional_id)
        
        if fecha:
            try:
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
                turnos = turnos.filter(fecha=fecha)
            except ValueError:
                return Response(
                    {"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        turnos = turnos.order_by('fecha', 'hora')
        serializer = self.get_serializer(turnos, many=True)
        return Response(serializer.data)