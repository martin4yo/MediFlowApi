from rest_framework import serializers
from MasterModels.modelos_reportes.reporte import Reporte

class ReporteSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    tipo_reporte_display = serializers.CharField(source='get_tipo_reporte_display', read_only=True)
    
    # Campos calculados
    filtros_disponibles = serializers.SerializerMethodField()
    columnas_disponibles = serializers.SerializerMethodField()
    
    class Meta:
        model = Reporte
        fields = [
            'id', 'nombre', 'descripcion', 'categoria', 'categoria_display',
            'tipo_reporte', 'tipo_reporte_display', 'filtros_default', 'columnas',
            'query_personalizada', 'permite_grafico', 'tipo_grafico', 
            'roles_permitidos', 'es_publico', 'activo', 'cache_minutos',
            'filtros_disponibles', 'columnas_disponibles', 'created_at', 'updated_at'
        ]
    
    def get_filtros_disponibles(self, obj):
        return obj.get_filtros_disponibles()
    
    def get_columnas_disponibles(self, obj):
        return obj.get_columnas_disponibles()

class ReporteListSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    tipo_reporte_display = serializers.CharField(source='get_tipo_reporte_display', read_only=True)
    
    class Meta:
        model = Reporte
        fields = [
            'id', 'nombre', 'descripcion', 'categoria', 'categoria_display',
            'tipo_reporte', 'tipo_reporte_display', 'permite_grafico', 
            'es_publico', 'activo'
        ]

class ReporteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = [
            'nombre', 'descripcion', 'categoria', 'tipo_reporte', 
            'filtros_default', 'columnas', 'query_personalizada',
            'permite_grafico', 'tipo_grafico', 'roles_permitidos', 
            'es_publico', 'cache_minutos'
        ]