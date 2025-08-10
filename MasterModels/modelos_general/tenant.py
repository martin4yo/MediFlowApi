from django.db import models
from django.core.exceptions import ValidationError
from .centro import Centro
from django.utils import timezone

class Tenant(models.Model):
    """
    Modelo para gestionar multi-tenancy.
    Cada tenant puede tener múltiples centros médicos.
    """
    
    # Información básica
    nombre = models.CharField(
        max_length=200, 
        verbose_name="Nombre del Tenant",
        help_text="Nombre de la organización o empresa"
    )
    
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código único",
        help_text="Código único identificador del tenant"
    )
    
    descripcion = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Descripción",
        help_text="Descripción del tenant"
    )
    
    # Estado y configuración
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Si el tenant está activo y puede ser utilizado"
    )
    
    es_demo = models.BooleanField(
        default=False,
        verbose_name="Es Demo",
        help_text="Indica si es el tenant demo para nuevos usuarios"
    )
    
    # Límites del tenant
    limite_usuarios = models.PositiveIntegerField(
        default=10,
        verbose_name="Límite de usuarios",
        help_text="Número máximo de usuarios permitidos para este tenant"
    )
    
    limite_centros = models.PositiveIntegerField(
        default=1,
        verbose_name="Límite de centros",
        help_text="Número máximo de centros médicos permitidos"
    )
    
    # Información de contacto
    email_contacto = models.EmailField(
        blank=True, 
        null=True,
        verbose_name="Email de contacto"
    )
    
    telefono_contacto = models.CharField(
        max_length=20,
        blank=True, 
        null=True,
        verbose_name="Teléfono de contacto"
    )
    
    # Configuración de facturación
    tipo_facturacion = models.CharField(
        max_length=20,
        choices=[
            ('mensual', 'Mensual'),
            ('anual', 'Anual'),
            ('demo', 'Demo'),
            ('cortesia', 'Cortesía')
        ],
        default='mensual',
        verbose_name="Tipo de facturación"
    )
    
    fecha_vencimiento = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Fecha de vencimiento",
        help_text="Fecha hasta la cual el tenant puede operar"
    )
    
    # Configuración personalizada (JSON)
    configuracion = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Configuración personalizada",
        help_text="Configuraciones específicas del tenant en formato JSON"
    )
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    created_by = models.ForeignKey(
        'MasterModels.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tenants_creados',
        verbose_name="Creado por"
    )
    
    class Meta:
        db_table = 'tenant'
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
        ordering = ['nombre']
        
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Solo puede haber un tenant demo
        if self.es_demo:
            existing_demo = Tenant.objects.filter(es_demo=True).exclude(pk=self.pk)
            if existing_demo.exists():
                raise ValidationError("Solo puede existir un tenant demo.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def centros_count(self):
        """Número de centros asociados"""
        return self.centros.count()
    
    @property
    def usuarios_count(self):
        """Número de usuarios asociados"""
        return self.usuarios.count()
    
    @property
    def esta_activo(self):
        """Verifica si el tenant está activo y no vencido"""
        if not self.activo:
            return False
            
        if self.fecha_vencimiento and self.fecha_vencimiento < timezone.now():
            return False
            
        return True
    
    @property
    def puede_agregar_usuarios(self):
        """Verifica si se pueden agregar más usuarios"""
        return self.usuarios_count < self.limite_usuarios
    
    @property
    def puede_agregar_centros(self):
        """Verifica si se pueden agregar más centros"""
        return self.centros_count < self.limite_centros
    
    def get_centros_disponibles(self):
        """Retorna los centros asociados al tenant"""
        return self.centros.filter(activo=True)
    
    def get_usuarios_activos(self):
        """Retorna los usuarios activos del tenant"""
        return self.usuarios.filter(activo=True)
    
    @classmethod
    def get_tenant_demo(cls):
        """Retorna el tenant demo o lo crea si no existe"""
        tenant_demo, created = cls.objects.get_or_create(
            es_demo=True,
            defaults={
                'nombre': 'Demo MediFlow',
                'codigo': 'DEMO',
                'descripcion': 'Tenant demo para nuevos usuarios',
                'tipo_facturacion': 'demo',
                'limite_usuarios': 100,
                'limite_centros': 5,
                'activo': True
            }
        )
        return tenant_demo
    
    @classmethod
    def crear_tenant_basico(cls, nombre, codigo, email_contacto=None):
        """Crea un tenant básico con configuración estándar"""
        return cls.objects.create(
            nombre=nombre,
            codigo=codigo.upper(),
            email_contacto=email_contacto,
            limite_usuarios=10,
            limite_centros=1,
            tipo_facturacion='mensual',
            activo=True
        )