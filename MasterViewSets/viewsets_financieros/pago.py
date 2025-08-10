from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Sum, Count, Avg
from django.db import models
from datetime import datetime, timedelta

from MasterModels.modelos_financieros.pago import Pago
from MasterSerializers.serializers_financieros.pago import PagoSerializer, PagoDetailSerializer, PagoCreateSerializer

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'idturno', 'idpaciente', 'idcentro', 'tipo_pago', 'metodo_pago', 
        'estado_pago', 'fecha_pago', 'disabled'
    ]
    ordering_fields = ['id', 'fecha_pago', 'monto', 'created_at']
    ordering = ['-fecha_pago']

    def get_serializer_class(self):
        if self.action == 'create':
            return PagoCreateSerializer
        elif self.action == 'retrieve':
            return PagoDetailSerializer
        return PagoSerializer

    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """Confirma un pago procesado"""
        pago = self.get_object()
        
        if pago.estado_pago != 'PROCESADO':
            return Response(
                {"error": "Solo se pueden confirmar pagos en estado PROCESADO"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pago.estado_pago = 'CONFIRMADO'
        pago.save()
        
        serializer = self.get_serializer(pago)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        """Anula un pago"""
        pago = self.get_object()
        motivo = request.data.get('motivo', '')
        
        if pago.estado_pago == 'ANULADO':
            return Response(
                {"error": "El pago ya está anulado"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear pago de reembolso
        Pago.objects.create(
            idturno=pago.idturno,
            idpaciente=pago.idpaciente,
            idcentro=pago.idcentro,
            tipo_pago='REEMBOLSO',
            metodo_pago=pago.metodo_pago,
            monto=pago.monto,
            monto_paciente=pago.monto_paciente,
            monto_cobertura=pago.monto_cobertura,
            observaciones=f'Reembolso de pago #{pago.id}. Motivo: {motivo}',
            estado_pago='PROCESADO'
        )
        
        pago.estado_pago = 'ANULADO'
        pago.observaciones = f'Anulado: {motivo}'
        pago.save()
        
        # Actualizar estado del turno si corresponde
        turno = pago.idturno
        if pago.tipo_pago == 'SENA':
            turno.sena_pagada = False
        elif pago.tipo_pago in ['RESTO', 'COMPLETO']:
            turno.pago_completo = False
        turno.save()
        
        serializer = self.get_serializer(pago)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_turno(self, request):
        """Obtiene todos los pagos de un turno específico"""
        turno_id = request.query_params.get('turno_id')
        if not turno_id:
            return Response(
                {"error": "Falta parámetro: turno_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pagos = self.get_queryset().filter(idturno_id=turno_id).order_by('-fecha_pago')
        serializer = self.get_serializer(pagos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def resumen_diario(self, request):
        """Resumen de pagos por día"""
        fecha = request.query_params.get('fecha')
        centro_id = request.query_params.get('centro_id')
        
        if not fecha:
            fecha = datetime.now().date().strftime('%Y-%m-%d')
        
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(fecha_pago__date=fecha)
        if centro_id:
            queryset = queryset.filter(idcentro_id=centro_id)
        
        # Resumen por tipo de pago
        resumen = queryset.values('tipo_pago', 'metodo_pago').annotate(
            total=Sum('monto'),
            cantidad=Count('id')
        ).order_by('tipo_pago', 'metodo_pago')
        
        # Totales generales
        totales = queryset.aggregate(
            total_ingresos=Sum('monto'),
            total_pagos=Count('id')
        )
        
        return Response({
            'fecha': fecha,
            'resumen_detallado': resumen,
            'totales': totales
        })

    @action(detail=False, methods=['get'])
    def pendientes_confirmacion(self, request):
        """Pagos pendientes de confirmación"""
        centro_id = request.query_params.get('centro_id')
        
        queryset = self.get_queryset().filter(estado_pago='PROCESADO')
        if centro_id:
            queryset = queryset.filter(idcentro_id=centro_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas de pagos"""
        centro_id = request.query_params.get('centro_id')
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        queryset = self.get_queryset()
        
        if centro_id:
            queryset = queryset.filter(idcentro_id=centro_id)
        
        if fecha_desde:
            try:
                fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_pago__date__gte=fecha_desde)
            except ValueError:
                pass
        
        if fecha_hasta:
            try:
                fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_pago__date__lte=fecha_hasta)
            except ValueError:
                pass
        
        # Estadísticas generales
        stats = {
            'total_ingresos': queryset.aggregate(Sum('monto'))['monto__sum'] or 0,
            'total_pagos': queryset.count(),
            'promedio_pago': queryset.aggregate(models.Avg('monto'))['monto__avg'] or 0,
            
            # Por tipo de pago
            'por_tipo': list(queryset.values('tipo_pago').annotate(
                total=Sum('monto'),
                cantidad=Count('id')
            ).order_by('-total')),
            
            # Por método de pago
            'por_metodo': list(queryset.values('metodo_pago').annotate(
                total=Sum('monto'),
                cantidad=Count('id')
            ).order_by('-total')),
            
            # Por estado
            'por_estado': list(queryset.values('estado_pago').annotate(
                total=Sum('monto'),
                cantidad=Count('id')
            ).order_by('-total'))
        }
        
        return Response(stats)