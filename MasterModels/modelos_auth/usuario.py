from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from ..universal import AuditModel, TenantModel

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un email')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        # Asignar tenant demo automáticamente a usuarios nuevos (excepto superusers)
        if not extra_fields.get('is_superuser', False):
            user.asignar_tenant_demo()
        
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('activo', True)
        
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin, AuditModel, TenantModel):
    """Usuario del sistema con autenticación y permisos"""
    
    # Información básica
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    
    # Relaciones (temporal nullable para migración)
    idrol = models.ForeignKey('Rol', on_delete=models.PROTECT, null=True, blank=True)
    idprofesional = models.ForeignKey('Profesional', on_delete=models.SET_NULL, blank=True, null=True)
    idcentro = models.ForeignKey('Centro', on_delete=models.SET_NULL, blank=True, null=True)
    
    # Relación many-to-many con tenants
    tenants = models.ManyToManyField(
        'MasterModels.Tenant',
        through='MasterModels.UsuarioTenant',
        through_fields=('usuario', 'tenant'),
        related_name='usuarios',
        verbose_name="Tenants",
        help_text="Tenants a los que el usuario tiene acceso"
    )
    
    # Estados del usuario
    activo = models.BooleanField(default=True)
    email_verificado = models.BooleanField(default=False)
    debe_cambiar_password = models.BooleanField(default=True)
    
    # Control de acceso
    ultimo_acceso = models.DateTimeField(blank=True, null=True)
    intentos_fallidos = models.IntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(blank=True, null=True)
    
    # Configuraciones personales
    configuracion = models.JSONField(default=dict, help_text="Configuraciones personales del usuario")
    
    # Django fields
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Override groups and user_permissions to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'AUTH - Usuarios'
        ordering = ['apellido', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.email})"
    
    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"
    
    def get_short_name(self):
        return self.nombre
    
    def tiene_permiso(self, modulo, accion):
        """Verifica si el usuario tiene un permiso específico"""
        if not self.activo or self.esta_bloqueado():
            return False
        
        if self.is_superuser:
            return True
        
        return self.idrol.tiene_permiso(modulo, accion)
    
    def esta_bloqueado(self):
        """Verifica si el usuario está bloqueado"""
        if self.bloqueado_hasta:
            return timezone.now() < self.bloqueado_hasta
        return False
    
    def bloquear_usuario(self, minutos=30):
        """Bloquea el usuario por un tiempo determinado"""
        self.bloqueado_hasta = timezone.now() + timezone.timedelta(minutes=minutos)
        self.save()
    
    def desbloquear_usuario(self):
        """Desbloquea el usuario"""
        self.bloqueado_hasta = None
        self.intentos_fallidos = 0
        self.save()
    
    def incrementar_intentos_fallidos(self):
        """Incrementa los intentos fallidos de login"""
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 5:  # Bloquear después de 5 intentos
            self.bloquear_usuario()
        self.save()
    
    def reset_intentos_fallidos(self):
        """Resetea los intentos fallidos al hacer login exitoso"""
        self.intentos_fallidos = 0
        self.ultimo_acceso = timezone.now()
        self.save()
    
    def puede_ver_centro(self, centro_id):
        """Verifica si puede ver datos de un centro específico"""
        if self.is_superuser or self.idrol.nivel >= 8:
            return True
        
        if self.idcentro:
            return self.idcentro.id == centro_id
        
        return False
    
    def puede_ver_profesional(self, profesional_id):
        """Verifica si puede ver datos de un profesional específico"""
        if self.is_superuser or self.idrol.nivel >= 8:
            return True
        
        if self.idprofesional:
            return self.idprofesional.id == profesional_id
        
        return False
    
    def get_centros_permitidos(self):
        """Retorna los centros a los que tiene acceso"""
        from MasterModels.modelos_centros.centro import Centro
        
        if self.is_superuser or self.idrol.nivel >= 8:
            return Centro.objects.filter(activo=True)
        
        if self.idcentro:
            return Centro.objects.filter(id=self.idcentro.id, activo=True)
        
        return Centro.objects.none()
    
    def get_profesionales_permitidos(self):
        """Retorna los profesionales a los que tiene acceso"""
        from MasterModels.modelos_profesionales.profesional import Profesional
        
        if self.is_superuser or self.idrol.nivel >= 8:
            return Profesional.objects.filter(activo=True)
        
        if self.idprofesional:
            return Profesional.objects.filter(id=self.idprofesional.id, activo=True)
        
        if self.idcentro:
            # Profesionales que atienden en el centro del usuario
            return Profesional.objects.filter(
                profesionalpracticacentro__idcentro=self.idcentro,
                activo=True
            ).distinct()
        
        return Profesional.objects.none()
    
    def configurar_usuario(self, clave, valor):
        """Configura una preferencia del usuario"""
        if not self.configuracion:
            self.configuracion = {}
        self.configuracion[clave] = valor
        self.save()
    
    def get_configuracion(self, clave, default=None):
        """Obtiene una configuración del usuario"""
        return self.configuracion.get(clave, default) if self.configuracion else default
    
    def es_profesional(self):
        """Verifica si el usuario es un profesional médico"""
        return self.idprofesional is not None
    
    def es_admin_centro(self):
        """Verifica si es administrador de centro"""
        return self.idrol.nivel >= 8
    
    def puede_aprobar_liquidaciones(self):
        """Verifica si puede aprobar liquidaciones"""
        return self.tiene_permiso('financieros', 'aprobar_liquidaciones')
    
    # Métodos para manejo de tenants
    def get_tenants_activos(self):
        """Retorna los tenants activos del usuario"""
        from MasterModels.modelos_general.usuario_tenant import UsuarioTenant
        return UsuarioTenant.objects.filter(
            usuario=self,
            activo=True,
            tenant__activo=True
        ).select_related('tenant')
    
    def puede_acceder_tenant(self, tenant):
        """Verifica si el usuario puede acceder a un tenant específico"""
        if self.is_superuser:
            return True
            
        from MasterModels.modelos_general.usuario_tenant import UsuarioTenant
        return UsuarioTenant.objects.filter(
            usuario=self,
            tenant=tenant,
            activo=True
        ).exists()
    
    def get_centros_por_tenant(self, tenant):
        """Retorna los centros disponibles para el usuario en un tenant específico"""
        if not self.puede_acceder_tenant(tenant):
            return tenant.centros.none()
            
        from MasterModels.modelos_general.usuario_tenant import UsuarioTenant
        usuario_tenant = UsuarioTenant.objects.filter(
            usuario=self,
            tenant=tenant,
            activo=True
        ).first()
        
        if usuario_tenant:
            return usuario_tenant.get_centros_disponibles()
        
        return tenant.centros.none()
    
    def es_admin_tenant(self, tenant):
        """Verifica si el usuario es administrador de un tenant específico"""
        if self.is_superuser:
            return True
            
        from MasterModels.modelos_general.usuario_tenant import UsuarioTenant
        return UsuarioTenant.objects.filter(
            usuario=self,
            tenant=tenant,
            es_administrador_tenant=True,
            activo=True
        ).exists()
    
    def asignar_tenant_demo(self):
        """Asigna el tenant demo al usuario (usado en registro)"""
        from MasterModels.modelos_general.usuario_tenant import UsuarioTenant
        return UsuarioTenant.asignar_tenant_demo(self)
    
    def get_tenant_actual(self):
        """Retorna el tenant actual del usuario (el primero activo)"""
        tenant_activo = self.get_tenants_activos().first()
        return tenant_activo.tenant if tenant_activo else None