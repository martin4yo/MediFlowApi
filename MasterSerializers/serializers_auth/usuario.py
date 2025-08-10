from rest_framework import serializers
from django.contrib.auth import authenticate
from MasterModels.modelos_auth.usuario import Usuario
from .rol import RolListSerializer

class UsuarioSerializer(serializers.ModelSerializer):
    rol_info = RolListSerializer(source='idrol', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    # Propiedades calculadas
    esta_bloqueado = serializers.BooleanField(read_only=True)
    es_profesional = serializers.BooleanField(read_only=True)
    es_admin_centro = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'username', 'nombre', 'apellido', 'full_name',
            'idrol', 'rol_info', 'idprofesional', 'idcentro', 'activo', 
            'email_verificado', 'debe_cambiar_password', 'ultimo_acceso',
            'intentos_fallidos', 'esta_bloqueado', 'es_profesional',
            'es_admin_centro', 'configuracion', 'created_at', 'updated_at'
        ]
        read_only_fields = ['ultimo_acceso', 'intentos_fallidos']

class UsuarioListSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='idrol.nombre', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    centro_nombre = serializers.CharField(source='idcentro.nombre', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'full_name', 'rol_nombre', 'centro_nombre',
            'activo', 'ultimo_acceso', 'es_profesional'
        ]

class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'email', 'username', 'nombre', 'apellido', 'idrol', 
            'idprofesional', 'idcentro', 'password', 'password_confirm'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        usuario = Usuario.objects.create_user(
            password=password,
            **validated_data
        )
        return usuario

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            try:
                usuario = Usuario.objects.get(email=email)
                
                if usuario.esta_bloqueado():
                    raise serializers.ValidationError(
                        "Usuario bloqueado temporalmente. Intente más tarde."
                    )
                
                if not usuario.activo:
                    raise serializers.ValidationError("Usuario inactivo")
                
                user = authenticate(username=email, password=password)
                
                if user:
                    usuario.reset_intentos_fallidos()
                    data['user'] = user
                else:
                    usuario.incrementar_intentos_fallidos()
                    raise serializers.ValidationError("Credenciales inválidas")
                    
            except Usuario.DoesNotExist:
                raise serializers.ValidationError("Credenciales inválidas")
        else:
            raise serializers.ValidationError("Email y contraseña son requeridos")
        
        return data

class CambioPasswordSerializer(serializers.Serializer):
    password_actual = serializers.CharField(write_only=True)
    password_nuevo = serializers.CharField(write_only=True, min_length=8)
    password_confirmar = serializers.CharField(write_only=True)
    
    def validate(self, data):
        if data['password_nuevo'] != data['password_confirmar']:
            raise serializers.ValidationError("Las contraseñas nuevas no coinciden")
        
        usuario = self.context['request'].user
        if not usuario.check_password(data['password_actual']):
            raise serializers.ValidationError("Contraseña actual incorrecta")
        
        return data

class UsuarioPerfilSerializer(serializers.ModelSerializer):
    """Serializer para que el usuario vea/edite su propio perfil"""
    rol_info = RolListSerializer(source='idrol', read_only=True)
    permisos = serializers.SerializerMethodField()
    centros_permitidos = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nombre', 'apellido', 'rol_info', 'idcentro',
            'configuracion', 'permisos', 'centros_permitidos'
        ]
        read_only_fields = ['email', 'rol_info', 'permisos', 'centros_permitidos']
    
    def get_permisos(self, obj):
        return obj.idrol.get_permisos_completos()
    
    def get_centros_permitidos(self, obj):
        centros = obj.get_centros_permitidos()
        return [{'id': c.id, 'nombre': c.nombre} for c in centros]