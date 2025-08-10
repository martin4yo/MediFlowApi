from rest_framework import serializers
from MasterModels.modelos_auth.rol import Rol

class RolSerializer(serializers.ModelSerializer):
    permisos_completos = serializers.SerializerMethodField()
    
    class Meta:
        model = Rol
        fields = [
            'id', 'nombre', 'descripcion', 'nivel', 'activo', 'es_sistema',
            'permisos_turnos', 'permisos_pacientes', 'permisos_financieros',
            'permisos_reportes', 'permisos_admin', 'permisos_completos',
            'created_at', 'updated_at'
        ]
    
    def get_permisos_completos(self, obj):
        return obj.get_permisos_completos()

class RolListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion', 'nivel', 'activo']

class RolCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = [
            'nombre', 'descripcion', 'nivel', 'permisos_turnos', 
            'permisos_pacientes', 'permisos_financieros', 'permisos_reportes', 
            'permisos_admin'
        ]
    
    def validate_nombre(self, value):
        if Rol.objects.filter(nombre=value).exists():
            raise serializers.ValidationError("Ya existe un rol con este nombre")
        return value