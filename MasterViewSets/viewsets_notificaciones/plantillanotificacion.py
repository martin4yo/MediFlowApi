from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from MasterModels.modelos_notificaciones.plantillanotificacion import PlantillaNotificacion
from MasterSerializers.serializers_notificaciones.plantillanotificacion import (
    PlantillaNotificacionSerializer, 
    PlantillaNotificacionListSerializer
)

class PlantillaNotificacionViewSet(viewsets.ModelViewSet):
    queryset = PlantillaNotificacion.objects.all()
    serializer_class = PlantillaNotificacionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo', 'canal', 'activa', 'es_default']
    search_fields = ['nombre', 'asunto', 'contenido']
    ordering_fields = ['nombre', 'tipo', 'canal', 'created_at']
    ordering = ['nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return PlantillaNotificacionListSerializer
        return PlantillaNotificacionSerializer

    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Obtiene solo las plantillas activas"""
        plantillas = self.queryset.filter(activa=True)
        serializer = PlantillaNotificacionListSerializer(plantillas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Obtiene plantillas agrupadas por tipo"""
        tipo = request.query_params.get('tipo')
        if not tipo:
            return Response(
                {'error': 'Parámetro tipo es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plantillas = self.queryset.filter(tipo=tipo, activa=True)
        serializer = PlantillaNotificacionListSerializer(plantillas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_canal(self, request):
        """Obtiene plantillas por canal de notificación"""
        canal = request.query_params.get('canal')
        if not canal:
            return Response(
                {'error': 'Parámetro canal es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plantillas = self.queryset.filter(canal=canal, activa=True)
        serializer = PlantillaNotificacionListSerializer(plantillas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def defaults(self, request):
        """Obtiene todas las plantillas por defecto"""
        plantillas = self.queryset.filter(es_default=True, activa=True)
        serializer = PlantillaNotificacionListSerializer(plantillas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """Previsualiza la plantilla con variables de ejemplo"""
        plantilla = self.get_object()
        variables = request.data.get('variables', {})
        
        try:
            resultado = plantilla.renderizar(variables)
            return Response(resultado)
        except Exception as e:
            return Response(
                {'error': f'Error al renderizar plantilla: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activa una plantilla"""
        plantilla = self.get_object()
        plantilla.activa = True
        plantilla.save()
        return Response({'status': 'Plantilla activada'})

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactiva una plantilla"""
        plantilla = self.get_object()
        plantilla.activa = False
        plantilla.save()
        return Response({'status': 'Plantilla desactivada'})

    @action(detail=True, methods=['post'])
    def marcar_default(self, request, pk=None):
        """Marca esta plantilla como por defecto"""
        plantilla = self.get_object()
        
        # Remover default de otras plantillas del mismo tipo/canal
        PlantillaNotificacion.objects.filter(
            tipo=plantilla.tipo,
            canal=plantilla.canal,
            es_default=True
        ).update(es_default=False)
        
        # Marcar esta como default
        plantilla.es_default = True
        plantilla.save()
        
        return Response({'status': 'Plantilla marcada como por defecto'})

    @action(detail=False, methods=['get'])
    def tipos_disponibles(self, request):
        """Lista todos los tipos de notificación disponibles"""
        tipos = [{'value': choice[0], 'label': choice[1]} 
                for choice in PlantillaNotificacion._meta.get_field('tipo').choices]
        return Response(tipos)

    @action(detail=False, methods=['get'])
    def canales_disponibles(self, request):
        """Lista todos los canales de notificación disponibles"""
        canales = [{'value': choice[0], 'label': choice[1]} 
                  for choice in PlantillaNotificacion._meta.get_field('canal').choices]
        return Response(canales)