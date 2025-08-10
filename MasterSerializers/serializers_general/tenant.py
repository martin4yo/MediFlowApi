from rest_framework import serializers
from MasterModels.modelos_general.tenant import Tenant
from MasterModels.modelos_general.usuario_tenant import UsuarioTenant
from MasterModels.modelos_general.centro import Centro

class TenantListSerializer(serializers.ModelSerializer):
    """Serializer básico para listar tenants"""
    centros_count = serializers.ReadOnlyField()
    usuarios_count = serializers.ReadOnlyField()
    esta_activo = serializers.ReadOnlyField()
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'nombre', 'codigo', 'activo', 'es_demo', 
            'tipo_facturacion', 'fecha_vencimiento',
            'centros_count', 'usuarios_count', 'esta_activo',
            'created_at', 'updated_at'
        ]

class TenantSerializer(serializers.ModelSerializer):
    """Serializer completo para tenant"""
    centros_count = serializers.ReadOnlyField()
    usuarios_count = serializers.ReadOnlyField()
    esta_activo = serializers.ReadOnlyField()
    puede_agregar_usuarios = serializers.ReadOnlyField()
    puede_agregar_centros = serializers.ReadOnlyField()
    
    # Información de centros asociados
    centros = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'nombre', 'codigo', 'descripcion', 'activo', 'es_demo',
            'limite_usuarios', 'limite_centros', 'email_contacto', 
            'telefono_contacto', 'tipo_facturacion', 'fecha_vencimiento',
            'configuracion', 'centros_count', 'usuarios_count', 
            'esta_activo', 'puede_agregar_usuarios', 'puede_agregar_centros',
            'centros', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']
    
    def get_centros(self, obj):
        """Retorna información básica de los centros del tenant"""
        centros = obj.get_centros_disponibles()
        return [{
            'id': centro.id,
            'codigo': centro.codigo,
            'nombre': centro.nombre,
            'activo': centro.activo
        } for centro in centros]

class TenantCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear tenant"""
    
    class Meta:
        model = Tenant
        fields = [
            'nombre', 'codigo', 'descripcion', 'limite_usuarios', 
            'limite_centros', 'email_contacto', 'telefono_contacto',
            'tipo_facturacion', 'fecha_vencimiento', 'configuracion'
        ]
    
    def validate_codigo(self, value):
        """Validar que el código sea único"""
        if Tenant.objects.filter(codigo=value.upper()).exists():
            raise serializers.ValidationError("Ya existe un tenant con este código")
        return value.upper()
    
    def create(self, validated_data):
        """Crear tenant con usuario creador"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class UsuarioTenantSerializer(serializers.ModelSerializer):
    """Serializer para la relación usuario-tenant"""
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    tenant_nombre = serializers.CharField(source='tenant.nombre', read_only=True)
    tenant_codigo = serializers.CharField(source='tenant.codigo', read_only=True)
    esta_activo = serializers.ReadOnlyField()
    centros_disponibles = serializers.SerializerMethodField()
    
    class Meta:
        model = UsuarioTenant
        fields = [
            'id', 'usuario', 'tenant', 'usuario_nombre', 'usuario_email',
            'tenant_nombre', 'tenant_codigo', 'activo', 'es_administrador_tenant',
            'fecha_asignacion', 'fecha_vencimiento', 'configuracion_tenant',
            'esta_activo', 'centros_disponibles', 'created_at', 'updated_at'
        ]
        read_only_fields = ['fecha_asignacion', 'created_at', 'updated_at']
    
    def get_centros_disponibles(self, obj):
        """Retorna los centros disponibles para este usuario en este tenant"""
        centros = obj.get_centros_disponibles()
        return [{
            'id': centro.id,
            'codigo': centro.codigo,
            'nombre': centro.nombre
        } for centro in centros]

class AsignarUsuarioTenantSerializer(serializers.Serializer):
    """Serializer para asignar usuario a tenant"""
    usuario_id = serializers.IntegerField()
    tenant_id = serializers.IntegerField()
    es_administrador_tenant = serializers.BooleanField(default=False)
    fecha_vencimiento = serializers.DateTimeField(required=False, allow_null=True)
    centros_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    
    def validate(self, data):
        """Validaciones personalizadas"""
        from MasterModels.modelos_auth.usuario import Usuario
        
        # Verificar que el usuario existe
        try:
            usuario = Usuario.objects.get(id=data['usuario_id'])
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")
        
        # Verificar que el tenant existe
        try:
            tenant = Tenant.objects.get(id=data['tenant_id'])
        except Tenant.DoesNotExist:
            raise serializers.ValidationError("Tenant no encontrado")
        
        # Verificar límites del tenant
        if not tenant.puede_agregar_usuarios:
            raise serializers.ValidationError(
                f"El tenant {tenant.nombre} ha alcanzado su límite de usuarios"
            )
        
        # Verificar que no exista ya la asignación
        if UsuarioTenant.objects.filter(usuario=usuario, tenant=tenant).exists():
            raise serializers.ValidationError("El usuario ya está asignado a este tenant")
        
        # Validar centros si se proporcionan
        if 'centros_ids' in data:
            centros_invalidos = []
            for centro_id in data['centros_ids']:
                try:
                    centro = Centro.objects.get(id=centro_id)
                    if centro.tenant != tenant:
                        centros_invalidos.append(centro_id)
                except Centro.DoesNotExist:
                    centros_invalidos.append(centro_id)
            
            if centros_invalidos:
                raise serializers.ValidationError(
                    f"Centros inválidos o no pertenecen al tenant: {centros_invalidos}"
                )
        
        data['usuario'] = usuario
        data['tenant'] = tenant
        return data
    
    def save(self):
        """Crear la asignación usuario-tenant"""
        usuario = self.validated_data['usuario']
        tenant = self.validated_data['tenant']
        
        # Crear la asignación
        usuario_tenant = UsuarioTenant.objects.create(
            usuario=usuario,
            tenant=tenant,
            es_administrador_tenant=self.validated_data.get('es_administrador_tenant', False),
            fecha_vencimiento=self.validated_data.get('fecha_vencimiento'),
            asignado_por=self.context['request'].user
        )
        
        # Asignar centros si se proporcionan
        if 'centros_ids' in self.validated_data:
            centros = Centro.objects.filter(
                id__in=self.validated_data['centros_ids'],
                tenant=tenant
            )
            usuario_tenant.centros.set(centros)
        
        return usuario_tenant

class TenantEstadisticasSerializer(serializers.Serializer):
    """Serializer para estadísticas de tenants"""
    total_tenants = serializers.IntegerField()
    tenants_activos = serializers.IntegerField()
    tenants_demo = serializers.IntegerField()
    total_usuarios = serializers.IntegerField()
    total_centros = serializers.IntegerField()
    distribucion_por_tipo = serializers.DictField()
    tenants_por_vencer = serializers.ListField()
    
class CentroTenantSerializer(serializers.ModelSerializer):
    """Serializer para centros con información de tenant"""
    tenant_nombre = serializers.CharField(source='tenant.nombre', read_only=True)
    tenant_codigo = serializers.CharField(source='tenant.codigo', read_only=True)
    
    class Meta:
        model = Centro
        fields = [
            'id', 'codigo', 'nombre', 'direccion', 'localidad',
            'telefono', 'horario', 'mail', 'web', 'observaciones',
            'activo', 'tenant', 'tenant_nombre', 'tenant_codigo'
        ]
    
    def validate(self, data):
        """Validar que el tenant puede agregar más centros"""
        if not self.instance:  # Creación
            tenant = data.get('tenant')
            if tenant and not tenant.puede_agregar_centros:
                raise serializers.ValidationError(
                    f"El tenant {tenant.nombre} ha alcanzado su límite de centros"
                )
        return data