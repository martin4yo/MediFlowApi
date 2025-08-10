from django.db import models
from ..universal import AuditModel, TenantModel

class PacienteHistoria(AuditModel, TenantModel):
    """ Historia clínica de pacientes por consulta """
    idpaciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)
    idprofesional = models.ForeignKey('Profesional', on_delete=models.CASCADE)
    idturno = models.ForeignKey('Turno', on_delete=models.SET_NULL, blank=True, null=True)
    idespecialidadpractica = models.ForeignKey('EspecialidadPractica', on_delete=models.CASCADE)
    idcentro = models.ForeignKey('Centro', on_delete=models.CASCADE)
    
    # Información básica
    fecha = models.DateField()
    hora_inicio = models.TimeField(blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)
    
    # Información clínica
    motivo_consulta = models.TextField(help_text="Motivo principal de la consulta")
    antecedentes = models.TextField(blank=True, null=True, help_text="Antecedentes relevantes")
    examen_fisico = models.TextField(blank=True, null=True, help_text="Hallazgos del examen físico")
    diagnostico_principal = models.TextField(help_text="Diagnóstico principal")
    diagnosticos_secundarios = models.TextField(blank=True, null=True, help_text="Diagnósticos secundarios")
    
    # Tratamiento y seguimiento
    tratamiento = models.TextField(blank=True, null=True, help_text="Plan de tratamiento")
    indicaciones = models.TextField(blank=True, null=True, help_text="Indicaciones al paciente")
    observaciones = models.TextField(blank=True, null=True, help_text="Observaciones adicionales")
    
    # Control y seguimiento
    proximo_control = models.DateField(blank=True, null=True, help_text="Fecha del próximo control")
    urgente = models.BooleanField(default=False, help_text="Marcado como urgente o derivación")
    derivacion = models.TextField(blank=True, null=True, help_text="Derivación a especialista")
    
    # Signos vitales
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Peso en kg")
    altura = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Altura en cm")
    presion_sistolica = models.IntegerField(blank=True, null=True)
    presion_diastolica = models.IntegerField(blank=True, null=True)
    frecuencia_cardiaca = models.IntegerField(blank=True, null=True)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Historia Clínica'
        verbose_name_plural = 'PACI - Historias por paciente'

    def __str__(self):
        return f'{self.idpaciente} - {self.idprofesional} - {self.fecha}'
    
    @property
    def imc(self):
        """Calcula el índice de masa corporal"""
        if self.peso and self.altura:
            altura_m = float(self.altura) / 100  # convertir cm a metros
            return round(float(self.peso) / (altura_m ** 2), 2)
        return None
    
    @property
    def duracion_consulta(self):
        """Calcula la duración de la consulta en minutos"""
        if self.hora_inicio and self.hora_fin:
            from datetime import datetime, timedelta
            inicio = datetime.combine(self.fecha, self.hora_inicio)
            fin = datetime.combine(self.fecha, self.hora_fin)
            return int((fin - inicio).total_seconds() / 60)
        return None
    
    @property
    def presion_arterial(self):
        """Retorna la presión arterial formateada"""
        if self.presion_sistolica and self.presion_diastolica:
            return f"{self.presion_sistolica}/{self.presion_diastolica}"
        return None
    
    def tiene_recetas(self):
        """Verifica si tiene recetas asociadas"""
        return self.pacientehistoriareceta_set.exists()
    
    def tiene_adjuntos(self):
        """Verifica si tiene archivos adjuntos"""
        return self.pacientehistoriaadjunto_set.exists()