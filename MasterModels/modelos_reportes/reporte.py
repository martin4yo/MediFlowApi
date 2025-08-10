from django.db import models
from ..universal import AuditModel, TenantModel

class Reporte(AuditModel, TenantModel):
    """Definición de reportes personalizables del sistema"""
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    
    categoria = models.CharField(max_length=50, choices=[
        ('FINANCIERO', 'Reportes Financieros'),
        ('MEDICO', 'Reportes Médicos'),
        ('ADMINISTRATIVO', 'Reportes Administrativos'),
        ('ESTADISTICO', 'Reportes Estadísticos'),
        ('AUDITORIA', 'Reportes de Auditoría')
    ])
    
    # Configuración del reporte
    tipo_reporte = models.CharField(max_length=30, choices=[
        ('TURNOS_CENTRO', 'Turnos por Centro'),
        ('TURNOS_PROFESIONAL', 'Turnos por Profesional'),
        ('INGRESOS_PERIODO', 'Ingresos por Período'),
        ('LIQUIDACIONES', 'Liquidaciones Profesionales'),
        ('HISTORIAS_CLINICAS', 'Historias Clínicas'),
        ('PRESCRIPCIONES', 'Prescripciones'),
        ('PACIENTES_ACTIVOS', 'Pacientes Activos'),
        ('OCUPACION_AGENDA', 'Ocupación de Agenda'),
        ('NOTIFICACIONES', 'Estadísticas de Notificaciones'),
        ('PERSONALIZADO', 'Reporte Personalizado')
    ])
    
    # Filtros por defecto
    filtros_default = models.JSONField(default=dict, help_text="Filtros por defecto del reporte")
    
    # Configuración de columnas
    columnas = models.JSONField(
        default=list, 
        help_text="Lista de columnas a mostrar en el reporte"
    )
    
    # Query personalizada (para reportes avanzados)
    query_personalizada = models.TextField(
        blank=True, 
        null=True,
        help_text="Query SQL personalizada para reportes avanzados"
    )
    
    # Configuración de visualización
    permite_grafico = models.BooleanField(default=False)
    tipo_grafico = models.CharField(max_length=20, choices=[
        ('BAR', 'Barras'),
        ('LINE', 'Líneas'),
        ('PIE', 'Circular'),
        ('AREA', 'Área')
    ], blank=True, null=True)
    
    # Permisos
    roles_permitidos = models.JSONField(
        default=list,
        help_text="Roles que pueden ejecutar este reporte"
    )
    
    es_publico = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    
    # Configuración de ejecución
    cache_minutos = models.IntegerField(
        default=0, 
        help_text="Minutos para cachear el resultado (0 = sin cache)"
    )
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'REP - Reportes'
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        return f'{self.nombre} ({self.get_categoria_display()})'
    
    def puede_ejecutar(self, usuario):
        """Verifica si un usuario puede ejecutar este reporte"""
        if not self.activo:
            return False
        
        if self.es_publico:
            return True
        
        if not self.roles_permitidos:
            return True
        
        # Verificar roles del usuario (implementar según sistema de permisos)
        # user_roles = get_user_roles(usuario)
        # return any(role in self.roles_permitidos for role in user_roles)
        return True  # Por ahora permitir a todos
    
    def get_filtros_disponibles(self):
        """Retorna los filtros disponibles según el tipo de reporte"""
        filtros = {
            'TURNOS_CENTRO': [
                {'name': 'centro_id', 'type': 'select', 'label': 'Centro'},
                {'name': 'fecha_desde', 'type': 'date', 'label': 'Fecha Desde'},
                {'name': 'fecha_hasta', 'type': 'date', 'label': 'Fecha Hasta'},
                {'name': 'estado', 'type': 'select', 'label': 'Estado'}
            ],
            'TURNOS_PROFESIONAL': [
                {'name': 'profesional_id', 'type': 'select', 'label': 'Profesional'},
                {'name': 'fecha_desde', 'type': 'date', 'label': 'Fecha Desde'},
                {'name': 'fecha_hasta', 'type': 'date', 'label': 'Fecha Hasta'},
                {'name': 'centro_id', 'type': 'select', 'label': 'Centro'}
            ],
            'INGRESOS_PERIODO': [
                {'name': 'fecha_desde', 'type': 'date', 'label': 'Fecha Desde'},
                {'name': 'fecha_hasta', 'type': 'date', 'label': 'Fecha Hasta'},
                {'name': 'centro_id', 'type': 'select', 'label': 'Centro'},
                {'name': 'tipo_pago', 'type': 'select', 'label': 'Tipo de Pago'}
            ]
        }
        
        return filtros.get(self.tipo_reporte, [])
    
    def get_columnas_disponibles(self):
        """Retorna las columnas disponibles según el tipo de reporte"""
        columnas = {
            'TURNOS_CENTRO': [
                {'key': 'fecha', 'label': 'Fecha', 'type': 'date'},
                {'key': 'paciente', 'label': 'Paciente', 'type': 'string'},
                {'key': 'profesional', 'label': 'Profesional', 'type': 'string'},
                {'key': 'practica', 'label': 'Práctica', 'type': 'string'},
                {'key': 'estado', 'label': 'Estado', 'type': 'string'},
                {'key': 'precio_total', 'label': 'Precio Total', 'type': 'currency'}
            ],
            'INGRESOS_PERIODO': [
                {'key': 'fecha', 'label': 'Fecha', 'type': 'date'},
                {'key': 'centro', 'label': 'Centro', 'type': 'string'},
                {'key': 'profesional', 'label': 'Profesional', 'type': 'string'},
                {'key': 'monto_total', 'label': 'Monto Total', 'type': 'currency'},
                {'key': 'monto_profesional', 'label': 'Monto Profesional', 'type': 'currency'},
                {'key': 'monto_centro', 'label': 'Monto Centro', 'type': 'currency'}
            ]
        }
        
        return columnas.get(self.tipo_reporte, [])