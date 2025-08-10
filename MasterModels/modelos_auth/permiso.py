from django.db import models
from ..universal import AuditModel, TenantModel

class Permiso(AuditModel, TenantModel):
    """Permisos específicos del sistema"""
    
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    modulo = models.CharField(max_length=50, choices=[
        ('TURNOS', 'Gestión de Turnos'),
        ('PACIENTES', 'Gestión de Pacientes'),
        ('FINANCIERO', 'Gestión Financiera'),
        ('REPORTES', 'Reportes y Estadísticas'),
        ('ADMIN', 'Administración'),
        ('NOTIFICACIONES', 'Notificaciones'),
        ('SISTEMA', 'Sistema')
    ])
    
    accion = models.CharField(max_length=30, choices=[
        ('CREAR', 'Crear'),
        ('VER', 'Ver/Listar'),
        ('EDITAR', 'Editar/Modificar'),
        ('ELIMINAR', 'Eliminar'),
        ('APROBAR', 'Aprobar'),
        ('EJECUTAR', 'Ejecutar'),
        ('CONFIGURAR', 'Configurar'),
        ('EXPORTAR', 'Exportar')
    ])
    
    nivel_requerido = models.IntegerField(default=1, help_text="Nivel mínimo requerido para este permiso")
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Permiso'
        verbose_name_plural = 'AUTH - Permisos'
        unique_together = ['modulo', 'accion']
        ordering = ['modulo', 'accion']
    
    def __str__(self):
        return f"{self.get_modulo_display()} - {self.get_accion_display()}"
    
    @classmethod
    def crear_permisos_sistema(cls):
        """Crea los permisos básicos del sistema"""
        permisos_base = [
            # Turnos
            ('TURNOS', 'CREAR', 'Crear nuevos turnos', 'turnos.crear', 4),
            ('TURNOS', 'VER', 'Ver listado de turnos', 'turnos.ver', 2),
            ('TURNOS', 'EDITAR', 'Modificar turnos existentes', 'turnos.editar', 4),
            ('TURNOS', 'ELIMINAR', 'Eliminar turnos', 'turnos.eliminar', 6),
            
            # Pacientes
            ('PACIENTES', 'CREAR', 'Crear nuevos pacientes', 'pacientes.crear', 4),
            ('PACIENTES', 'VER', 'Ver listado de pacientes', 'pacientes.ver', 2),
            ('PACIENTES', 'EDITAR', 'Modificar datos de pacientes', 'pacientes.editar', 4),
            ('PACIENTES', 'ELIMINAR', 'Eliminar pacientes', 'pacientes.eliminar', 8),
            
            # Financiero
            ('FINANCIERO', 'VER', 'Ver información financiera', 'financiero.ver', 5),
            ('FINANCIERO', 'CREAR', 'Crear pagos y transacciones', 'financiero.crear', 5),
            ('FINANCIERO', 'APROBAR', 'Aprobar liquidaciones', 'financiero.aprobar', 7),
            ('FINANCIERO', 'EXPORTAR', 'Exportar reportes financieros', 'financiero.exportar', 6),
            
            # Reportes
            ('REPORTES', 'VER', 'Ver reportes básicos', 'reportes.ver', 3),
            ('REPORTES', 'EJECUTAR', 'Ejecutar reportes', 'reportes.ejecutar', 4),
            ('REPORTES', 'CREAR', 'Crear reportes personalizados', 'reportes.crear', 7),
            ('REPORTES', 'EXPORTAR', 'Exportar reportes', 'reportes.exportar', 4),
            
            # Administración
            ('ADMIN', 'VER', 'Ver configuraciones', 'admin.ver', 7),
            ('ADMIN', 'CONFIGURAR', 'Configurar sistema', 'admin.configurar', 9),
            ('ADMIN', 'CREAR', 'Crear usuarios y roles', 'admin.crear', 8),
            ('ADMIN', 'ELIMINAR', 'Eliminar configuraciones', 'admin.eliminar', 9),
            
            # Notificaciones
            ('NOTIFICACIONES', 'VER', 'Ver notificaciones', 'notificaciones.ver', 2),
            ('NOTIFICACIONES', 'CREAR', 'Crear notificaciones', 'notificaciones.crear', 5),
            ('NOTIFICACIONES', 'CONFIGURAR', 'Configurar plantillas', 'notificaciones.configurar', 7),
        ]
        
        for modulo, accion, descripcion, codigo, nivel in permisos_base:
            permiso, created = cls.objects.get_or_create(
                modulo=modulo,
                accion=accion,
                defaults={
                    'nombre': f"{modulo} - {accion}",
                    'codigo': codigo,
                    'descripcion': descripcion,
                    'nivel_requerido': nivel
                }
            )
            if created:
                print(f"Permiso creado: {permiso.codigo}")
        
        return cls.objects.all()
    
    def puede_ser_otorgado_a_nivel(self, nivel):
        """Verifica si el permiso puede ser otorgado a un nivel específico"""
        return nivel >= self.nivel_requerido