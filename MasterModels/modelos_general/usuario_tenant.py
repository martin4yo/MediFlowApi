from django.db import models
from django.utils import timezone

class UsuarioTenant(models.Model):
    """
    Tabla intermedia para la relación many-to-many entre Usuario y Tenant.
    Permite que un usuario pertenezca a múltiples tenants con diferentes roles.
    """
    
    usuario = models.ForeignKey(
        'MasterModels.Usuario',
        on_delete=models.CASCADE,
        related_name='usuario_tenants',
        verbose_name="Usuario"
    )
    
    tenant = models.ForeignKey(
        'MasterModels.Tenant',
        on_delete=models.CASCADE,
        related_name='tenant_usuarios',
        verbose_name="Tenant"
    )
    
    # Centros específicos a los que el usuario tiene acceso dentro de este tenant
    centros = models.ManyToManyField(
        'MasterModels.Centro',
        blank=True,
        related_name='usuarios_autorizados',
        verbose_name="Centros autorizados",
        help_text="Centros específicos a los que el usuario tiene acceso en este tenant"
    )
    
    # Información de la asignación
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Si la asignación del usuario al tenant está activa"
    )
    
    es_administrador_tenant = models.BooleanField(
        default=False,
        verbose_name="Administrador del Tenant",
        help_text="Si el usuario es administrador de este tenant específico"
    )
    
    fecha_asignacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de asignación"
    )
    
    fecha_vencimiento = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha de vencimiento",
        help_text="Fecha hasta la cual el usuario puede acceder a este tenant"
    )
    
    # Configuración específica para este tenant
    configuracion_tenant = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Configuración específica del tenant",
        help_text="Configuraciones específicas del usuario para este tenant"
    )
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    asignado_por = models.ForeignKey(
        'MasterModels.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asignaciones_tenant_realizadas',
        verbose_name="Asignado por"
    )
    
    class Meta:
        db_table = 'usuario_tenant'
        verbose_name = 'Usuario-Tenant'
        verbose_name_plural = 'Usuarios-Tenants'
        unique_together = [('usuario', 'tenant')]
        ordering = ['tenant', 'usuario']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.tenant.nombre}"
    
    @property
    def esta_activo(self):
        """Verifica si la asignación está activa y no vencida"""
        if not self.activo:
            return False
            
        if self.fecha_vencimiento and self.fecha_vencimiento < timezone.now():
            return False
            
        return self.tenant.esta_activo
    
    def get_centros_disponibles(self):
        """Retorna los centros disponibles para este usuario en este tenant"""
        if self.centros.exists():
            # Si tiene centros específicos asignados
            return self.centros.filter(activo=True)
        else:
            # Si no tiene centros específicos, puede acceder a todos los del tenant
            return self.tenant.get_centros_disponibles()
    
    def puede_acceder_centro(self, centro):
        """Verifica si el usuario puede acceder a un centro específico"""
        if not self.esta_activo:
            return False
            
        # Verificar que el centro pertenezca al tenant
        if centro.tenant != self.tenant:
            return False
            
        # Si tiene centros específicos asignados
        if self.centros.exists():
            return self.centros.filter(id=centro.id, activo=True).exists()
        
        # Si no tiene centros específicos, puede acceder a todos los del tenant
        return centro.activo
    
    @classmethod
    def asignar_tenant_demo(cls, usuario):
        """Asigna el tenant demo a un usuario nuevo"""
        from .tenant import Tenant
        
        tenant_demo = Tenant.get_tenant_demo()
        
        # Verificar si ya tiene asignado el tenant demo
        if cls.objects.filter(usuario=usuario, tenant=tenant_demo).exists():
            return cls.objects.get(usuario=usuario, tenant=tenant_demo)
        
        # Crear la asignación
        asignacion = cls.objects.create(
            usuario=usuario,
            tenant=tenant_demo,
            activo=True
        )
        
        # Asignar todos los centros del tenant demo
        centros_demo = tenant_demo.get_centros_disponibles()
        if centros_demo.exists():
            asignacion.centros.set(centros_demo)
        
        return asignacion