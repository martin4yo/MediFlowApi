from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models

from MasterModels.modelos_auth.rol import Rol
from MasterSerializers.serializers_auth.rol import (
    RolSerializer, 
    RolListSerializer,
    RolCreateSerializer
)

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activo', 'es_sistema', 'nivel']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'nivel', 'created_at']
    ordering = ['nivel', 'nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return RolListSerializer
        elif self.action == 'create':
            return RolCreateSerializer
        return RolSerializer

    def destroy(self, request, *args, **kwargs):
        """Prevenir eliminación de roles del sistema"""
        rol = self.get_object()
        if rol.es_sistema:
            return Response(
                {'error': 'No se pueden eliminar roles del sistema'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def sistema(self, request):
        """Obtiene solo los roles del sistema"""
        roles = self.queryset.filter(es_sistema=True, activo=True)
        serializer = RolListSerializer(roles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def personalizados(self, request):
        """Obtiene solo los roles personalizados"""
        roles = self.queryset.filter(es_sistema=False, activo=True)
        serializer = RolListSerializer(roles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def crear_roles_sistema(self, request):
        """Crea los roles básicos del sistema"""
        roles_creados = Rol.crear_roles_sistema()
        serializer = RolListSerializer(roles_creados, many=True)
        return Response({
            'message': f'{len(roles_creados)} roles del sistema verificados/creados',
            'roles': serializer.data
        })

    @action(detail=True, methods=['get'])
    def permisos(self, request, pk=None):
        """Obtiene todos los permisos del rol"""
        rol = self.get_object()
        return Response({
            'rol': rol.nombre,
            'permisos': rol.get_permisos_completos()
        })

    @action(detail=True, methods=['post'])
    def actualizar_permisos(self, request, pk=None):
        """Actualiza los permisos de un rol"""
        rol = self.get_object()
        
        if rol.es_sistema:
            return Response(
                {'error': 'No se pueden modificar permisos de roles del sistema'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar permisos por módulo
        for modulo in ['turnos', 'pacientes', 'financieros', 'reportes', 'admin']:
            permisos_modulo = request.data.get(f'permisos_{modulo}')
            if permisos_modulo is not None:
                setattr(rol, f'permisos_{modulo}', permisos_modulo)
        
        rol.save()
        
        # Invalidar cache de usuarios con este rol
        from MasterModels.utils.cache_manager import CacheManager
        usuarios_con_rol = rol.usuario_set.values_list('id', flat=True)
        for usuario_id in usuarios_con_rol:
            CacheManager.invalidar_cache_usuario(usuario_id)
        
        serializer = RolSerializer(rol)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def duplicar(self, request, pk=None):
        """Duplica un rol existente"""
        rol_original = self.get_object()
        nuevo_nombre = request.data.get('nuevo_nombre', f"{rol_original.nombre} (Copia)")
        
        nuevo_rol = Rol.objects.create(
            nombre=nuevo_nombre,
            descripcion=rol_original.descripcion,
            nivel=rol_original.nivel,
            permisos_turnos=rol_original.permisos_turnos,
            permisos_pacientes=rol_original.permisos_pacientes,
            permisos_financieros=rol_original.permisos_financieros,
            permisos_reportes=rol_original.permisos_reportes,
            permisos_admin=rol_original.permisos_admin,
            es_sistema=False  # Las copias nunca son del sistema
        )
        
        serializer = RolSerializer(nuevo_rol)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def jerarquia(self, request):
        """Obtiene los roles ordenados por jerarquía"""
        roles = self.queryset.filter(activo=True).order_by('-nivel', 'nombre')
        
        jerarquia = []
        for rol in roles:
            jerarquia.append({
                'id': rol.id,
                'nombre': rol.nombre,
                'nivel': rol.nivel,
                'descripcion': rol.descripcion,
                'es_sistema': rol.es_sistema,
                'usuarios_count': rol.usuario_set.filter(activo=True).count()
            })
        
        return Response(jerarquia)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas de roles"""
        stats = {
            'total_roles': self.queryset.count(),
            'roles_activos': self.queryset.filter(activo=True).count(),
            'roles_sistema': self.queryset.filter(es_sistema=True).count(),
            'roles_personalizados': self.queryset.filter(es_sistema=False).count(),
            'usuarios_por_rol': list(
                self.queryset.annotate(
                    usuarios_count=models.Count('usuario', filter=models.Q(usuario__activo=True))
                ).values('nombre', 'usuarios_count').order_by('-usuarios_count')
            ),
            'niveles_distribucion': list(
                self.queryset.values('nivel').annotate(
                    cantidad=models.Count('id')
                ).order_by('nivel')
            )
        }
        return Response(stats)