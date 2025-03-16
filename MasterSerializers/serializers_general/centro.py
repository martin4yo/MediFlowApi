from rest_framework import serializers
from MasterModels.modelos_general.centro import Centro

class CentroSerializer(serializers.ModelSerializer):
    """ Serializador """
    class Meta:
        """ Clase """
        model = Centro
        fields = '__all__'  # O especifica los campos que deseas incluir
        read_only_fields = ('created_at', 'updated_at')


