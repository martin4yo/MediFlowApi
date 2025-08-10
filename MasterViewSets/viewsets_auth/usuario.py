from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db import models

from MasterModels.modelos_auth.usuario import Usuario
from MasterSerializers.serializers_auth.usuario import (
    UsuarioSerializer, 
    UsuarioListSerializer,
    UsuarioCreateSerializer,
    LoginSerializer,
    CambioPasswordSerializer,
    UsuarioPerfilSerializer
)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.select_related('idrol', 'idcentro', 'idprofesional')
    serializer_class = UsuarioSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['idrol', 'idcentro', 'activo', 'email_verificado']
    search_fields = ['email', 'nombre', 'apellido']
    ordering_fields = ['nombre', 'apellido', 'email', 'ultimo_acceso']
    ordering = ['apellido', 'nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return UsuarioListSerializer
        elif self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action == 'perfil':
            return UsuarioPerfilSerializer
        return UsuarioSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear usuario y asignar automáticamente al tenant demo"""
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            # Obtener el usuario creado
            usuario = Usuario.objects.get(id=response.data['id'])
            
            # Asignar tenant demo automáticamente
            try:
                usuario.asignar_tenant_demo()
            except Exception as e:
                # Log del error pero no fallar la creación del usuario
                import logging
                logging.error(f"Error al asignar tenant demo al usuario {usuario.email}: {str(e)}")
        
        return response

    @action(detail=False, methods=['post'], permission_classes=[])
    def login(self, request):
        """Login de usuario"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            # Crear sesión personalizada
            from MasterModels.modelos_auth.sesion import Sesion
            sesion = Sesion.objects.create(
                idusuario=user,
                token=request.session.session_key or 'web_session',
                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                fecha_expiracion=timezone.now() + timezone.timedelta(hours=8)
            )
            
            response_data = {
                'user': UsuarioPerfilSerializer(user).data,
                'session_id': sesion.id,
                'message': 'Login exitoso'
            }
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout de usuario"""
        # Cerrar sesiones personalizadas
        from MasterModels.modelos_auth.sesion import Sesion
        Sesion.objects.filter(
            idusuario=request.user,
            activa=True
        ).update(activa=False, cerrada_por_usuario=True)
        
        logout(request)
        return Response({'message': 'Logout exitoso'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def perfil(self, request):
        """Obtiene el perfil del usuario autenticado"""
        serializer = UsuarioPerfilSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def actualizar_perfil(self, request):
        """Actualiza el perfil del usuario autenticado"""
        serializer = UsuarioPerfilSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def cambiar_password(self, request):
        """Cambio de contraseña"""
        serializer = CambioPasswordSerializer(
            data=request.data, 
            context={'request': request}
        )
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['password_nuevo'])
            user.debe_cambiar_password = False
            user.save()
            
            return Response({'message': 'Contraseña cambiada exitosamente'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar usuario"""
        usuario = self.get_object()
        usuario.activo = True
        usuario.save()
        return Response({'message': 'Usuario activado'})

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar usuario"""
        usuario = self.get_object()
        usuario.activo = False
        usuario.save()
        
        # Cerrar todas las sesiones del usuario
        from MasterModels.modelos_auth.sesion import Sesion
        Sesion.cerrar_todas_sesiones_usuario(usuario, 'admin')
        
        return Response({'message': 'Usuario desactivado'})

    @action(detail=True, methods=['post'])
    def desbloquear(self, request, pk=None):
        """Desbloquear usuario"""
        usuario = self.get_object()
        usuario.desbloquear_usuario()
        return Response({'message': 'Usuario desbloqueado'})

    @action(detail=True, methods=['get'])
    def sesiones_activas(self, request, pk=None):
        """Ver sesiones activas del usuario"""
        usuario = self.get_object()
        from MasterModels.modelos_auth.sesion import Sesion
        sesiones = Sesion.get_sesiones_activas_usuario(usuario)
        
        from MasterSerializers.serializers_auth.sesion import SesionListSerializer
        serializer = SesionListSerializer(sesiones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas de usuarios"""
        stats = {
            'total_usuarios': self.queryset.count(),
            'usuarios_activos': self.queryset.filter(activo=True).count(),
            'usuarios_bloqueados': self.queryset.exclude(bloqueado_hasta__isnull=True).count(),
            'por_rol': list(
                self.queryset.values('idrol__nombre').annotate(
                    cantidad=models.Count('id')
                )
            ),
            'ultimos_accesos': list(
                self.queryset.filter(ultimo_acceso__isnull=False)
                           .order_by('-ultimo_acceso')[:10]
                           .values('nombre', 'apellido', 'ultimo_acceso')
            )
        }
        return Response(stats)