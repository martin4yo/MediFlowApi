import time
import logging
from django.db import connection
from django.conf import settings
from functools import wraps
from collections import defaultdict
import json

logger = logging.getLogger('performance')

class PerformanceMonitor:
    """Monitor de performance para queries y operaciones del sistema"""
    
    def __init__(self):
        self.stats = defaultdict(list)
        self.slow_queries = []
        self.slow_threshold = getattr(settings, 'SLOW_QUERY_THRESHOLD', 1.0)  # 1 segundo
    
    @classmethod
    def monitor_query_performance(cls, func):
        """Decorator para monitorear performance de queries"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_queries = len(connection.queries)
            
            try:
                result = func(*args, **kwargs)
                
                end_time = time.time()
                end_queries = len(connection.queries)
                
                execution_time = end_time - start_time
                queries_count = end_queries - start_queries
                
                # Log si es lento
                if execution_time > cls().slow_threshold:
                    logger.warning(
                        f"Slow operation: {func.__name__} took {execution_time:.3f}s "
                        f"with {queries_count} queries"
                    )
                    
                    # Guardar queries lentas si DEBUG está activo
                    if settings.DEBUG and connection.queries:
                        slow_queries = connection.queries[start_queries:]
                        cls()._log_slow_queries(func.__name__, slow_queries, execution_time)
                
                # Estadísticas generales
                cls()._record_stats(func.__name__, execution_time, queries_count)
                
                return result
                
            except Exception as e:
                end_time = time.time()
                execution_time = end_time - start_time
                
                logger.error(
                    f"Error in {func.__name__} after {execution_time:.3f}s: {str(e)}"
                )
                raise
        
        return wrapper
    
    def _record_stats(self, operation, execution_time, queries_count):
        """Registra estadísticas de performance"""
        self.stats[operation].append({
            'timestamp': time.time(),
            'execution_time': execution_time,
            'queries_count': queries_count
        })
        
        # Mantener solo los últimos 100 registros por operación
        if len(self.stats[operation]) > 100:
            self.stats[operation] = self.stats[operation][-100:]
    
    def _log_slow_queries(self, operation, queries, total_time):
        """Log detallado de queries lentas"""
        self.slow_queries.append({
            'operation': operation,
            'total_time': total_time,
            'queries': [
                {
                    'sql': q['sql'],
                    'time': float(q['time'])
                }
                for q in queries
            ],
            'timestamp': time.time()
        })
        
        # Mantener solo las últimas 50 operaciones lentas
        if len(self.slow_queries) > 50:
            self.slow_queries = self.slow_queries[-50:]
        
        # Log detallado
        for query in queries:
            if float(query['time']) > 0.5:  # Queries de más de 500ms
                logger.warning(
                    f"Slow query ({query['time']}s): {query['sql'][:200]}..."
                )
    
    def get_performance_report(self):
        """Genera reporte de performance"""
        report = {
            'operations': {},
            'slow_queries_count': len(self.slow_queries),
            'total_operations': sum(len(ops) for ops in self.stats.values())
        }
        
        for operation, records in self.stats.items():
            if records:
                times = [r['execution_time'] for r in records]
                queries = [r['queries_count'] for r in records]
                
                report['operations'][operation] = {
                    'count': len(records),
                    'avg_time': sum(times) / len(times),
                    'max_time': max(times),
                    'min_time': min(times),
                    'avg_queries': sum(queries) / len(queries) if queries else 0,
                    'max_queries': max(queries) if queries else 0
                }
        
        return report
    
    def get_slow_queries_report(self):
        """Obtiene reporte de queries lentas"""
        return {
            'total_slow_queries': len(self.slow_queries),
            'queries': self.slow_queries
        }
    
    @staticmethod
    def analyze_query_plan(query):
        """Analiza el plan de ejecución de una query (PostgreSQL)"""
        if not settings.DEBUG:
            return None
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXPLAIN ANALYZE {query}")
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error analyzing query plan: {str(e)}")
            return None
    
    @staticmethod
    def check_missing_indexes():
        """Identifica posibles índices faltantes analizando queries lentas"""
        if not settings.DEBUG:
            return []
        
        suggestions = []
        
        # Analizar queries recientes
        for query_info in connection.queries[-50:]:  # Últimas 50 queries
            query_time = float(query_info.get('time', 0))
            
            if query_time > 0.1:  # Queries de más de 100ms
                sql = query_info['sql'].lower()
                
                # Detectar patrones comunes que necesitan índices
                if 'where' in sql and 'index' not in sql:
                    # Buscar campos en WHERE sin índices
                    suggestions.append({
                        'query': query_info['sql'][:200] + '...',
                        'time': query_time,
                        'suggestion': 'Considerar agregar índice en campos del WHERE'
                    })
                
                if 'order by' in sql:
                    suggestions.append({
                        'query': query_info['sql'][:200] + '...',
                        'time': query_time,
                        'suggestion': 'Considerar agregar índice en campos del ORDER BY'
                    })
                
                if 'join' in sql and 'foreign key' not in sql:
                    suggestions.append({
                        'query': query_info['sql'][:200] + '...',
                        'time': query_time,
                        'suggestion': 'Verificar índices en campos de JOIN'
                    })
        
        # Eliminar duplicados
        unique_suggestions = []
        seen_queries = set()
        
        for suggestion in suggestions:
            if suggestion['query'] not in seen_queries:
                unique_suggestions.append(suggestion)
                seen_queries.add(suggestion['query'])
        
        return unique_suggestions[:10]  # Top 10 sugerencias
    
    @staticmethod
    def optimize_queryset(queryset, operation_name=''):
        """Optimiza un queryset sugiriendo mejoras"""
        suggestions = []
        
        # Verificar si usa select_related/prefetch_related
        query = str(queryset.query)
        
        if 'JOIN' in query.upper() and not hasattr(queryset, '_prefetch_related_lookups'):
            suggestions.append({
                'type': 'prefetch_related',
                'message': 'Considerar usar prefetch_related() para relaciones múltiples'
            })
        
        if 'JOIN' in query.upper() and not queryset._select_related:
            suggestions.append({
                'type': 'select_related',
                'message': 'Considerar usar select_related() para relaciones uno-a-uno/muchos-a-uno'
            })
        
        # Verificar uso de only() o defer()
        if len(query) > 1000:  # Query muy larga, posiblemente seleccionando muchos campos
            suggestions.append({
                'type': 'field_selection',
                'message': 'Considerar usar only() para seleccionar solo campos necesarios'
            })
        
        return suggestions

# Instance global del monitor
performance_monitor = PerformanceMonitor()

# Decorators convenientes
def monitor_performance(func):
    """Decorator simple para monitorear performance"""
    return PerformanceMonitor.monitor_query_performance(func)

def log_slow_operations(threshold=1.0):
    """Decorator configurable para operaciones lentas"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            result = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            
            if execution_time > threshold:
                logger.warning(
                    f"Slow operation: {func.__name__} took {execution_time:.3f}s"
                )
            
            return result
        return wrapper
    return decorator