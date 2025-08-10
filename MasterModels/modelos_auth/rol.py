from django.db import models
from ..universal import AuditModel, TenantModel

class Rol(AuditModel, TenantModel):
    """Roles del sistema con permisos específicos"""
    
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    # Jerarquía de roles
    nivel = models.IntegerField(default=1, help_text="Nivel jerárquico del rol (1=más bajo, 10=más alto)")
    
    # Estados del rol
    activo = models.BooleanField(default=True)
    es_sistema = models.BooleanField(default=False, help_text="Rol del sistema que no se puede eliminar")
    
    # Permisos específicos por módulo
    permisos_turnos = models.JSONField(default=dict, help_text="Permisos sobre turnos")
    permisos_pacientes = models.JSONField(default=dict, help_text="Permisos sobre pacientes")
    permisos_financieros = models.JSONField(default=dict, help_text="Permisos financieros")
    permisos_reportes = models.JSONField(default=dict, help_text="Permisos de reportes")
    permisos_admin = models.JSONField(default=dict, help_text="Permisos administrativos")
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'AUTH - Roles'
        ordering = ['nivel', 'nombre']
    
    def __str__(self):
        return self.nombre
    
    def tiene_permiso(self, modulo, accion):
        """Verifica si el rol tiene un permiso específico"""
        permisos_modulo = getattr(self, f'permisos_{modulo}', {})
        return permisos_modulo.get(accion, False)
    
    def get_permisos_completos(self):
        """Retorna todos los permisos del rol organizados"""
        return {
            'turnos': self.permisos_turnos,
            'pacientes': self.permisos_pacientes,
            'financieros': self.permisos_financieros,
            'reportes': self.permisos_reportes,
            'admin': self.permisos_admin
        }
    
    def puede_ver_datos_financieros(self):
        """Verifica si puede ver información financiera"""
        return self.permisos_financieros.get('ver_pagos', False) or \
               self.permisos_financieros.get('ver_liquidaciones', False)
    
    def puede_administrar(self):
        """Verifica si tiene permisos de administración"""
        return any(self.permisos_admin.values()) or self.nivel >= 8
    
    @classmethod
    def crear_roles_sistema(cls):
        """Crea los roles básicos del sistema"""
        roles_base = [
            {
                'nombre': 'SUPER_ADMIN',
                'descripcion': 'Administrador principal con todos los permisos',
                'nivel': 10,
                'es_sistema': True,
                'permisos_turnos': {'crear': True, 'ver': True, 'editar': True, 'eliminar': True, 'gestionar_agenda': True},
                'permisos_pacientes': {'crear': True, 'ver': True, 'editar': True, 'eliminar': True, 'ver_historia': True},
                'permisos_financieros': {'ver_pagos': True, 'crear_pagos': True, 'ver_liquidaciones': True, 'aprobar_liquidaciones': True},
                'permisos_reportes': {'ejecutar': True, 'crear': True, 'editar': True, 'ver_todos': True},
                'permisos_admin': {'gestionar_usuarios': True, 'gestionar_roles': True, 'configurar_sistema': True}
            },
            {
                'nombre': 'ADMIN_CENTRO',
                'descripcion': 'Administrador de centro médico',
                'nivel': 8,
                'es_sistema': True,
                'permisos_turnos': {'crear': True, 'ver': True, 'editar': True, 'eliminar': False, 'gestionar_agenda': True},
                'permisos_pacientes': {'crear': True, 'ver': True, 'editar': True, 'eliminar': False, 'ver_historia': True},
                'permisos_financieros': {'ver_pagos': True, 'crear_pagos': True, 'ver_liquidaciones': True, 'aprobar_liquidaciones': False},
                'permisos_reportes': {'ejecutar': True, 'crear': False, 'editar': False, 'ver_todos': True},
                'permisos_admin': {'gestionar_usuarios': False, 'gestionar_roles': False, 'configurar_sistema': False}
            },
            {
                'nombre': 'PROFESIONAL',
                'descripcion': 'Profesional médico',
                'nivel': 6,
                'es_sistema': True,
                'permisos_turnos': {'crear': False, 'ver': True, 'editar': True, 'eliminar': False, 'gestionar_agenda': True},
                'permisos_pacientes': {'crear': False, 'ver': True, 'editar': True, 'eliminar': False, 'ver_historia': True},
                'permisos_financieros': {'ver_pagos': False, 'crear_pagos': False, 'ver_liquidaciones': True, 'aprobar_liquidaciones': False},
                'permisos_reportes': {'ejecutar': True, 'crear': False, 'editar': False, 'ver_todos': False},
                'permisos_admin': {'gestionar_usuarios': False, 'gestionar_roles': False, 'configurar_sistema': False}
            },
            {
                'nombre': 'SECRETARIA',
                'descripcion': 'Personal administrativo/secretaría',
                'nivel': 4,
                'es_sistema': True,
                'permisos_turnos': {'crear': True, 'ver': True, 'editar': True, 'eliminar': False, 'gestionar_agenda': False},
                'permisos_pacientes': {'crear': True, 'ver': True, 'editar': True, 'eliminar': False, 'ver_historia': False},
                'permisos_financieros': {'ver_pagos': True, 'crear_pagos': True, 'ver_liquidaciones': False, 'aprobar_liquidaciones': False},
                'permisos_reportes': {'ejecutar': False, 'crear': False, 'editar': False, 'ver_todos': False},
                'permisos_admin': {'gestionar_usuarios': False, 'gestionar_roles': False, 'configurar_sistema': False}
            },
            {
                'nombre': 'CONTADOR',
                'descripción': 'Personal contable/financiero',
                'nivel': 5,
                'es_sistema': True,
                'permisos_turnos': {'crear': False, 'ver': True, 'editar': False, 'eliminar': False, 'gestionar_agenda': False},
                'permisos_pacientes': {'crear': False, 'ver': True, 'editar': False, 'eliminar': False, 'ver_historia': False},
                'permisos_financieros': {'ver_pagos': True, 'crear_pagos': False, 'ver_liquidaciones': True, 'aprobar_liquidaciones': True},
                'permisos_reportes': {'ejecutar': True, 'crear': False, 'editar': False, 'ver_todos': False},
                'permisos_admin': {'gestionar_usuarios': False, 'gestionar_roles': False, 'configurar_sistema': False}
            }
        ]
        
        for rol_data in roles_base:
            rol, created = cls.objects.get_or_create(
                nombre=rol_data['nombre'],
                defaults=rol_data
            )
            if created:
                print(f"Rol creado: {rol.nombre}")
        
        return cls.objects.filter(es_sistema=True)