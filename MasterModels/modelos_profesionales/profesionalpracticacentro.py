from django.db import models
from ..universal import AuditModel, TenantModel

class ProfesionalPracticaCentro(AuditModel, TenantModel):
    """ Asignación de profesionales a centros con configuración de horarios """
    idprofesional = models.ForeignKey('Profesional', on_delete=models.CASCADE)
    idcentro = models.ForeignKey('Centro', on_delete=models.CASCADE)
    idespecialidadpractica = models.ForeignKey('EspecialidadPractica', on_delete=models.CASCADE)
    
    # Configuración de horarios por día de semana
    lunes = models.BooleanField(default=False)
    martes = models.BooleanField(default=False)
    miercoles = models.BooleanField(default=False)
    jueves = models.BooleanField(default=False)
    viernes = models.BooleanField(default=False)
    sabado = models.BooleanField(default=False)
    domingo = models.BooleanField(default=False)
    
    # Horarios de atención
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    # Configuración de turnos
    duracion_turno_minutos = models.IntegerField(default=30, help_text="Duración de cada turno en minutos")
    tiempo_descanso_minutos = models.IntegerField(default=0, help_text="Tiempo de descanso entre turnos")
    
    # Configuración de agenda
    dias_anticipacion = models.IntegerField(default=30, help_text="Días de anticipación para agendar turnos")
    turnos_simultaneos = models.IntegerField(default=1, help_text="Cantidad de turnos simultáneos")
    
    # Control de vigencia
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    # Información adicional
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Práctica por Profesional/Centro'
        verbose_name_plural = 'PROS - Prácticas por Profesional/Centro'
        unique_together = ['idprofesional', 'idcentro', 'idespecialidadpractica']

    def __str__(self):
        return f'{self.idprofesional} - {self.idespecialidadpractica.idpractica.nombre} - {self.idcentro.nombre}'
    
    @property
    def dias_atencion(self):
        """Retorna los días de atención como lista"""
        dias = []
        if self.lunes: dias.append('Lunes')
        if self.martes: dias.append('Martes')
        if self.miercoles: dias.append('Miércoles')
        if self.jueves: dias.append('Jueves')
        if self.viernes: dias.append('Viernes')
        if self.sabado: dias.append('Sábado')
        if self.domingo: dias.append('Domingo')
        return dias
    
    @property
    def horario_formateado(self):
        """Retorna el horario en formato legible"""
        return f"{self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}"
    
    def get_dias_semana_numerico(self):
        """Retorna los días de semana en formato numérico (1=Lunes, 7=Domingo)"""
        dias = []
        if self.lunes: dias.append(1)
        if self.martes: dias.append(2)
        if self.miercoles: dias.append(3)
        if self.jueves: dias.append(4)
        if self.viernes: dias.append(5)
        if self.sabado: dias.append(6)
        if self.domingo: dias.append(7)
        return dias
    