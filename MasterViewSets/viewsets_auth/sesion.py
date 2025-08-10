from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models
from django.utils import timezone
from datetime import timedelta

from MasterModels.modelos_auth.sesion import Sesion
from MasterSerializers.serializers_auth.sesion import SesionSerializer, SesionListSerializer

class SesionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para gestión y monitoreo de sesiones"""
    queryset = Sesion.objects.select_related('idusuario')
    serializer_class = SesionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['idusuario', 'activa', 'cerrada_por_usuario', 'cerrada_por_inactividad']
    search_fields = ['idusuario__nombre', 'idusuario__apellido', 'ip_address', 'dispositivo']
    ordering_fields = ['fecha_inicio', 'fecha_ultimo_uso', 'acciones_realizadas']
    ordering = ['-fecha_inicio']

    def get_queryset(self):
        """Filtrar sesiones según permisos del usuario"""
        user = self.request.user
        
        if user.idrol.nivel >= 8:  # Admin puede ver todas las sesiones
            return self.queryset
        else:  # Usuarios normales solo ven sus sesiones
            return self.queryset.filter(idusuario=user)

    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Obtiene sesiones activas"""
        sesiones_activas = self.get_queryset().filter(
            activa=True,
            fecha_expiracion__gt=timezone.now()
        )
        
        resultado = []
        for sesion in sesiones_activas:
            resultado.append({
                'id': sesion.id,
                'usuario': sesion.idusuario.get_full_name(),
                'email': sesion.idusuario.email,
                'fecha_inicio': sesion.fecha_inicio,
                'fecha_ultimo_uso': sesion.fecha_ultimo_uso,
                'ip_address': sesion.ip_address,
                'dispositivo': sesion.dispositivo,
                'duracion': str(sesion.get_duracion()),
                'acciones_realizadas': sesion.acciones_realizadas
            })
        
        return Response(resultado)

    @action(detail=False, methods=['get'])
    def mi_sesion(self, request):
        """Obtiene información de la sesión actual del usuario"""
        sesiones_usuario = Sesion.objects.filter(
            idusuario=request.user,
            activa=True
        ).order_by('-fecha_inicio')
        
        if sesiones_usuario.exists():
            sesion = sesiones_usuario.first()
            return Response({
                'id': sesion.id,
                'fecha_inicio': sesion.fecha_inicio,
                'fecha_ultimo_uso': sesion.fecha_ultimo_uso,
                'ip_address': sesion.ip_address,
                'dispositivo': sesion.dispositivo,
                'navegador': sesion.navegador,
                'duracion': str(sesion.get_duracion()),
                'tiempo_inactividad': str(sesion.get_tiempo_inactividad()),
                'acciones_realizadas': sesion.acciones_realizadas,
                'paginas_visitadas': sesion.paginas_visitadas,
                'fecha_expiracion': sesion.fecha_expiracion
            })
        
        return Response({'message': 'No hay sesión activa'})

    @action(detail=False, methods=['get'])
    def sospechosas(self, request):
        """Obtiene sesiones sospechosas"""
        if request.user.idrol.nivel < 8:
            return Response(
                {'error': 'Sin permisos para ver sesiones sospechosas'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        sesiones_activas = self.queryset.filter(activa=True)
        sesiones_sospechosas = []
        
        for sesion in sesiones_activas:
            criterios = sesion.es_sospechosa()
            if criterios:
                sesiones_sospechosas.append({
                    'id': sesion.id,
                    'usuario': sesion.idusuario.get_full_name(),
                    'email': sesion.idusuario.email,
                    'criterios_sospechosos': criterios,
                    'fecha_inicio': sesion.fecha_inicio,
                    'ip_address': sesion.ip_address,
                    'duracion': str(sesion.get_duracion()),
                    'acciones_realizadas': sesion.acciones_realizadas
                })
        
        return Response(sesiones_sospechosas)

    @action(detail=True, methods=['post'])
    def cerrar(self, request, pk=None):
        """Cierra una sesión específica"""
        sesion = self.get_object()
        
        # Solo admin o el propio usuario pueden cerrar la sesión
        if request.user.idrol.nivel < 8 and sesion.idusuario != request.user:
            return Response(
                {'error': 'Sin permisos para cerrar esta sesión'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        motivo = 'admin' if sesion.idusuario != request.user else 'usuario'
        sesion.cerrar_sesion(motivo)
        
        return Response({'message': 'Sesión cerrada exitosamente'})

    @action(detail=False, methods=['post'])
    def cerrar_todas_usuario(self, request):
        """Cierra todas las sesiones de un usuario"""
        usuario_id = request.data.get('usuario_id')
        
        if not usuario_id:
            return Response(
                {'error': 'usuario_id es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Solo admin puede cerrar sesiones de otros usuarios
        if request.user.idrol.nivel < 8 and str(request.user.id) != str(usuario_id):
            return Response(
                {'error': 'Sin permisos para cerrar sesiones de otros usuarios'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        from MasterModels.modelos_auth.usuario import Usuario
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            cantidad = Sesion.cerrar_todas_sesiones_usuario(usuario, 'admin')
            
            return Response({
                'message': f'{cantidad} sesiones cerradas para {usuario.get_full_name()}'
            })
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def limpiar_expiradas(self, request):
        """Limpia sesiones expiradas"""
        if request.user.idrol.nivel < 8:
            return Response(
                {'error': 'Sin permisos para limpiar sesiones'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        cantidad = Sesion.limpiar_sesiones_expiradas()
        return Response({
            'message': f'{cantidad} sesiones expiradas limpiadas'
        })

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas de sesiones"""
        if request.user.idrol.nivel < 8:
            # Usuarios normales solo ven sus estadísticas
            queryset = self.queryset.filter(idusuario=request.user)
        else:
            queryset = self.queryset
        
        now = timezone.now()
        hace_24h = now - timedelta(hours=24)
        hace_7d = now - timedelta(days=7)
        
        stats = {
            'sesiones_activas': queryset.filter(
                activa=True, 
                fecha_expiracion__gt=now
            ).count(),
            'sesiones_24h': queryset.filter(
                fecha_inicio__gte=hace_24h
            ).count(),
            'sesiones_7d': queryset.filter(
                fecha_inicio__gte=hace_7d
            ).count(),
            'duracion_promedio_minutos': 0,
            'dispositivos_mas_usados': [],
            'ips_mas_frecuentes': [],
            'usuarios_mas_activos': []
        }
        
        # Calcular duración promedio
        sesiones_con_duracion = queryset.filter(activa=False)
        if sesiones_con_duracion.exists():
            duraciones = []
            for sesion in sesiones_con_duracion[:100]:  # Últimas 100 para performance
                duracion = sesion.get_duracion()
                duraciones.append(duracion.total_seconds() / 60)
            
            if duraciones:
                stats['duracion_promedio_minutos'] = sum(duraciones) / len(duraciones)
        
        # Solo para admins - estadísticas más detalladas
        if request.user.idrol.nivel >= 8:
            # Dispositivos más usados
            stats['dispositivos_mas_usados'] = list(
                queryset.exclude(dispositivo__isnull=True)
                        .exclude(dispositivo='')
                        .values('dispositivo')
                        .annotate(cantidad=models.Count('id'))
                        .order_by('-cantidad')[:5]
            )
            
            # IPs más frecuentes
            stats['ips_mas_frecuentes'] = list(
                queryset.values('ip_address')
                        .annotate(cantidad=models.Count('id'))
                        .order_by('-cantidad')[:5]
            )
            
            # Usuarios más activos
            stats['usuarios_mas_activos'] = list(
                queryset.values(
                    'idusuario__nombre', 
                    'idusuario__apellido'
                ).annotate(
                    total_sesiones=models.Count('id'),
                    total_acciones=models.Sum('acciones_realizadas')
                ).order_by('-total_acciones')[:5]
            )
        
        return Response(stats)