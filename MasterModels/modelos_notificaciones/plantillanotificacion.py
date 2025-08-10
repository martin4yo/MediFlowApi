from django.db import models
from ..universal import AuditModel, TenantModel

class PlantillaNotificacion(AuditModel, TenantModel):
    """Plantillas para diferentes tipos de notificaciones"""
    
    tipo = models.CharField(max_length=30, choices=[
        ('CONFIRMACION_TURNO', 'Confirmación de Turno'),
        ('RECORDATORIO_TURNO', 'Recordatorio de Turno'),
        ('CANCELACION_TURNO', 'Cancelación de Turno'),
        ('REAGENDAMIENTO', 'Reagendamiento de Turno'),
        ('RECETA_DIGITAL', 'Receta Digital'),
        ('RESULTADO_ESTUDIO', 'Resultado de Estudio'),
        ('PAGO_CONFIRMADO', 'Pago Confirmado'),
        ('PREPARACION_TURNO', 'Instrucciones de Preparación'),
        ('BIENVENIDA', 'Mensaje de Bienvenida'),
        ('OTRO', 'Otro')
    ])
    
    canal = models.CharField(max_length=20, choices=[
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('WHATSAPP', 'WhatsApp'),
        ('PUSH', 'Notificación Push'),
        ('SISTEMA', 'Notificación del Sistema')
    ])
    
    nombre = models.CharField(max_length=100, help_text="Nombre descriptivo de la plantilla")
    asunto = models.CharField(max_length=200, blank=True, null=True, help_text="Asunto del email o título de la notificación")
    
    # Contenido de la plantilla con variables
    contenido = models.TextField(help_text="Contenido con variables como {{paciente_nombre}}, {{fecha_turno}}, etc.")
    
    # Variables disponibles para esta plantilla
    variables_disponibles = models.JSONField(
        default=list, 
        help_text="Lista de variables disponibles para esta plantilla"
    )
    
    # Configuración
    activa = models.BooleanField(default=True)
    es_default = models.BooleanField(default=False, help_text="Plantilla por defecto para este tipo")
    
    class Meta:
        verbose_name = 'Plantilla de Notificación'
        verbose_name_plural = 'NOT - Plantillas de Notificación'
        unique_together = ['tipo', 'canal', 'es_default']
    
    def __str__(self):
        return f'{self.nombre} ({self.get_tipo_display()} - {self.get_canal_display()})'
    
    def renderizar(self, variables):
        """Renderiza la plantilla con las variables proporcionadas"""
        contenido = self.contenido
        asunto = self.asunto or ""
        
        for variable, valor in variables.items():
            placeholder = f"{{{{{variable}}}}}"
            contenido = contenido.replace(placeholder, str(valor))
            asunto = asunto.replace(placeholder, str(valor))
        
        return {
            'asunto': asunto,
            'contenido': contenido
        }