from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import time

from MasterModels.modelos_reportes.reporte import Reporte
from MasterModels.modelos_reportes.reporteejecutado import ReporteEjecutado
from MasterModels.modelos_turnos.turno import Turno
from MasterModels.modelos_financieros.pago import Pago
from MasterModels.modelos_financieros.liquidacion import Liquidacion

from MasterSerializers.serializers_reportes.reporte import (
    ReporteSerializer, 
    ReporteListSerializer,
    ReporteCreateSerializer
)

class ReporteViewSet(viewsets.ModelViewSet):
    queryset = Reporte.objects.all()
    serializer_class = ReporteSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categoria', 'tipo_reporte', 'activo', 'es_publico']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'categoria', 'created_at']
    ordering = ['categoria', 'nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return ReporteListSerializer
        elif self.action == 'create':
            return ReporteCreateSerializer
        return ReporteSerializer

    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        """Obtiene reportes agrupados por categoría"""
        categoria = request.query_params.get('categoria')
        if not categoria:
            return Response(
                {'error': 'Parámetro categoria es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reportes = self.queryset.filter(categoria=categoria, activo=True)
        serializer = ReporteListSerializer(reportes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def publicos(self, request):
        """Obtiene reportes públicos"""
        reportes = self.queryset.filter(es_publico=True, activo=True)
        serializer = ReporteListSerializer(reportes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def ejecutar(self, request, pk=None):
        """Ejecuta un reporte con filtros específicos"""
        reporte = self.get_object()
        filtros = request.data.get('filtros', {})
        usuario = request.data.get('usuario', 'sistema')
        forzar_ejecucion = request.data.get('forzar_ejecucion', False)
        
        # Verificar permisos
        if not reporte.puede_ejecutar(request.user if hasattr(request, 'user') else None):
            return Response(
                {'error': 'No tiene permisos para ejecutar este reporte'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Buscar resultado cacheado
        if not forzar_ejecucion and reporte.cache_minutos > 0:
            cache_valido = ReporteEjecutado.objects.filter(
                idreporte=reporte,
                filtros_aplicados=filtros,
                valido_hasta__gt=timezone.now()
            ).first()
            
            if cache_valido:
                from MasterSerializers.serializers_reportes.reporteejecutado import ReporteEjecutadoSerializer
                serializer = ReporteEjecutadoSerializer(cache_valido)
                return Response({
                    'desde_cache': True,
                    'reporte_ejecutado': serializer.data
                })
        
        # Ejecutar reporte
        inicio = time.time()
        try:
            resultado = self._ejecutar_reporte(reporte, filtros)
            tiempo_ms = int((time.time() - inicio) * 1000)
            
            # Calcular fecha de expiración del cache
            valido_hasta = None
            if reporte.cache_minutos > 0:
                valido_hasta = timezone.now() + timedelta(minutes=reporte.cache_minutos)
            
            # Guardar resultado
            reporte_ejecutado = ReporteEjecutado.objects.create(
                idreporte=reporte,
                usuario_ejecutor=usuario,
                filtros_aplicados=filtros,
                resultado_data=resultado,
                total_registros=len(resultado.get('datos', [])),
                tiempo_ejecucion_ms=tiempo_ms,
                estado='EXITOSO',
                valido_hasta=valido_hasta
            )
            
            from MasterSerializers.serializers_reportes.reporteejecutado import ReporteEjecutadoSerializer
            serializer = ReporteEjecutadoSerializer(reporte_ejecutado)
            
            return Response({
                'desde_cache': False,
                'reporte_ejecutado': serializer.data
            })
            
        except Exception as e:
            tiempo_ms = int((time.time() - inicio) * 1000)
            
            # Guardar error
            ReporteEjecutado.objects.create(
                idreporte=reporte,
                usuario_ejecutor=usuario,
                filtros_aplicados=filtros,
                resultado_data={},
                total_registros=0,
                tiempo_ejecucion_ms=tiempo_ms,
                estado='ERROR',
                mensaje_error=str(e)
            )
            
            return Response(
                {'error': f'Error al ejecutar reporte: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _ejecutar_reporte(self, reporte, filtros):
        """Método interno para ejecutar diferentes tipos de reportes"""
        if reporte.tipo_reporte == 'TURNOS_CENTRO':
            return self._generar_reporte_turnos_centro(filtros)
        elif reporte.tipo_reporte == 'TURNOS_PROFESIONAL':
            return self._generar_reporte_turnos_profesional(filtros)
        elif reporte.tipo_reporte == 'INGRESOS_PERIODO':
            return self._generar_reporte_ingresos_periodo(filtros)
        elif reporte.tipo_reporte == 'LIQUIDACIONES':
            return self._generar_reporte_liquidaciones(filtros)
        elif reporte.tipo_reporte == 'PERSONALIZADO' and reporte.query_personalizada:
            return self._ejecutar_query_personalizada(reporte.query_personalizada, filtros)
        else:
            raise ValueError(f"Tipo de reporte no implementado: {reporte.tipo_reporte}")

    def _generar_reporte_turnos_centro(self, filtros):
        """Genera reporte de turnos por centro"""
        queryset = Turno.objects.select_related(
            'idpaciente__persona', 'idprofesional__persona', 
            'idpractica', 'idcentro'
        )
        
        # Aplicar filtros
        if filtros.get('centro_id'):
            queryset = queryset.filter(idcentro=filtros['centro_id'])
        if filtros.get('fecha_desde'):
            queryset = queryset.filter(fecha__gte=filtros['fecha_desde'])
        if filtros.get('fecha_hasta'):
            queryset = queryset.filter(fecha__lte=filtros['fecha_hasta'])
        if filtros.get('estado'):
            queryset = queryset.filter(estado=filtros['estado'])
        
        datos = []
        for turno in queryset:
            datos.append({
                'fecha': turno.fecha.strftime('%Y-%m-%d'),
                'hora': turno.hora.strftime('%H:%M'),
                'paciente': turno.idpaciente.persona.get_nombre_completo() if turno.idpaciente else '',
                'profesional': turno.idprofesional.persona.get_nombre_completo() if turno.idprofesional else '',
                'practica': turno.idpractica.nombre if turno.idpractica else '',
                'centro': turno.idcentro.nombre if turno.idcentro else '',
                'estado': turno.get_estado_display(),
                'precio_total': float(turno.precio_total) if turno.precio_total else 0
            })
        
        # Calcular estadísticas
        total_turnos = len(datos)
        ingresos_total = sum(item['precio_total'] for item in datos)
        
        return {
            'datos': datos,
            'estadisticas': {
                'total_turnos': total_turnos,
                'ingresos_total': ingresos_total,
                'promedio_por_turno': ingresos_total / total_turnos if total_turnos > 0 else 0
            },
            'filtros_aplicados': filtros
        }

    def _generar_reporte_ingresos_periodo(self, filtros):
        """Genera reporte de ingresos por período"""
        queryset = Pago.objects.select_related(
            'idturno__idcentro', 'idturno__idprofesional__persona'
        )
        
        # Aplicar filtros
        if filtros.get('fecha_desde'):
            queryset = queryset.filter(fecha_pago__gte=filtros['fecha_desde'])
        if filtros.get('fecha_hasta'):
            queryset = queryset.filter(fecha_pago__lte=filtros['fecha_hasta'])
        if filtros.get('centro_id'):
            queryset = queryset.filter(idturno__idcentro=filtros['centro_id'])
        if filtros.get('tipo_pago'):
            queryset = queryset.filter(tipo_pago=filtros['tipo_pago'])
        
        datos = []
        for pago in queryset:
            datos.append({
                'fecha': pago.fecha_pago.strftime('%Y-%m-%d'),
                'centro': pago.idturno.idcentro.nombre if pago.idturno and pago.idturno.idcentro else '',
                'profesional': pago.idturno.idprofesional.persona.get_nombre_completo() if pago.idturno and pago.idturno.idprofesional else '',
                'tipo_pago': pago.get_tipo_pago_display(),
                'monto_total': float(pago.monto),
                'descripcion': pago.descripcion
            })
        
        # Estadísticas
        total_ingresos = sum(item['monto_total'] for item in datos)
        cantidad_pagos = len(datos)
        
        return {
            'datos': datos,
            'estadisticas': {
                'total_ingresos': total_ingresos,
                'cantidad_pagos': cantidad_pagos,
                'promedio_pago': total_ingresos / cantidad_pagos if cantidad_pagos > 0 else 0
            },
            'filtros_aplicados': filtros
        }

    @action(detail=False, methods=['get'])
    def tipos_disponibles(self, request):
        """Lista todos los tipos de reporte disponibles"""
        tipos = [{'value': choice[0], 'label': choice[1]} 
                for choice in Reporte._meta.get_field('tipo_reporte').choices]
        return Response(tipos)

    @action(detail=False, methods=['get'])
    def categorias_disponibles(self, request):
        """Lista todas las categorías disponibles"""
        categorias = [{'value': choice[0], 'label': choice[1]} 
                     for choice in Reporte._meta.get_field('categoria').choices]
        return Response(categorias)

    @action(detail=True, methods=['post'])
    def duplicar(self, request, pk=None):
        """Duplica un reporte existente"""
        reporte_original = self.get_object()
        nuevo_nombre = request.data.get('nuevo_nombre', f"{reporte_original.nombre} (Copia)")
        
        nuevo_reporte = Reporte.objects.create(
            nombre=nuevo_nombre,
            descripcion=reporte_original.descripcion,
            categoria=reporte_original.categoria,
            tipo_reporte=reporte_original.tipo_reporte,
            filtros_default=reporte_original.filtros_default,
            columnas=reporte_original.columnas,
            query_personalizada=reporte_original.query_personalizada,
            permite_grafico=reporte_original.permite_grafico,
            tipo_grafico=reporte_original.tipo_grafico,
            roles_permitidos=reporte_original.roles_permitidos,
            es_publico=False,  # Las copias no son públicas por defecto
            cache_minutos=reporte_original.cache_minutos
        )
        
        serializer = ReporteSerializer(nuevo_reporte)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Obtiene datos para dashboard de reportes"""
        reportes_activos = self.queryset.filter(activo=True).count()
        reportes_publicos = self.queryset.filter(es_publico=True, activo=True).count()
        
        # Reportes más ejecutados
        from django.db.models import Count
        mas_ejecutados = ReporteEjecutado.objects.values(
            'idreporte__nombre'
        ).annotate(
            total_ejecuciones=Count('id')
        ).order_by('-total_ejecuciones')[:5]
        
        # Estadísticas por categoría
        por_categoria = self.queryset.filter(activo=True).values(
            'categoria'
        ).annotate(
            cantidad=Count('id')
        )
        
        return Response({
            'resumen': {
                'reportes_activos': reportes_activos,
                'reportes_publicos': reportes_publicos,
                'total_reportes': self.queryset.count()
            },
            'mas_ejecutados': list(mas_ejecutados),
            'por_categoria': list(por_categoria)
        })