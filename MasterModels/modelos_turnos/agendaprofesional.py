from django.db import models
from ..universal import AuditModel, TenantModel

class AgendaProfesional(AuditModel, TenantModel):
    """Configuración de agenda de cada profesional por centro"""
    idprofesional = models.ForeignKey('Profesional', on_delete=models.CASCADE)
    idcentro = models.ForeignKey('Centro', on_delete=models.CASCADE)
    idespecialidadpractica = models.ForeignKey('EspecialidadPractica', on_delete=models.CASCADE)
    
    # Configuración de horarios
    dia_semana = models.IntegerField(choices=[
        (1, 'Lunes'), (2, 'Martes'), (3, 'Miércoles'), 
        (4, 'Jueves'), (5, 'Viernes'), (6, 'Sábado'), (7, 'Domingo')
    ])
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    # Configuración de turnos
    duracion_turno_minutos = models.IntegerField(default=30)  # Duración de cada turno en minutos
    dias_adelanto = models.IntegerField(default=30)  # Días de anticipación para agendar
    
    # Control de disponibilidad
    activo = models.BooleanField(default=True)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Agenda de Profesional'
        verbose_name_plural = 'TURN - Agendas de Profesionales'
        unique_together = ['idprofesional', 'idcentro', 'idespecialidadpractica', 'dia_semana', 'hora_inicio']
        
    def __str__(self):
        dias = {1: 'Lun', 2: 'Mar', 3: 'Mié', 4: 'Jue', 5: 'Vie', 6: 'Sáb', 7: 'Dom'}
        return f'{self.idprofesional.apellido} - {self.idcentro.codigo} - {dias[self.dia_semana]} {self.hora_inicio}-{self.hora_fin}'