from django.db import models
from ..universal import AuditModel, TenantModel

class PacienteHistoriaReceta(AuditModel, TenantModel):
    """ Recetas médicas asociadas a historias clínicas """
    idpacientehistoria = models.ForeignKey('PacienteHistoria', on_delete=models.CASCADE)
    
    # Tipo de receta
    tipo_receta = models.CharField(max_length=20, choices=[
        ('MEDICAMENTO', 'Medicamento'),
        ('ESTUDIO', 'Estudio médico'),
        ('LABORATORIO', 'Análisis de laboratorio'),
        ('DERIVACION', 'Derivación'),
        ('TERAPIA', 'Terapia/Rehabilitación'),
        ('OTRO', 'Otro')
    ], default='MEDICAMENTO')
    
    # Información del item recetado
    item = models.CharField(max_length=200, help_text="Medicamento, estudio o procedimiento")
    dosis = models.CharField(max_length=100, blank=True, null=True, help_text="Dosis del medicamento")
    frecuencia = models.CharField(max_length=100, blank=True, null=True, help_text="Frecuencia de administración")
    duracion = models.CharField(max_length=100, blank=True, null=True, help_text="Duración del tratamiento")
    
    # Instrucciones
    indicaciones = models.TextField(help_text="Indicaciones específicas")
    observaciones = models.TextField(blank=True, null=True, help_text="Observaciones adicionales")
    
    # Control
    urgente = models.BooleanField(default=False, help_text="Receta urgente o prioritaria")
    fecha_vencimiento = models.DateField(blank=True, null=True, help_text="Fecha límite para realizar")
    completado = models.BooleanField(default=False, help_text="Paciente completó la indicación")
    fecha_completado = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Historia Receta'
        verbose_name_plural = 'PACI - Historia/Receta por paciente'

    def __str__(self):
        return f'{self.item} - {self.tipo_receta} - {self.idpacientehistoria.fecha}'
    
    @property
    def esta_vencido(self):
        """Verifica si la receta está vencida"""
        if self.fecha_vencimiento:
            from django.utils import timezone
            return timezone.now().date() > self.fecha_vencimiento
        return False
    
    def marcar_completado(self):
        """Marca la receta como completada"""
        from django.utils import timezone
        self.completado = True
        self.fecha_completado = timezone.now().date()
        self.save()