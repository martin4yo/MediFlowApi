from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models

from MasterModels.modelos_auth.permiso import Permiso
from MasterSerializers.serializers_auth.permiso import PermisoSerializer, PermisoListSerializer

class PermisoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para permisos del sistema"""
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['modulo', 'accion', 'activo', 'nivel_requerido']
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering_fields = ['modulo', 'accion', 'nivel_requerido']
    ordering = ['modulo', 'nivel_requerido', 'accion']

    @action(detail=False, methods=['get'])
    def por_modulo(self, request):
        """Obtiene permisos agrupados por módulo"""
        modulo = request.query_params.get('modulo')
        if not modulo:
            return Response(
                {'error': 'Parámetro modulo es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        permisos = self.queryset.filter(modulo=modulo, activo=True)
        
        resultado = []
        for permiso in permisos:
            resultado.append({
                'id': permiso.id,
                'nombre': permiso.nombre,
                'codigo': permiso.codigo,
                'accion': permiso.accion,
                'descripcion': permiso.descripcion,
                'nivel_requerido': permiso.nivel_requerido
            })
        
        return Response(resultado)

    @action(detail=False, methods=['get'])
    def modulos_disponibles(self, request):
        """Lista todos los módulos disponibles"""
        modulos = [{'value': choice[0], 'label': choice[1]} 
                  for choice in Permiso._meta.get_field('modulo').choices]
        return Response(modulos)

    @action(detail=False, methods=['get'])
    def acciones_disponibles(self, request):
        """Lista todas las acciones disponibles"""
        acciones = [{'value': choice[0], 'label': choice[1]} 
                   for choice in Permiso._meta.get_field('accion').choices]
        return Response(acciones)

    @action(detail=False, methods=['post'])
    def crear_permisos_sistema(self, request):
        """Crea los permisos básicos del sistema"""
        permisos_creados = Permiso.crear_permisos_sistema()
        
        resultado = []
        for permiso in permisos_creados:
            resultado.append({
                'id': permiso.id,
                'nombre': permiso.nombre,
                'codigo': permiso.codigo,
                'modulo': permiso.modulo,
                'accion': permiso.accion
            })
        
        return Response({
            'message': f'{len(permisos_creados)} permisos del sistema verificados',
            'permisos': resultado
        })

    @action(detail=False, methods=['get'])
    def por_nivel(self, request):
        """Obtiene permisos por nivel mínimo requerido"""
        nivel = request.query_params.get('nivel')
        if not nivel:
            return Response(
                {'error': 'Parámetro nivel es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            nivel = int(nivel)
        except ValueError:
            return Response(
                {'error': 'El nivel debe ser un número'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        permisos = self.queryset.filter(nivel_requerido__lte=nivel, activo=True)
        
        resultado = {}
        for permiso in permisos:
            if permiso.modulo not in resultado:
                resultado[permiso.modulo] = []
            
            resultado[permiso.modulo].append({
                'codigo': permiso.codigo,
                'accion': permiso.accion,
                'descripcion': permiso.descripcion,
                'nivel_requerido': permiso.nivel_requerido
            })
        
        return Response(resultado)

    @action(detail=False, methods=['get'])
    def matriz_permisos(self, request):
        """Genera matriz de permisos por módulo y acción"""
        permisos = self.queryset.filter(activo=True)
        
        matriz = {}
        for permiso in permisos:
            if permiso.modulo not in matriz:
                matriz[permiso.modulo] = {}
            
            matriz[permiso.modulo][permiso.accion] = {
                'id': permiso.id,
                'nombre': permiso.nombre,
                'codigo': permiso.codigo,
                'descripcion': permiso.descripcion,
                'nivel_requerido': permiso.nivel_requerido
            }
        
        return Response(matriz)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas de permisos"""
        stats = {
            'total_permisos': self.queryset.count(),
            'permisos_activos': self.queryset.filter(activo=True).count(),
            'por_modulo': list(
                self.queryset.values('modulo').annotate(
                    cantidad=models.Count('id')
                ).order_by('-cantidad')
            ),
            'por_accion': list(
                self.queryset.values('accion').annotate(
                    cantidad=models.Count('id')
                ).order_by('-cantidad')
            ),
            'por_nivel': list(
                self.queryset.values('nivel_requerido').annotate(
                    cantidad=models.Count('id')
                ).order_by('nivel_requerido')
            )
        }
        return Response(stats)