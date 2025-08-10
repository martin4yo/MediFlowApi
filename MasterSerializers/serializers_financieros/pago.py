from rest_framework import serializers
from MasterModels.modelos_financieros.pago import Pago
from MasterSerializers.serializers_turnos.turno import TurnoSerializer
from MasterSerializers.serializers_pacientes.paciente import PacienteSerializer
from MasterSerializers.serializers_general.centro import CentroSerializer

class PagoSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='idpaciente.nombre_completo', read_only=True)
    centro_nombre = serializers.CharField(source='idcentro.nombre', read_only=True)
    turno_fecha = serializers.DateField(source='idturno.fecha', read_only=True)
    turno_hora = serializers.TimeField(source='idturno.hora', read_only=True)
    profesional_nombre = serializers.CharField(source='idturno.idprofesional.nombre_completo', read_only=True)
    practica_nombre = serializers.CharField(source='idturno.idespecialidadpractica.idpractica.nombre', read_only=True)
    
    # Propiedades calculadas
    es_sena = serializers.BooleanField(read_only=True)
    requiere_resto = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Pago
        fields = [
            'id', 'idturno', 'idpaciente', 'idcentro', 'tipo_pago', 'metodo_pago',
            'monto', 'monto_cobertura', 'monto_paciente', 'fecha_pago', 'comprobante',
            'observaciones', 'estado_pago', 'paciente_nombre', 'centro_nombre',
            'turno_fecha', 'turno_hora', 'profesional_nombre', 'practica_nombre',
            'es_sena', 'requiere_resto', 'created_at', 'updated_at', 'disabled'
        ]

class PagoDetailSerializer(PagoSerializer):
    idturno = TurnoSerializer(read_only=True)
    idpaciente = PacienteSerializer(read_only=True)
    idcentro = CentroSerializer(read_only=True)
    
    class Meta(PagoSerializer.Meta):
        pass

class PagoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear pagos"""
    class Meta:
        model = Pago
        fields = [
            'idturno', 'tipo_pago', 'metodo_pago', 'monto', 
            'comprobante', 'observaciones'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas para pagos"""
        turno = data['idturno']
        tipo_pago = data['tipo_pago']
        monto = data['monto']
        
        # Validar que el turno exista y esté en estado válido para pago
        if turno.idestadoturno.codigo in ['CANCELADO', 'NO_ASISTIO']:
            raise serializers.ValidationError("No se puede procesar pagos para turnos cancelados o donde el paciente no asistió")
        
        # Validar montos según el tipo de pago
        if tipo_pago == 'SENA':
            if monto > turno.sena_requerida:
                raise serializers.ValidationError(f"El monto de la seña no puede ser mayor a ${turno.sena_requerida}")
            if turno.sena_pagada:
                raise serializers.ValidationError("La seña ya fue pagada para este turno")
        
        elif tipo_pago == 'RESTO':
            # Verificar que se haya pagado la seña
            if not turno.sena_pagada:
                raise serializers.ValidationError("No se puede pagar el resto sin haber pagado la seña")
            
            # Calcular monto restante
            saldo_pendiente = turno.saldo_pendiente
            if monto > saldo_pendiente:
                raise serializers.ValidationError(f"El monto no puede ser mayor al saldo pendiente: ${saldo_pendiente}")
        
        elif tipo_pago == 'COMPLETO':
            if turno.pago_completo:
                raise serializers.ValidationError("El turno ya fue pagado completamente")
            if monto != turno.precio_paciente:
                raise serializers.ValidationError(f"Para pago completo, el monto debe ser ${turno.precio_paciente}")
        
        return data
    
    def create(self, validated_data):
        turno = validated_data['idturno']
        
        # Autocompletar campos
        validated_data['idpaciente'] = turno.idpaciente
        validated_data['idcentro'] = turno.idcentro
        validated_data['monto_paciente'] = validated_data['monto']
        validated_data['monto_cobertura'] = 0  # Por ahora
        
        pago = super().create(validated_data)
        
        # Actualizar estado del turno
        if pago.tipo_pago == 'SENA':
            turno.marcar_sena_pagada()
        elif pago.tipo_pago in ['RESTO', 'COMPLETO']:
            if turno.saldo_pendiente <= 0:
                turno.marcar_pago_completo()
        
        # Crear movimiento de caja
        from MasterModels.modelos_financieros.movimientocaja import MovimientoCaja
        MovimientoCaja.crear_movimiento_desde_pago(pago)
        
        return pago