from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Sum, Count
from django.db import models
from datetime import datetime

from MasterModels.modelos_financieros.liquidacion import Liquidacion
from MasterSerializers.serializers_financieros.liquidacion import LiquidacionSerializer, LiquidacionDetailSerializer, LiquidacionCreateSerializer

class LiquidacionViewSet(viewsets.ModelViewSet):
    queryset = Liquidacion.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'idprofesional', 'idcentro', 'estado', 'periodo_desde', 
        'periodo_hasta', 'disabled'
    ]
    ordering_fields = ['id', 'periodo_desde', 'fecha_calculo', 'total_a_pagar', 'created_at']
    ordering = ['-periodo_desde']

    def get_serializer_class(self):
        if self.action == 'create':
            return LiquidacionCreateSerializer
        elif self.action == 'retrieve':
            return LiquidacionDetailSerializer
        return LiquidacionSerializer

    def perform_create(self, serializer):
        """Al crear una liquidación, mantener en estado borrador"""
        serializer.save(estado='BORRADOR')

    @action(detail=True, methods=['post'])
    def calcular(self, request, pk=None):
        """Calcula los montos de la liquidación"""
        liquidacion = self.get_object()
        
        if liquidacion.estado not in ['BORRADOR', 'CALCULADA']:
            return Response(
                {"error": "Solo se pueden recalcular liquidaciones en estado BORRADOR o CALCULADA"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            liquidacion.calcular_liquidacion()
            serializer = self.get_serializer(liquidacion)
            return Response({
                "message": "Liquidación calculada exitosamente",
                "liquidacion": serializer.data
            })
        except Exception as e:
            return Response(
                {"error": f"Error al calcular liquidación: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """Aprueba una liquidación calculada"""
        liquidacion = self.get_object()
        
        if liquidacion.estado != 'CALCULADA':
            return Response(
                {"error": "Solo se pueden aprobar liquidaciones CALCULADAS"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        liquidacion.aprobar()
        
        serializer = self.get_serializer(liquidacion)
        return Response({
            "message": "Liquidación aprobada exitosamente",
            "liquidacion": serializer.data
        })

    @action(detail=True, methods=['post'])
    def marcar_pagada(self, request, pk=None):
        """Marca una liquidación como pagada"""
        liquidacion = self.get_object()
        
        if liquidacion.estado != 'APROBADA':
            return Response(
                {"error": "Solo se pueden marcar como pagadas liquidaciones APROBADAS"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        liquidacion.marcar_pagada()
        
        # Crear movimiento de caja
        from MasterModels.modelos_financieros.movimientocaja import MovimientoCaja
        MovimientoCaja.crear_movimiento_desde_liquidacion(liquidacion)
        
        serializer = self.get_serializer(liquidacion)
        return Response({
            "message": "Liquidación marcada como pagada",
            "liquidacion": serializer.data
        })

    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        """Anula una liquidación"""
        liquidacion = self.get_object()
        motivo = request.data.get('motivo', '')
        
        if liquidacion.estado == 'PAGADA':
            return Response(
                {"error": "No se puede anular una liquidación que ya fue pagada"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        liquidacion.estado = 'ANULADA'
        liquidacion.observaciones = f'Anulada: {motivo}'
        liquidacion.save()
        
        serializer = self.get_serializer(liquidacion)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def crear_masiva(self, request):
        """Crea liquidaciones para múltiples profesionales en un período"""
        data = request.data
        profesionales_ids = data.get('profesionales_ids', [])
        centro_id = data.get('centro_id')
        periodo_desde = data.get('periodo_desde')
        periodo_hasta = data.get('periodo_hasta')
        
        if not all([profesionales_ids, centro_id, periodo_desde, periodo_hasta]):
            return Response(
                {"error": "Faltan parámetros obligatorios"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            periodo_desde = datetime.strptime(periodo_desde, '%Y-%m-%d').date()
            periodo_hasta = datetime.strptime(periodo_hasta, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        liquidaciones_creadas = []
        errores = []
        
        for profesional_id in profesionales_ids:
            try:
                # Verificar que no exista liquidación para este período
                existe = Liquidacion.objects.filter(
                    idprofesional_id=profesional_id,
                    idcentro_id=centro_id,
                    periodo_desde=periodo_desde,
                    periodo_hasta=periodo_hasta
                ).exists()
                
                if not existe:
                    liquidacion = Liquidacion.objects.create(
                        idprofesional_id=profesional_id,
                        idcentro_id=centro_id,
                        periodo_desde=periodo_desde,
                        periodo_hasta=periodo_hasta,
                        estado='BORRADOR'
                    )
                    liquidaciones_creadas.append(liquidacion.id)
                else:
                    errores.append(f"Profesional {profesional_id}: Ya existe liquidación para este período")
                    
            except Exception as e:
                errores.append(f"Profesional {profesional_id}: {str(e)}")
        
        return Response({
            "liquidaciones_creadas": liquidaciones_creadas,
            "total_creadas": len(liquidaciones_creadas),
            "errores": errores
        })

    @action(detail=False, methods=['get'])
    def pendientes_calculo(self, request):
        """Liquidaciones pendientes de cálculo"""
        centro_id = request.query_params.get('centro_id')
        
        queryset = self.get_queryset().filter(estado='BORRADOR')
        if centro_id:
            queryset = queryset.filter(idcentro_id=centro_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def resumen_periodo(self, request):
        """Resumen de liquidaciones por período"""
        centro_id = request.query_params.get('centro_id')
        periodo_desde = request.query_params.get('periodo_desde')
        periodo_hasta = request.query_params.get('periodo_hasta')
        
        if not all([periodo_desde, periodo_hasta]):
            return Response(
                {"error": "Faltan parámetros: periodo_desde, periodo_hasta"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            periodo_desde = datetime.strptime(periodo_desde, '%Y-%m-%d').date()
            periodo_hasta = datetime.strptime(periodo_hasta, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta
        )
        
        if centro_id:
            queryset = queryset.filter(idcentro_id=centro_id)
        
        # Resumen por estado
        resumen = queryset.values('estado').annotate(
            cantidad=models.Count('id'),
            total_bruto=Sum('total_bruto'),
            total_profesional=Sum('total_comision_profesional'),
            total_centro=Sum('total_comision_centro'),
            total_a_pagar=Sum('total_a_pagar')
        ).order_by('estado')
        
        # Totales generales
        totales = queryset.aggregate(
            total_liquidaciones=models.Count('id'),
            total_bruto_general=Sum('total_bruto'),
            total_profesionales_general=Sum('total_comision_profesional'),
            total_centro_general=Sum('total_comision_centro'),
            total_a_pagar_general=Sum('total_a_pagar')
        )
        
        return Response({
            'periodo': {
                'desde': periodo_desde,
                'hasta': periodo_hasta
            },
            'resumen_por_estado': resumen,
            'totales_generales': totales
        })