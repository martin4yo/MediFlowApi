from rest_framework import serializers
from MasterModels.modelos_notificaciones.plantillanotificacion import PlantillaNotificacion

class PlantillaNotificacionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    canal_display = serializers.CharField(source='get_canal_display', read_only=True)
    
    class Meta:
        model = PlantillaNotificacion
        fields = [
            'id', 'tipo', 'tipo_display', 'canal', 'canal_display', 'nombre', 
            'asunto', 'contenido', 'variables_disponibles', 'activa', 'es_default',
            'created_at', 'updated_at', 'disabled'
        ]
    
    def validate(self, data):
        # Validar que solo haya una plantilla default por tipo/canal
        if data.get('es_default'):
            existing = PlantillaNotificacion.objects.filter(
                tipo=data['tipo'], 
                canal=data['canal'], 
                es_default=True
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise serializers.ValidationError(
                    "Ya existe una plantilla por defecto para este tipo y canal"
                )
        return data

class PlantillaNotificacionListSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    canal_display = serializers.CharField(source='get_canal_display', read_only=True)
    
    class Meta:
        model = PlantillaNotificacion
        fields = ['id', 'nombre', 'tipo', 'tipo_display', 'canal', 'canal_display', 'activa', 'es_default']