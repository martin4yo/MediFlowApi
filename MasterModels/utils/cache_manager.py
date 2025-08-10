from django.core.cache import cache
from django.conf import settings
import hashlib
import json
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class CacheManager:
    """Gestor de cache inteligente para optimizar performance"""
    
    # Tiempos de cache por defecto (en segundos)
    CACHE_TIMES = {
        'usuario_permisos': 300,      # 5 minutos
        'configuracion_centro': 600,   # 10 minutos
        'agenda_profesional': 180,     # 3 minutos
        'estadisticas_dashboard': 120, # 2 minutos
        'reportes_frecuentes': 1800,   # 30 minutos
        'lista_pacientes': 300,        # 5 minutos
        'turnos_dia': 60,             # 1 minuto
        'liquidaciones_mes': 3600,     # 1 hora
    }
    
    @classmethod
    def generar_cache_key(cls, prefix, *args, **kwargs):
        """Genera una clave de cache única"""
        # Convertir argumentos a string para el hash
        key_data = f"{prefix}:{':'.join(map(str, args))}"
        
        # Agregar kwargs ordenados
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            kwargs_str = ':'.join(f"{k}={v}" for k, v in sorted_kwargs)
            key_data += f":{kwargs_str}"
        
        # Hash para evitar claves muy largas
        if len(key_data) > 150:
            key_hash = hashlib.md5(key_data.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        
        return key_data
    
    @classmethod
    def cache_usuario_permisos(cls, usuario_id):
        """Cache de permisos de usuario"""
        cache_key = cls.generar_cache_key('permisos', usuario_id)
        
        def obtener_permisos():
            from MasterModels.modelos_auth.usuario import Usuario
            try:
                usuario = Usuario.objects.select_related('idrol').get(id=usuario_id)
                return {
                    'permisos': usuario.idrol.get_permisos_completos(),
                    'nivel': usuario.idrol.nivel,
                    'centros_permitidos': [c.id for c in usuario.get_centros_permitidos()],
                    'es_admin': usuario.es_admin_centro()
                }
            except Usuario.DoesNotExist:
                return None
        
        return cls.get_or_set(cache_key, obtener_permisos, cls.CACHE_TIMES['usuario_permisos'])
    
    @classmethod
    def cache_estadisticas_dashboard(cls, usuario_id):
        """Cache de estadísticas del dashboard"""
        cache_key = cls.generar_cache_key('dashboard_stats', usuario_id)
        
        def obtener_estadisticas():
            from MasterModels.modelos_auth.usuario import Usuario
            from MasterModels.utils.optimizaciones import QueryOptimizer
            
            try:
                usuario = Usuario.objects.get(id=usuario_id)
                return QueryOptimizer.get_dashboard_stats(usuario)
            except Usuario.DoesNotExist:
                return {}
        
        return cls.get_or_set(cache_key, obtener_estadisticas, cls.CACHE_TIMES['estadisticas_dashboard'])
    
    @classmethod
    def cache_agenda_profesional(cls, profesional_id, fecha_desde, fecha_hasta):
        """Cache de agenda de profesional"""
        cache_key = cls.generar_cache_key('agenda', profesional_id, fecha_desde, fecha_hasta)
        
        def obtener_agenda():
            from MasterModels.utils.optimizaciones import QueryOptimizer
            return QueryOptimizer.get_agenda_profesional_optimized(
                profesional_id, fecha_desde, fecha_hasta
            )
        
        return cls.get_or_set(cache_key, obtener_agenda, cls.CACHE_TIMES['agenda_profesional'])
    
    @classmethod
    def cache_turnos_dia(cls, centro_id, fecha):
        """Cache de turnos del día por centro"""
        cache_key = cls.generar_cache_key('turnos_dia', centro_id, fecha)
        
        def obtener_turnos():
            from MasterModels.modelos_turnos.turno import Turno
            return list(Turno.objects.filter(
                idcentro=centro_id,
                fecha=fecha
            ).select_related(
                'idpaciente__persona',
                'idprofesional__persona',
                'idpractica'
            ).values(
                'id', 'hora', 'estado',
                'idpaciente__persona__nombre',
                'idpaciente__persona__apellido',
                'idprofesional__persona__nombre', 
                'idprofesional__persona__apellido',
                'idpractica__nombre'
            ))
        
        return cls.get_or_set(cache_key, obtener_turnos, cls.CACHE_TIMES['turnos_dia'])
    
    @classmethod
    def get_or_set(cls, key, func, timeout=None):
        """Obtiene del cache o ejecuta función y guarda resultado"""
        data = cache.get(key)
        
        if data is None:
            try:
                data = func()
                if data is not None:
                    cache.set(key, data, timeout or 300)
                    logger.debug(f"Cache SET: {key}")
            except Exception as e:
                logger.error(f"Error generando cache {key}: {str(e)}")
                return None
        else:
            logger.debug(f"Cache HIT: {key}")
        
        return data
    
    @classmethod
    def invalidar_cache_usuario(cls, usuario_id):
        """Invalida todas las entradas de cache relacionadas con un usuario"""
        keys_to_delete = [
            cls.generar_cache_key('permisos', usuario_id),
            cls.generar_cache_key('dashboard_stats', usuario_id)
        ]
        
        for key in keys_to_delete:
            cache.delete(key)
            logger.debug(f"Cache DELETED: {key}")
    
    @classmethod
    def invalidar_cache_agenda(cls, profesional_id):
        """Invalida cache de agenda cuando hay cambios"""
        # Como no tenemos las fechas específicas, usar patrón
        pattern = f"agenda:{profesional_id}:*"
        cls._delete_by_pattern(pattern)
    
    @classmethod
    def invalidar_cache_turnos_centro(cls, centro_id):
        """Invalida cache de turnos cuando hay cambios en un centro"""
        pattern = f"turnos_dia:{centro_id}:*"
        cls._delete_by_pattern(pattern)
    
    @classmethod
    def _delete_by_pattern(cls, pattern):
        """Elimina claves de cache por patrón (requiere Redis)"""
        try:
            # Si usamos Redis, podemos usar KEYS
            from django.core.cache.backends.redis import RedisCache
            if isinstance(cache, RedisCache):
                keys = cache._cache.keys(pattern)
                if keys:
                    cache._cache.delete(*keys)
                    logger.debug(f"Cache pattern deleted: {pattern}")
        except ImportError:
            # Para otros backends, no hay una forma eficiente
            logger.warning(f"No se puede eliminar por patrón {pattern} - backend no soportado")
    
    @classmethod
    def limpiar_cache_expirado(cls):
        """Limpia entradas de cache expiradas (si el backend lo soporta)"""
        try:
            # Algunos backends tienen métodos de limpieza automática
            if hasattr(cache, 'clear_expired'):
                cache.clear_expired()
                logger.info("Cache expirado limpiado")
        except Exception as e:
            logger.error(f"Error limpiando cache expirado: {str(e)}")
    
    @classmethod
    def estadisticas_cache(cls):
        """Obtiene estadísticas del cache si están disponibles"""
        try:
            if hasattr(cache, 'get_stats'):
                return cache.get_stats()
            elif hasattr(cache, '_cache') and hasattr(cache._cache, 'info'):
                return cache._cache.info()
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de cache: {str(e)}")
        
        return {"message": "Estadísticas no disponibles para este backend de cache"}

def cache_result(cache_key_prefix, timeout=300):
    """Decorator para cachear resultados de funciones"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar cache key con argumentos
            cache_key = CacheManager.generar_cache_key(cache_key_prefix, *args, **kwargs)
            
            # Intentar obtener del cache
            result = cache.get(cache_key)
            
            if result is None:
                # Ejecutar función y guardar resultado
                result = func(*args, **kwargs)
                if result is not None:
                    cache.set(cache_key, result, timeout)
                    logger.debug(f"Cached function result: {cache_key}")
            else:
                logger.debug(f"Function result from cache: {cache_key}")
            
            return result
        
        return wrapper
    return decorator