from django.db.models import Prefetch, Q, Count, Sum, Avg
from django.core.cache import cache
from django.conf import settings
import time
import logging

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """Utilidades para optimización de queries del ORM de Django"""
    
    @staticmethod
    def get_turnos_optimized(filtros=None):
        """Query optimizada para turnos con todas las relaciones"""
        from MasterModels.modelos_turnos.turno import Turno
        
        queryset = Turno.objects.select_related(
            'idpaciente__persona',
            'idprofesional__persona',
            'idpractica',
            'idcentro',
            'idestado'
        ).prefetch_related(
            'pago_set',  # Prefetch pagos relacionados
            'pacientehistoria_set'  # Prefetch historias clínicas
        )
        
        # Aplicar filtros si existen
        if filtros:
            if filtros.get('centro_id'):
                queryset = queryset.filter(idcentro=filtros['centro_id'])
            if filtros.get('profesional_id'):
                queryset = queryset.filter(idprofesional=filtros['profesional_id'])
            if filtros.get('fecha_desde'):
                queryset = queryset.filter(fecha__gte=filtros['fecha_desde'])
            if filtros.get('fecha_hasta'):
                queryset = queryset.filter(fecha__lte=filtros['fecha_hasta'])
            if filtros.get('estado'):
                queryset = queryset.filter(estado=filtros['estado'])
        
        return queryset
    
    @staticmethod
    def get_pacientes_con_estadisticas():
        """Pacientes con estadísticas de turnos y pagos"""
        from MasterModels.modelos_pacientes.paciente import Paciente
        
        return Paciente.objects.select_related('persona').annotate(
            total_turnos=Count('turno'),
            turnos_completados=Count('turno', filter=Q(turno__estado='COMPLETADO')),
            total_pagado=Sum('turno__pago__monto'),
            ultima_consulta=Max('turno__fecha')
        ).prefetch_related(
            Prefetch(
                'turno_set',
                queryset=Turno.objects.select_related('idprofesional__persona', 'idpractica')
                                     .order_by('-fecha')[:5]  # Últimos 5 turnos
            )
        )
    
    @staticmethod
    def get_profesionales_con_agenda():
        """Profesionales con información completa de agenda"""
        from MasterModels.modelos_profesionales.profesional import Profesional
        
        return Profesional.objects.select_related('persona').prefetch_related(
            'profesionalpracticacentro_set__idcentro',
            'profesionalpracticacentro_set__idespecialidadpractica__idpractica',
            Prefetch(
                'turno_set',
                queryset=Turno.objects.select_related('idpaciente__persona')
                                     .filter(fecha__gte=timezone.now().date())
                                     .order_by('fecha', 'hora')
            )
        ).annotate(
            turnos_mes=Count('turno', filter=Q(turno__fecha__month=timezone.now().month)),
            ingresos_mes=Sum('turno__precio_total', filter=Q(turno__fecha__month=timezone.now().month))
        )
    
    @staticmethod 
    def get_reportes_financieros_optimized(fecha_desde, fecha_hasta, centro_id=None):
        """Query optimizada para reportes financieros"""
        from MasterModels.modelos_financieros.pago import Pago
        
        queryset = Pago.objects.select_related(
            'idturno__idpaciente__persona',
            'idturno__idprofesional__persona',
            'idturno__idcentro',
            'idturno__idpractica'
        ).filter(
            fecha_pago__range=[fecha_desde, fecha_hasta]
        )
        
        if centro_id:
            queryset = queryset.filter(idturno__idcentro=centro_id)
        
        return queryset.values(
            'idturno__idcentro__nombre',
            'idturno__idprofesional__persona__nombre',
            'idturno__idprofesional__persona__apellido',
            'tipo_pago',
            'fecha_pago__date'
        ).annotate(
            total_monto=Sum('monto'),
            cantidad_pagos=Count('id')
        ).order_by('-total_monto')
    
    @staticmethod
    def get_dashboard_stats(usuario):
        """Estadísticas optimizadas para dashboard según el usuario"""
        from django.utils import timezone
        from datetime import timedelta
        
        hoy = timezone.now().date()
        mes_actual = timezone.now().replace(day=1).date()
        
        stats = {}
        
        # Filtrar según permisos del usuario
        centros_permitidos = usuario.get_centros_permitidos()
        
        if usuario.tiene_permiso('turnos', 'ver'):
            from MasterModels.modelos_turnos.turno import Turno
            
            turnos_base = Turno.objects.filter(idcentro__in=centros_permitidos)
            
            stats['turnos'] = {
                'hoy': turnos_base.filter(fecha=hoy).count(),
                'mes': turnos_base.filter(fecha__gte=mes_actual).count(),
                'pendientes': turnos_base.filter(
                    fecha__gte=hoy,
                    estado='AGENDADO'
                ).count()
            }
        
        if usuario.tiene_permiso('financieros', 'ver_pagos'):
            from MasterModels.modelos_financieros.pago import Pago
            
            pagos_base = Pago.objects.filter(idturno__idcentro__in=centros_permitidos)
            
            stats['financiero'] = {
                'ingresos_mes': pagos_base.filter(
                    fecha_pago__gte=mes_actual
                ).aggregate(total=Sum('monto'))['total'] or 0,
                'pagos_hoy': pagos_base.filter(fecha_pago__date=hoy).count()
            }
        
        return stats
    
    @staticmethod
    def bulk_update_turnos_estado(turno_ids, nuevo_estado):
        """Actualización masiva optimizada del estado de turnos"""
        from MasterModels.modelos_turnos.turno import Turno
        
        return Turno.objects.filter(id__in=turno_ids).update(
            estado=nuevo_estado,
            updated_at=timezone.now()
        )
    
    @staticmethod
    def get_agenda_profesional_optimized(profesional_id, fecha_desde, fecha_hasta):
        """Agenda optimizada de un profesional"""
        from MasterModels.modelos_turnos.turno import Turno
        from MasterModels.modelos_profesionales.profesionalpracticacentro import ProfesionalPracticaCentro
        
        # Obtener configuración de horarios
        configuraciones = ProfesionalPracticaCentro.objects.filter(
            idprofesional=profesional_id,
            activo=True
        ).select_related('idcentro', 'idespecialidadpractica__idpractica')
        
        # Turnos en el período
        turnos = Turno.objects.filter(
            idprofesional=profesional_id,
            fecha__range=[fecha_desde, fecha_hasta]
        ).select_related(
            'idpaciente__persona',
            'idpractica',
            'idcentro'
        ).order_by('fecha', 'hora')
        
        return {
            'configuraciones': configuraciones,
            'turnos': turnos
        }
    
    @staticmethod
    def ejecutar_con_timeout(query_func, timeout=30):
        """Ejecuta una query con timeout para evitar bloqueos"""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Query timeout")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            result = query_func()
            signal.alarm(0)  # Cancelar timeout
            return result
        except TimeoutError:
            logger.error(f"Query timeout después de {timeout} segundos")
            raise
        except Exception as e:
            signal.alarm(0)
            logger.error(f"Error en query: {str(e)}")
            raise