from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models, transaction
from django.utils import timezone

from MasterModels.modelos_general.tenant import Tenant
from MasterModels.modelos_general.usuario_tenant import UsuarioTenant
from MasterModels.modelos_general.centro import Centro
from MasterSerializers.serializers_general.tenant import (
    TenantSerializer, TenantListSerializer, TenantCreateSerializer,
    UsuarioTenantSerializer, AsignarUsuarioTenantSerializer,
    TenantEstadisticasSerializer, CentroTenantSerializer
)

class TenantViewSet(viewsets.ModelViewSet):
    """ViewSet para ABM de Tenants"""
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activo', 'es_demo', 'tipo_facturacion']
    search_fields = ['nombre', 'codigo', 'email_contacto']
    ordering_fields = ['nombre', 'codigo', 'created_at']
    ordering = ['nombre']
    
    def get_permissions(self):
        """Permisos personalizados"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action == 'list':
            return TenantListSerializer
        elif self.action == 'create':
            return TenantCreateSerializer
        return TenantSerializer
    
    def get_queryset(self):
        """Filtrar tenants según permisos del usuario"""
        user = self.request.user
        
        if user.is_superuser:
            return Tenant.objects.all()
        
        # Usuarios normales solo ven sus tenants asignados
        tenants_ids = user.get_tenants_activos().values_list('tenant_id', flat=True)
        return Tenant.objects.filter(id__in=tenants_ids)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas generales de tenants"""
        stats = {
            'total_tenants': Tenant.objects.count(),
            'tenants_activos': Tenant.objects.filter(activo=True).count(),
            'tenants_demo': Tenant.objects.filter(es_demo=True).count(),
            'total_usuarios': UsuarioTenant.objects.filter(activo=True).count(),
            'total_centros': Centro.objects.filter(activo=True).count(),
            'distribucion_por_tipo': dict(
                Tenant.objects.values('tipo_facturacion').annotate(
                    cantidad=models.Count('id')
                ).values_list('tipo_facturacion', 'cantidad')
            ),
            'tenants_por_vencer': []
        }
        
        # Tenants que vencen en los próximos 30 días
        fecha_limite = timezone.now() + timezone.timedelta(days=30)
        tenants_vencen = Tenant.objects.filter(
            fecha_vencimiento__isnull=False,
            fecha_vencimiento__lte=fecha_limite,
            activo=True
        ).values('id', 'nombre', 'codigo', 'fecha_vencimiento')
        
        stats['tenants_por_vencer'] = list(tenants_vencen)
        
        serializer = TenantEstadisticasSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def usuarios(self, request, pk=None):
        """Listar usuarios asignados al tenant"""
        tenant = self.get_object()
        usuarios_tenant = UsuarioTenant.objects.filter(tenant=tenant)
        
        # Filtros opcionales
        activos_solo = request.query_params.get('activos', 'false').lower() == 'true'
        if activos_solo:
            usuarios_tenant = usuarios_tenant.filter(activo=True)
        
        serializer = UsuarioTenantSerializer(usuarios_tenant, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def asignar_usuario(self, request, pk=None):
        """Asignar usuario al tenant"""
        tenant = self.get_object()
        
        # Agregar el tenant_id a los datos
        data = request.data.copy()
        data['tenant_id'] = tenant.id
        
        serializer = AsignarUsuarioTenantSerializer(
            data=data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            usuario_tenant = serializer.save()
            response_serializer = UsuarioTenantSerializer(usuario_tenant)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def desasignar_usuario(self, request, pk=None):
        """Desasignar usuario del tenant"""
        tenant = self.get_object()
        usuario_id = request.data.get('usuario_id')
        
        if not usuario_id:
            return Response(
                {'error': 'Se requiere usuario_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            usuario_tenant = UsuarioTenant.objects.get(
                tenant=tenant,
                usuario_id=usuario_id
            )
            usuario_tenant.delete()
            return Response({'message': 'Usuario desasignado correctamente'})
        except UsuarioTenant.DoesNotExist:
            return Response(
                {'error': 'Asignación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar tenant"""
        tenant = self.get_object()
        tenant.activo = True
        tenant.save()
        return Response({'message': 'Tenant activado correctamente'})
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar tenant"""
        tenant = self.get_object()
        
        # No permitir desactivar el tenant demo
        if tenant.es_demo:
            return Response(
                {'error': 'No se puede desactivar el tenant demo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tenant.activo = False
        tenant.save()
        
        # Desactivar todas las asignaciones de usuarios
        UsuarioTenant.objects.filter(tenant=tenant).update(activo=False)
        
        return Response({'message': 'Tenant desactivado correctamente'})
    
    @action(detail=True, methods=['get'])
    def centros(self, request, pk=None):
        """Listar centros del tenant"""
        tenant = self.get_object()
        centros = Centro.objects.filter(tenant=tenant)
        
        # Filtros opcionales
        activos_solo = request.query_params.get('activos', 'false').lower() == 'true'
        if activos_solo:
            centros = centros.filter(activo=True)
        
        serializer = CentroTenantSerializer(centros, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def crear_centro(self, request, pk=None):
        """Crear centro para el tenant"""
        tenant = self.get_object()
        
        # Verificar límites
        if not tenant.puede_agregar_centros:
            return Response(
                {'error': f'El tenant ha alcanzado su límite de centros ({tenant.limite_centros})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Agregar el tenant a los datos
        data = request.data.copy()
        data['tenant'] = tenant.id
        
        serializer = CentroTenantSerializer(data=data)
        if serializer.is_valid():
            centro = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def demo(self, request):
        """Obtener el tenant demo"""
        try:
            tenant_demo = Tenant.get_tenant_demo()
            serializer = TenantSerializer(tenant_demo)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Error al obtener tenant demo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def crear_tenant_completo(self, request):
        """Crear tenant con centro inicial"""
        if not request.user.is_superuser:
            return Response(
                {'error': 'Solo administradores pueden crear tenants'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        with transaction.atomic():
            # Crear tenant
            tenant_serializer = TenantCreateSerializer(
                data=request.data.get('tenant', {}),
                context={'request': request}
            )
            
            if not tenant_serializer.is_valid():
                return Response(
                    {'tenant_errors': tenant_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            tenant = tenant_serializer.save()
            
            # Crear centro inicial si se proporciona
            centro_data = request.data.get('centro')
            if centro_data:
                centro_data['tenant'] = tenant.id
                centro_serializer = CentroTenantSerializer(data=centro_data)
                
                if centro_serializer.is_valid():
                    centro = centro_serializer.save()
                else:
                    return Response(
                        {'centro_errors': centro_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Respuesta con tenant creado
            response_serializer = TenantSerializer(tenant)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class UsuarioTenantViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar asignaciones usuario-tenant"""
    queryset = UsuarioTenant.objects.all()
    serializer_class = UsuarioTenantSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activo', 'es_administrador_tenant', 'tenant', 'usuario']
    search_fields = ['usuario__nombre', 'usuario__apellido', 'usuario__email', 'tenant__nombre']
    ordering_fields = ['fecha_asignacion', 'usuario__apellido']
    ordering = ['-fecha_asignacion']
    
    def get_permissions(self):
        """Solo administradores pueden gestionar asignaciones"""
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
    
    def get_queryset(self):
        """Filtrar según permisos del usuario"""
        user = self.request.user
        
        if user.is_superuser:
            return UsuarioTenant.objects.all()
        
        # Admin de tenant puede ver solo sus asignaciones
        tenants_admin = user.get_tenants_activos().filter(
            es_administrador_tenant=True
        ).values_list('tenant_id', flat=True)
        
        return UsuarioTenant.objects.filter(tenant_id__in=tenants_admin)
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar asignación usuario-tenant"""
        usuario_tenant = self.get_object()
        usuario_tenant.activo = True
        usuario_tenant.save()
        return Response({'message': 'Asignación activada correctamente'})
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar asignación usuario-tenant"""
        usuario_tenant = self.get_object()
        usuario_tenant.activo = False
        usuario_tenant.save()
        return Response({'message': 'Asignación desactivada correctamente'})
    
    @action(detail=True, methods=['patch'])
    def actualizar_centros(self, request, pk=None):
        """Actualizar centros asignados al usuario en el tenant"""
        usuario_tenant = self.get_object()
        centros_ids = request.data.get('centros_ids', [])
        
        # Validar que los centros pertenezcan al tenant
        centros_validos = Centro.objects.filter(
            id__in=centros_ids,
            tenant=usuario_tenant.tenant,
            activo=True
        )
        
        if len(centros_validos) != len(centros_ids):
            return Response(
                {'error': 'Algunos centros no son válidos o no pertenecen al tenant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuario_tenant.centros.set(centros_validos)
        
        serializer = UsuarioTenantSerializer(usuario_tenant)
        return Response(serializer.data)