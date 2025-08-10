from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.utils import timezone
from datetime import datetime, timedelta
from django.db import models

from MasterModels.modelos_turnos.agendaprofesional import AgendaProfesional
from MasterSerializers.serializers_turnos.agendaprofesional import AgendaProfesionalSerializer, AgendaProfesionalDetailSerializer

class AgendaProfesionalViewSet(viewsets.ModelViewSet):
    queryset = AgendaProfesional.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'idprofesional', 'idcentro', 'idespecialidadpractica', 
        'dia_semana', 'activo', 'disabled'
    ]
    ordering_fields = ['id', 'dia_semana', 'hora_inicio', 'created_at']
    ordering = ['dia_semana', 'hora_inicio']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AgendaProfesionalDetailSerializer
        return AgendaProfesionalSerializer

    @action(detail=False, methods=['get'])
    def disponibilidad(self, request):
        """
        Obtiene la disponibilidad de horarios para un profesional en un centro específico
        Parámetros: profesional_id, centro_id, fecha_inicio, fecha_fin
        """
        profesional_id = request.query_params.get('profesional_id')
        centro_id = request.query_params.get('centro_id')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        if not all([profesional_id, centro_id, fecha_inicio, fecha_fin]):
            return Response(
                {"error": "Faltan parámetros: profesional_id, centro_id, fecha_inicio, fecha_fin"}, 
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

        # Obtener agendas del profesional en el centro
        agendas = AgendaProfesional.objects.filter(
            idprofesional_id=profesional_id,
            idcentro_id=centro_id,
            activo=True,
            fecha_inicio_vigencia__lte=fecha_fin,
            disabled=False
        ).filter(
            models.Q(fecha_fin_vigencia__isnull=True) | 
            models.Q(fecha_fin_vigencia__gte=fecha_inicio)
        )

        # Generar horarios disponibles por día
        from MasterModels.modelos_turnos.turno import Turno
        from MasterModels.modelos_turnos.excepcionagenda import ExcepcionAgenda
        
        disponibilidad = []
        fecha_actual = fecha_inicio
        
        while fecha_actual <= fecha_fin:
            dia_semana = fecha_actual.isoweekday()
            
            # Verificar si hay agenda para este día
            agenda_dia = agendas.filter(dia_semana=dia_semana).first()
            
            if agenda_dia:
                # Verificar excepciones
                excepciones = ExcepcionAgenda.objects.filter(
                    fecha_inicio__lte=fecha_actual,
                    fecha_fin__gte=fecha_actual,
                    disabled=False
                ).filter(
                    models.Q(idprofesional_id=profesional_id) |
                    models.Q(idcentro_id=centro_id, afecta_centro_completo=True)
                )
                
                if not excepciones.exists():
                    # Generar horarios disponibles
                    hora_actual = agenda_dia.hora_inicio
                    horarios_ocupados = list(Turno.objects.filter(
                        idprofesional_id=profesional_id,
                        idcentro_id=centro_id,
                        fecha=fecha_actual
                    ).exclude(
                        idestadoturno__codigo='CANCELADO'
                    ).values_list('hora', flat=True))
                    
                    horarios_disponibles = []
                    while hora_actual < agenda_dia.hora_fin:
                        if hora_actual not in horarios_ocupados:
                            horarios_disponibles.append(hora_actual.strftime('%H:%M'))
                        
                        # Sumar duración del turno
                        hora_actual = (datetime.combine(fecha_actual, hora_actual) + 
                                     timedelta(minutes=agenda_dia.duracion_turno_minutos)).time()
                    
                    if horarios_disponibles:
                        disponibilidad.append({
                            'fecha': fecha_actual.strftime('%Y-%m-%d'),
                            'dia_semana': dia_semana,
                            'horarios': horarios_disponibles
                        })
            
            fecha_actual += timedelta(days=1)

        return Response(disponibilidad)

    @action(detail=False, methods=['get'])
    def por_profesional(self, request):
        """Obtiene todas las agendas de un profesional"""
        profesional_id = request.query_params.get('profesional_id')
        if not profesional_id:
            return Response(
                {"error": "Falta parámetro: profesional_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        agendas = self.get_queryset().filter(idprofesional_id=profesional_id)
        serializer = self.get_serializer(agendas, many=True)
        return Response(serializer.data)