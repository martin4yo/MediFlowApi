from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta

from MasterModels.modelos_notificaciones.notificacion import Notificacion
from MasterModels.modelos_notificaciones.plantillanotificacion import PlantillaNotificacion
from MasterSerializers.serializers_notificaciones.notificacion import (
    NotificacionSerializer, 
    NotificacionListSerializer,
    NotificacionCreateSerializer
)

class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo', 'canal', 'estado', 'prioridad', 'idpaciente', 'idcentro']
    search_fields = ['destinatario_nombre', 'destinatario_email', 'asunto', 'contenido']
    ordering_fields = ['fecha_programada', 'fecha_enviado', 'created_at', 'prioridad']
    ordering = ['-fecha_programada']

    def get_serializer_class(self):
        if self.action == 'list':
            return NotificacionListSerializer
        elif self.action == 'create':
            return NotificacionCreateSerializer
        return NotificacionSerializer

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Obtiene notificaciones pendientes de envío"""
        notificaciones = self.queryset.filter(
            estado='PENDIENTE',
            fecha_programada__lte=timezone.now()
        ).order_by('prioridad', 'fecha_programada')
        
        serializer = NotificacionListSerializer(notificaciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """Obtiene notificaciones filtradas por estado"""
        estado = request.query_params.get('estado')
        if not estado:
            return Response(
                {'error': 'Parámetro estado es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notificaciones = self.queryset.filter(estado=estado)
        serializer = NotificacionListSerializer(notificaciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_paciente(self, request):
        """Obtiene notificaciones de un paciente específico"""
        paciente_id = request.query_params.get('paciente_id')
        if not paciente_id:
            return Response(
                {'error': 'Parámetro paciente_id es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notificaciones = self.queryset.filter(idpaciente=paciente_id)
        serializer = NotificacionListSerializer(notificaciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de notificaciones"""
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        queryset = self.queryset
        
        if fecha_desde:
            try:
                fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=fecha_desde)
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_desde inválido. Use YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if fecha_hasta:
            try:
                fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=fecha_hasta)
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_hasta inválido. Use YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        estadisticas = {
            'total': queryset.count(),
            'por_estado': list(queryset.values('estado').annotate(cantidad=Count('id'))),
            'por_tipo': list(queryset.values('tipo').annotate(cantidad=Count('id'))),
            'por_canal': list(queryset.values('canal').annotate(cantidad=Count('id'))),
            'exitosas': queryset.filter(estado='ENTREGADO').count(),
            'fallidas': queryset.filter(estado='ERROR').count(),
            'pendientes': queryset.filter(estado='PENDIENTE').count()
        }
        
        return Response(estadisticas)

    @action(detail=False, methods=['post'])
    def crear_desde_plantilla(self, request):
        """Crea notificación desde plantilla"""
        plantilla_id = request.data.get('plantilla_id')
        destinatario_datos = request.data.get('destinatario_datos', {})
        variables = request.data.get('variables', {})
        kwargs = request.data.get('kwargs', {})
        
        if not plantilla_id:
            return Response(
                {'error': 'plantilla_id es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            plantilla = PlantillaNotificacion.objects.get(id=plantilla_id)
            notificacion = Notificacion.crear_desde_plantilla(
                plantilla, destinatario_datos, variables, **kwargs
            )
            serializer = NotificacionSerializer(notificacion)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except PlantillaNotificacion.DoesNotExist:
            return Response(
                {'error': 'Plantilla no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al crear notificación: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def marcar_enviado(self, request, pk=None):
        """Marca una notificación como enviada"""
        notificacion = self.get_object()
        notificacion.marcar_enviado()
        return Response({'status': 'Notificación marcada como enviada'})

    @action(detail=True, methods=['post'])
    def marcar_entregado(self, request, pk=None):
        """Marca una notificación como entregada"""
        notificacion = self.get_object()
        notificacion.marcar_entregado()
        return Response({'status': 'Notificación marcada como entregada'})

    @action(detail=True, methods=['post'])
    def marcar_error(self, request, pk=None):
        """Marca una notificación con error"""
        notificacion = self.get_object()
        mensaje_error = request.data.get('mensaje_error', 'Error no especificado')
        notificacion.marcar_error(mensaje_error)
        return Response({'status': 'Notificación marcada con error'})

    @action(detail=True, methods=['post'])
    def reintentar(self, request, pk=None):
        """Reintenta el envío de una notificación"""
        notificacion = self.get_object()
        
        if not notificacion.puede_reintentar():
            return Response(
                {'error': 'No se puede reintentar esta notificación'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notificacion.estado = 'PENDIENTE'
        notificacion.fecha_programada = timezone.now()
        notificacion.save()
        
        return Response({'status': 'Notificación programada para reintento'})

    @action(detail=False, methods=['post'])
    def programar_masiva(self, request):
        """Programa notificaciones masivas"""
        plantilla_id = request.data.get('plantilla_id')
        destinatarios = request.data.get('destinatarios', [])
        variables_globales = request.data.get('variables_globales', {})
        fecha_programada = request.data.get('fecha_programada')
        
        if not plantilla_id or not destinatarios:
            return Response(
                {'error': 'plantilla_id y destinatarios son requeridos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            plantilla = PlantillaNotificacion.objects.get(id=plantilla_id)
            notificaciones_creadas = []
            
            for destinatario in destinatarios:
                variables = {**variables_globales, **destinatario.get('variables', {})}
                kwargs = destinatario.get('kwargs', {})
                
                if fecha_programada:
                    kwargs['fecha_programada'] = fecha_programada
                
                notificacion = Notificacion.crear_desde_plantilla(
                    plantilla, 
                    destinatario.get('datos', {}), 
                    variables, 
                    **kwargs
                )
                notificaciones_creadas.append(notificacion.id)
            
            return Response({
                'status': f'{len(notificaciones_creadas)} notificaciones programadas',
                'notificaciones_ids': notificaciones_creadas
            })
            
        except PlantillaNotificacion.DoesNotExist:
            return Response(
                {'error': 'Plantilla no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al programar notificaciones: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def resumen_diario(self, request):
        """Resumen de notificaciones del día"""
        fecha = request.query_params.get('fecha')
        if fecha:
            try:
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            fecha = timezone.now().date()
        
        notificaciones = self.queryset.filter(created_at__date=fecha)
        
        resumen = {
            'fecha': fecha,
            'total': notificaciones.count(),
            'enviadas': notificaciones.filter(estado='ENVIADO').count(),
            'entregadas': notificaciones.filter(estado='ENTREGADO').count(),
            'fallidas': notificaciones.filter(estado='ERROR').count(),
            'pendientes': notificaciones.filter(estado='PENDIENTE').count(),
            'por_canal': list(notificaciones.values('canal').annotate(cantidad=Count('id'))),
            'por_tipo': list(notificaciones.values('tipo').annotate(cantidad=Count('id')))
        }
        
        return Response(resumen)