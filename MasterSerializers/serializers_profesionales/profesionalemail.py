from rest_framework import serializers
from MasterModels.modelos_profesionales import ProfesionalEmail

class ProfesionalEmailSerializer(serializers.ModelSerializer):
    """ Serializador """
    class Meta:
        """ Clase """
        model = ProfesionalEmail
        fields = '__all__'  # O especifica los campos que deseas incluir
        read_only_fields = ('created_at', 'updated_at')


