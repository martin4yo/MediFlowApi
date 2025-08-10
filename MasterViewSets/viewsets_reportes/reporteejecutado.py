from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta

from MasterModels.modelos_reportes.reporteejecutado import ReporteEjecutado
from MasterSerializers.serializers_reportes.reporteejecutado import (
    ReporteEjecutadoSerializer, 
    ReporteEjecutadoListSerializer,
    ReporteEjecutadoCreateSerializer
)

class ReporteEjecutadoViewSet(viewsets.ModelViewSet):
    queryset = ReporteEjecutado.objects.select_related('idreporte')
    serializer_class = ReporteEjecutadoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['idreporte', 'estado', 'usuario_ejecutor']
    search_fields = ['idreporte__nombre', 'usuario_ejecutor']
    ordering_fields = ['fecha_ejecucion', 'tiempo_ejecucion_ms', 'total_registros']
    ordering = ['-fecha_ejecucion']

    def get_serializer_class(self):
        if self.action == 'list':
            return ReporteEjecutadoListSerializer
        elif self.action == 'create':
            return ReporteEjecutadoCreateSerializer
        return ReporteEjecutadoSerializer

    @action(detail=False, methods=['get'])
    def por_reporte(self, request):
        """Obtiene el historial de ejecuciones de un reporte específico"""
        reporte_id = request.query_params.get('reporte_id')
        if not reporte_id:
            return Response(
                {'error': 'Parámetro reporte_id es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ejecuciones = self.queryset.filter(idreporte=reporte_id)
        serializer = ReporteEjecutadoListSerializer(ejecuciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_usuario(self, request):
        """Obtiene reportes ejecutados por un usuario específico"""
        usuario = request.query_params.get('usuario')
        if not usuario:
            return Response(
                {'error': 'Parámetro usuario es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ejecuciones = self.queryset.filter(usuario_ejecutor=usuario)
        serializer = ReporteEjecutadoListSerializer(ejecuciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas_uso(self, request):
        """Obtiene estadísticas de uso de reportes"""
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        queryset = self.queryset
        
        if fecha_desde:
            try:
                fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_ejecucion__date__gte=fecha_desde)
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_desde inválido. Use YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if fecha_hasta:
            try:
                fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_ejecucion__date__lte=fecha_hasta)
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_hasta inválido. Use YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        estadisticas = {
            'total_ejecuciones': queryset.count(),
            'ejecuciones_exitosas': queryset.filter(estado='EXITOSO').count(),
            'ejecuciones_error': queryset.filter(estado='ERROR').count(),
            'tiempo_promedio_ms': queryset.filter(estado='EXITOSO').aggregate(
                promedio=Avg('tiempo_ejecucion_ms')
            )['promedio'] or 0,
            'reportes_mas_usados': list(
                queryset.values('idreporte__nombre').annotate(
                    total=Count('id')
                ).order_by('-total')[:5]
            ),
            'usuarios_mas_activos': list(
                queryset.values('usuario_ejecutor').annotate(
                    total=Count('id')
                ).order_by('-total')[:5]
            ),
            'por_estado': list(
                queryset.values('estado').annotate(
                    cantidad=Count('id')
                )
            )
        }
        
        return Response(estadisticas)

    @action(detail=False, methods=['get'])
    def cache_vigente(self, request):
        """Obtiene reportes con cache vigente"""
        vigentes = self.queryset.filter(
            valido_hasta__gt=timezone.now(),
            estado='EXITOSO'
        )
        serializer = ReporteEjecutadoListSerializer(vigentes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def limpiar_cache_expirado(self, request):
        """Limpia reportes con cache expirado"""
        expirados = self.queryset.filter(
            valido_hasta__lte=timezone.now()
        )
        cantidad = expirados.count()
        expirados.delete()
        
        return Response({
            'mensaje': f'Se eliminaron {cantidad} reportes con cache expirado'
        })

    @action(detail=True, methods=['post'])
    def exportar(self, request, pk=None):
        """Exporta los datos de un reporte ejecutado"""
        reporte_ejecutado = self.get_object()
        formato = request.data.get('formato', 'json')
        
        if reporte_ejecutado.estado != 'EXITOSO':
            return Response(
                {'error': 'Solo se pueden exportar reportes ejecutados exitosamente'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        datos = reporte_ejecutado.resultado_data.get('datos', [])
        
        if formato.lower() == 'csv':
            import csv
            from io import StringIO
            from django.http import HttpResponse
            
            if not datos:
                return Response({'error': 'No hay datos para exportar'}, status=status.HTTP_400_BAD_REQUEST)
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=datos[0].keys())
            writer.writeheader()
            for row in datos:
                writer.writerow(row)
            
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{reporte_ejecutado.idreporte.nombre}.csv"'
            return response
        
        # Por defecto retornar JSON
        return Response({
            'reporte': reporte_ejecutado.idreporte.nombre,
            'fecha_ejecucion': reporte_ejecutado.fecha_ejecucion,
            'datos': datos,
            'estadisticas': reporte_ejecutado.resultado_data.get('estadisticas', {})
        })

    @action(detail=False, methods=['get'])
    def resumen_diario(self, request):
        """Resumen de ejecuciones del día"""
        fecha = request.query_params.get('fecha')
        if fecha:
            try:
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            fecha = timezone.now().date()
        
        ejecuciones = self.queryset.filter(fecha_ejecucion__date=fecha)
        
        resumen = {
            'fecha': fecha,
            'total_ejecuciones': ejecuciones.count(),
            'exitosas': ejecuciones.filter(estado='EXITOSO').count(),
            'con_error': ejecuciones.filter(estado='ERROR').count(),
            'tiempo_total_ms': sum(e.tiempo_ejecucion_ms for e in ejecuciones),
            'reportes_ejecutados': list(
                ejecuciones.values('idreporte__nombre').annotate(
                    cantidad=Count('id')
                ).order_by('-cantidad')
            ),
            'usuarios_activos': list(
                ejecuciones.values('usuario_ejecutor').annotate(
                    cantidad=Count('id')
                ).order_by('-cantidad')
            )
        }
        
        return Response(resumen)

    @action(detail=True, methods=['post'])
    def marcar_expirado(self, request, pk=None):
        """Marca manualmente un cache como expirado"""
        reporte_ejecutado = self.get_object()
        reporte_ejecutado.marcar_expirado()
        return Response({'status': 'Cache marcado como expirado'})

    @action(detail=False, methods=['get'])
    def performance_report(self, request):
        """Reporte de performance de ejecuciones"""
        dias = int(request.query_params.get('dias', 7))
        fecha_limite = timezone.now() - timedelta(days=dias)
        
        ejecuciones = self.queryset.filter(
            fecha_ejecucion__gte=fecha_limite,
            estado='EXITOSO'
        )
        
        performance = {
            'periodo_dias': dias,
            'total_ejecuciones': ejecuciones.count(),
            'tiempo_promedio_ms': ejecuciones.aggregate(
                promedio=Avg('tiempo_ejecucion_ms')
            )['promedio'] or 0,
            'reportes_mas_lentos': list(
                ejecuciones.values('idreporte__nombre').annotate(
                    tiempo_promedio=Avg('tiempo_ejecucion_ms'),
                    ejecuciones=Count('id')
                ).filter(ejecuciones__gte=2).order_by('-tiempo_promedio')[:5]
            ),
            'reportes_mas_rapidos': list(
                ejecuciones.values('idreporte__nombre').annotate(
                    tiempo_promedio=Avg('tiempo_ejecucion_ms'),
                    ejecuciones=Count('id')
                ).filter(ejecuciones__gte=2).order_by('tiempo_promedio')[:5]
            )
        }
        
        return Response(performance)