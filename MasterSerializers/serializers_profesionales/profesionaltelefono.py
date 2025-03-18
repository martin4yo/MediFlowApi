from rest_framework import serializers
from MasterModels.modelos_profesionales import ProfesionalTelefono 


class ProfesionalTelefonoSerializer(serializers.ModelSerializer):
    """ Serializador """
    class Meta:
        """ Clase """
        model = ProfesionalTelefono
        fields = '__all__'  # O especifica los campos que deseas incluir
        read_only_fields = ('created_at', 'updated_at')


