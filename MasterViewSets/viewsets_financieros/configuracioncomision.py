from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from datetime import datetime
from django.db import models

from MasterModels.modelos_financieros.configuracioncomision import ConfiguracionComision
from MasterSerializers.serializers_financieros.configuracioncomision import ConfiguracionComisionSerializer, ConfiguracionComisionDetailSerializer

class ConfiguracionComisionViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracionComision.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'idprofesional', 'idcentro', 'idespecialidadpractica', 
        'activo', 'prioridad', 'disabled'
    ]
    ordering_fields = ['id', 'prioridad', 'fecha_inicio', 'created_at']
    ordering = ['prioridad', '-fecha_inicio']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConfiguracionComisionDetailSerializer
        return ConfiguracionComisionSerializer

    @action(detail=False, methods=['get'])
    def obtener_comision(self, request):
        """Obtiene la configuración de comisión aplicable para parámetros específicos"""
        profesional_id = request.query_params.get('profesional_id')
        centro_id = request.query_params.get('centro_id')
        especialidad_practica_id = request.query_params.get('especialidad_practica_id')
        fecha = request.query_params.get('fecha')
        
        if not all([profesional_id, centro_id, especialidad_practica_id]):
            return Response(
                {"error": "Faltan parámetros: profesional_id, centro_id, especialidad_practica_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if fecha:
            try:
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Buscar configuración aplicable
        from MasterModels.modelos_profesionales.profesional import Profesional
        from MasterModels.modelos_general.centro import Centro
        from MasterModels.modelos_general.especialidadpractica import EspecialidadPractica
        
        try:
            profesional = Profesional.objects.get(id=profesional_id)
            centro = Centro.objects.get(id=centro_id)
            especialidad_practica = EspecialidadPractica.objects.get(id=especialidad_practica_id)
        except (Profesional.DoesNotExist, Centro.DoesNotExist, EspecialidadPractica.DoesNotExist):
            return Response(
                {"error": "Uno o más objetos no encontrados"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        config = ConfiguracionComision.obtener_comision(
            profesional, centro, especialidad_practica, fecha
        )
        
        if config:
            serializer = self.get_serializer(config)
            return Response({
                "configuracion_encontrada": True,
                "configuracion": serializer.data
            })
        else:
            return Response({
                "configuracion_encontrada": False,
                "mensaje": "No se encontró configuración específica, se aplicarán valores por defecto",
                "valores_defecto": {
                    "porcentaje_profesional": 70.00,
                    "porcentaje_centro": 30.00
                }
            })

    @action(detail=False, methods=['get'])
    def por_profesional(self, request):
        """Obtiene todas las configuraciones de un profesional"""
        profesional_id = request.query_params.get('profesional_id')
        if not profesional_id:
            return Response(
                {"error": "Falta parámetro: profesional_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        configuraciones = self.get_queryset().filter(
            models.Q(idprofesional_id=profesional_id) |
            models.Q(idprofesional__isnull=True)  # Configuraciones generales
        ).order_by('prioridad')
        
        serializer = self.get_serializer(configuraciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_centro(self, request):
        """Obtiene todas las configuraciones de un centro"""
        centro_id = request.query_params.get('centro_id')
        if not centro_id:
            return Response(
                {"error": "Falta parámetro: centro_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        configuraciones = self.get_queryset().filter(
            models.Q(idcentro_id=centro_id) |
            models.Q(idcentro__isnull=True)  # Configuraciones generales
        ).order_by('prioridad')
        
        serializer = self.get_serializer(configuraciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def vigentes(self, request):
        """Obtiene configuraciones vigentes en una fecha específica"""
        fecha = request.query_params.get('fecha')
        
        if fecha:
            try:
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            from django.utils import timezone
            fecha = timezone.now().date()
        
        configuraciones = self.get_queryset().filter(
            activo=True,
            fecha_inicio__lte=fecha
        ).filter(
            models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gte=fecha)
        ).order_by('prioridad')
        
        serializer = self.get_serializer(configuraciones, many=True)
        return Response({
            "fecha_consulta": fecha,
            "configuraciones_vigentes": serializer.data
        })

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactiva una configuración"""
        configuracion = self.get_object()
        configuracion.activo = False
        configuracion.save()
        
        serializer = self.get_serializer(configuracion)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activa una configuración"""
        configuracion = self.get_object()
        configuracion.activo = True
        configuracion.save()
        
        serializer = self.get_serializer(configuracion)
        return Response(serializer.data)