from django.db import models
from ..universal import AuditModel, TenantModel

class ExcepcionAgenda(AuditModel, TenantModel):
    """Excepciones en la agenda: vacaciones, feriados, licencias, etc."""
    idprofesional = models.ForeignKey('Profesional', on_delete=models.CASCADE, blank=True, null=True)
    idcentro = models.ForeignKey('Centro', on_delete=models.CASCADE, blank=True, null=True)
    
    tipo = models.CharField(max_length=20, choices=[
        ('FERIADO', 'Feriado'),
        ('VACACIONES', 'Vacaciones'),
        ('LICENCIA', 'Licencia'),
        ('CAPACITACION', 'Capacitación'),
        ('CIERRE_CENTRO', 'Cierre de Centro'),
        ('OTRO', 'Otro')
    ])
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    hora_inicio = models.TimeField(blank=True, null=True)  # Para excepciones parciales del día
    hora_fin = models.TimeField(blank=True, null=True)
    
    descripcion = models.CharField(max_length=200)
    observaciones = models.TextField(blank=True, null=True)
    
    # Si es True, afecta a todo el centro, si es False, solo al profesional
    afecta_centro_completo = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Excepción de Agenda'
        verbose_name_plural = 'TURN - Excepciones de Agenda'
        
    def __str__(self):
        if self.afecta_centro_completo:
            return f'{self.tipo} - {self.idcentro.nombre} - {self.fecha_inicio}'
        return f'{self.tipo} - {self.idprofesional.apellido} - {self.fecha_inicio}'