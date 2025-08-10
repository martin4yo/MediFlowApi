from django.db import models
from django.utils import timezone
from ..universal import AuditModel, TenantModel

class Notificacion(AuditModel, TenantModel):
    """Registro de notificaciones enviadas"""
    
    # Destinatario
    destinatario_email = models.EmailField(blank=True, null=True)
    destinatario_telefono = models.CharField(max_length=20, blank=True, null=True)
    destinatario_nombre = models.CharField(max_length=200)
    
    # Referencias
    idpaciente = models.ForeignKey('Paciente', on_delete=models.SET_NULL, blank=True, null=True)
    idturno = models.ForeignKey('Turno', on_delete=models.SET_NULL, blank=True, null=True)
    idcentro = models.ForeignKey('Centro', on_delete=models.CASCADE)
    
    # Contenido
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
    
    asunto = models.CharField(max_length=200, blank=True, null=True)
    contenido = models.TextField()
    
    # Estado
    estado = models.CharField(max_length=20, choices=[
        ('PENDIENTE', 'Pendiente'),
        ('ENVIANDO', 'Enviando'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('ERROR', 'Error'),
        ('CANCELADO', 'Cancelado')
    ], default='PENDIENTE')
    
    # Control de envío
    fecha_programada = models.DateTimeField(default=timezone.now)
    fecha_enviado = models.DateTimeField(blank=True, null=True)
    fecha_entregado = models.DateTimeField(blank=True, null=True)
    
    intentos = models.IntegerField(default=0)
    max_intentos = models.IntegerField(default=3)
    
    # Respuesta del servicio
    respuesta_externa = models.JSONField(default=dict, blank=True)
    mensaje_error = models.TextField(blank=True, null=True)
    
    # Configuración
    prioridad = models.CharField(max_length=10, choices=[
        ('BAJA', 'Baja'),
        ('NORMAL', 'Normal'), 
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente')
    ], default='NORMAL')
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'NOT - Notificaciones'
        ordering = ['-fecha_programada']
    
    def __str__(self):
        return f'{self.get_tipo_display()} - {self.destinatario_nombre} - {self.estado}'
    
    def marcar_enviado(self):
        """Marca la notificación como enviada"""
        self.estado = 'ENVIADO'
        self.fecha_enviado = timezone.now()
        self.save()
    
    def marcar_entregado(self):
        """Marca la notificación como entregada"""
        self.estado = 'ENTREGADO'
        self.fecha_entregado = timezone.now()
        self.save()
    
    def marcar_error(self, mensaje_error):
        """Marca la notificación con error"""
        self.estado = 'ERROR'
        self.mensaje_error = mensaje_error
        self.intentos += 1
        self.save()
    
    def puede_reintentar(self):
        """Verifica si se puede reintentar el envío"""
        return self.intentos < self.max_intentos and self.estado == 'ERROR'
    
    @classmethod
    def crear_desde_plantilla(cls, plantilla, destinatario_datos, variables, **kwargs):
        """Crea una notificación desde una plantilla"""
        contenido_renderizado = plantilla.renderizar(variables)
        
        notificacion = cls.objects.create(
            tipo=plantilla.tipo,
            canal=plantilla.canal,
            asunto=contenido_renderizado['asunto'],
            contenido=contenido_renderizado['contenido'],
            destinatario_nombre=destinatario_datos.get('nombre', ''),
            destinatario_email=destinatario_datos.get('email', ''),
            destinatario_telefono=destinatario_datos.get('telefono', ''),
            **kwargs
        )
        
        return notificacion