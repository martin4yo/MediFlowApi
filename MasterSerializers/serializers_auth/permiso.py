from rest_framework import serializers
from MasterModels.modelos_auth.permiso import Permiso

class PermisoSerializer(serializers.ModelSerializer):
    modulo_display = serializers.CharField(source='get_modulo_display', read_only=True)
    accion_display = serializers.CharField(source='get_accion_display', read_only=True)
    
    class Meta:
        model = Permiso
        fields = [
            'id', 'nombre', 'codigo', 'descripcion', 'modulo', 'modulo_display',
            'accion', 'accion_display', 'nivel_requerido', 'activo',
            'created_at', 'updated_at'
        ]

class PermisoListSerializer(serializers.ModelSerializer):
    modulo_display = serializers.CharField(source='get_modulo_display', read_only=True)
    accion_display = serializers.CharField(source='get_accion_display', read_only=True)
    
    class Meta:
        model = Permiso
        fields = [
            'id', 'nombre', 'codigo', 'modulo', 'modulo_display',
            'accion', 'accion_display', 'nivel_requerido'
        ]