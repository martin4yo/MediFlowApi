from rest_framework import serializers
from MasterModels.modelos_financieros.liquidacion import Liquidacion
from MasterSerializers.serializers_profesionales.profesional import ProfesionalSerializer
from MasterSerializers.serializers_general.centro import CentroSerializer

class LiquidacionSerializer(serializers.ModelSerializer):
    profesional_nombre = serializers.CharField(source='idprofesional.nombre_completo', read_only=True)
    centro_nombre = serializers.CharField(source='idcentro.nombre', read_only=True)
    
    class Meta:
        model = Liquidacion
        fields = [
            'id', 'idprofesional', 'idcentro', 'periodo_desde', 'periodo_hasta',
            'total_bruto', 'total_comision_profesional', 'total_comision_centro',
            'descuentos', 'ajustes', 'total_a_pagar', 'estado', 'fecha_calculo',
            'fecha_aprobacion', 'fecha_pago', 'numero_liquidacion', 'observaciones',
            'detalle_calculo', 'profesional_nombre', 'centro_nombre',
            'created_at', 'updated_at', 'disabled'
        ]
        read_only_fields = [
            'total_bruto', 'total_comision_profesional', 'total_comision_centro',
            'total_a_pagar', 'fecha_calculo', 'fecha_aprobacion', 'fecha_pago',
            'numero_liquidacion', 'detalle_calculo'
        ]

class LiquidacionDetailSerializer(LiquidacionSerializer):
    idprofesional = ProfesionalSerializer(read_only=True)
    idcentro = CentroSerializer(read_only=True)
    
    class Meta(LiquidacionSerializer.Meta):
        pass

class LiquidacionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear liquidaciones"""
    class Meta:
        model = Liquidacion
        fields = [
            'idprofesional', 'idcentro', 'periodo_desde', 'periodo_hasta',
            'descuentos', 'ajustes', 'observaciones'
        ]
    
    def validate(self, data):
        """Validaciones para crear liquidación"""
        if data['periodo_desde'] >= data['periodo_hasta']:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha fin")
        
        # Verificar que no exista otra liquidación para el mismo período
        existe = Liquidacion.objects.filter(
            idprofesional=data['idprofesional'],
            idcentro=data['idcentro'],
            periodo_desde=data['periodo_desde'],
            periodo_hasta=data['periodo_hasta']
        ).exists()
        
        if existe:
            raise serializers.ValidationError(
                "Ya existe una liquidación para este profesional, centro y período"
            )
        
        return data