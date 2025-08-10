from rest_framework import serializers
from MasterModels.modelos_reportes.reporteejecutado import ReporteEjecutado
from .reporte import ReporteListSerializer

class ReporteEjecutadoSerializer(serializers.ModelSerializer):
    reporte_info = ReporteListSerializer(source='idreporte', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    # Propiedades calculadas
    esta_vigente = serializers.BooleanField(read_only=True)
    resumen_estadistico = serializers.SerializerMethodField()
    
    class Meta:
        model = ReporteEjecutado
        fields = [
            'id', 'idreporte', 'reporte_info', 'fecha_ejecucion', 
            'usuario_ejecutor', 'filtros_aplicados', 'resultado_data', 
            'total_registros', 'tiempo_ejecucion_ms', 'estado', 
            'estado_display', 'mensaje_error', 'valido_hasta', 
            'esta_vigente', 'resumen_estadistico', 'created_at'
        ]
    
    def get_resumen_estadistico(self, obj):
        return obj.get_resumen_estadistico()

class ReporteEjecutadoListSerializer(serializers.ModelSerializer):
    reporte_nombre = serializers.CharField(source='idreporte.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    esta_vigente = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ReporteEjecutado
        fields = [
            'id', 'reporte_nombre', 'fecha_ejecucion', 'usuario_ejecutor',
            'total_registros', 'tiempo_ejecucion_ms', 'estado', 
            'estado_display', 'esta_vigente'
        ]

class ReporteEjecutadoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteEjecutado
        fields = [
            'idreporte', 'usuario_ejecutor', 'filtros_aplicados',
            'resultado_data', 'total_registros', 'tiempo_ejecucion_ms',
            'estado', 'mensaje_error', 'valido_hasta'
        ]