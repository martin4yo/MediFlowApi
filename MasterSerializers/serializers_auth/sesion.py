from rest_framework import serializers
from MasterModels.modelos_auth.sesion import Sesion
from .usuario import UsuarioListSerializer

class SesionSerializer(serializers.ModelSerializer):
    usuario_info = UsuarioListSerializer(source='idusuario', read_only=True)
    
    # Propiedades calculadas
    esta_activa = serializers.BooleanField(read_only=True)
    duracion = serializers.SerializerMethodField()
    tiempo_inactividad = serializers.SerializerMethodField()
    es_sospechosa = serializers.SerializerMethodField()
    
    class Meta:
        model = Sesion
        fields = [
            'id', 'idusuario', 'usuario_info', 'token', 'fecha_inicio',
            'fecha_ultimo_uso', 'fecha_expiracion', 'ip_address', 'user_agent',
            'dispositivo', 'navegador', 'activa', 'cerrada_por_usuario',
            'cerrada_por_inactividad', 'cerrada_por_admin', 'paginas_visitadas',
            'acciones_realizadas', 'ultima_accion', 'esta_activa', 'duracion',
            'tiempo_inactividad', 'es_sospechosa', 'created_at'
        ]
    
    def get_duracion(self, obj):
        duracion = obj.get_duracion()
        return str(duracion) if duracion else None
    
    def get_tiempo_inactividad(self, obj):
        tiempo = obj.get_tiempo_inactividad()
        return str(tiempo) if tiempo else None
    
    def get_es_sospechosa(self, obj):
        return obj.es_sospechosa()

class SesionListSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='idusuario.get_full_name', read_only=True)
    usuario_email = serializers.CharField(source='idusuario.email', read_only=True)
    duracion = serializers.SerializerMethodField()
    
    class Meta:
        model = Sesion
        fields = [
            'id', 'usuario_nombre', 'usuario_email', 'fecha_inicio',
            'fecha_ultimo_uso', 'ip_address', 'dispositivo', 'activa',
            'acciones_realizadas', 'duracion'
        ]
    
    def get_duracion(self, obj):
        duracion = obj.get_duracion()
        return str(duracion) if duracion else None