from rest_framework import serializers
from MasterModels.modelos_profesionales import Profesional 


class ProfesionalSerializer(serializers.ModelSerializer):
    """ Serializador """
    class Meta:
        """ Clase """
        model = Profesional
        fields = '__all__'  # O especifica los campos que deseas incluir
        read_only_fields = ('created_at', 'updated_at')


