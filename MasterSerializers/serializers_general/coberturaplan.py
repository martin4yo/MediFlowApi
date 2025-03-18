from rest_framework import serializers
from MasterModels.modelos_general.coberturaplan import CoberturaPlan

class CoberturaPlanSerializer(serializers.ModelSerializer):
    """ Serializador """
    class Meta:
        """ Clase """
        model = CoberturaPlan
        fields = '__all__'  # O especifica los campos que deseas incluir
        read_only_fields = ('created_at', 'updated_at')


