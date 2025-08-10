"""
Script para crear datos de demo del sistema financiero
Ejecutar después de aplicar las migraciones financieras
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MediFlowConnect.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from MasterModels.modelos_financieros.configuracioncomision import ConfiguracionComision
from MasterModels.modelos_financieros.gastoadministrativo import GastoAdministrativo
from MasterModels.modelos_general.practica import Practica
from MasterModels.modelos_general.centro import Centro

def crear_configuraciones_comision():
    """Crear configuraciones de comisión de ejemplo"""
    print("Creando configuraciones de comisión...")
    
    # Configuración general por defecto
    config_general, created = ConfiguracionComision.objects.get_or_create(
        idprofesional=None,
        idcentro=None,
        idespecialidadpractica=None,
        defaults={
            'porcentaje_profesional': Decimal('70.00'),
            'porcentaje_centro': Decimal('30.00'),
            'prioridad': 5,
            'fecha_inicio': date(2024, 1, 1),
            'activo': True,
            'descripcion': 'Configuración general por defecto'
        }
    )
    
    if created:
        print(f"[OK] Configuración general creada: 70%/30%")
    else:
        print(f"[--] Configuración general ya existe")

def actualizar_precios_practicas():
    """Actualizar precios de las prácticas existentes"""
    print("Actualizando precios de prácticas...")
    
    precios_ejemplo = {
        'CONS': 8000,  # Consulta
        'CTRL': 6000,  # Control
        'ECG': 4500,   # Electrocardiograma
        'LAB': 12000,  # Laboratorio
        'RX': 15000,   # Radiografía
    }
    
    for codigo, precio in precios_ejemplo.items():
        try:
            practica = Practica.objects.filter(codigo=codigo).first()
            if practica:
                practica.precio_base = Decimal(str(precio))
                practica.save()
                print(f"[OK] {practica.nombre}: ${precio}")
            else:
                print(f"[--] Práctica con código {codigo} no encontrada")
        except Exception as e:
            print(f"[ERROR] Error actualizando {codigo}: {e}")

def crear_gastos_administrativos_demo():
    """Crear gastos administrativos de ejemplo"""
    print("Creando gastos administrativos de ejemplo...")
    
    # Buscar el primer centro
    centro = Centro.objects.first()
    if not centro:
        print("[ERROR] No hay centros disponibles")
        return
    
    gastos_ejemplo = [
        {
            'categoria': 'SERVICIOS',
            'subcategoria': 'Electricidad',
            'concepto': 'Factura de luz - Enero 2024',
            'proveedor': 'EDESUR',
            'monto': Decimal('25000'),
            'iva': Decimal('5250'),
            'fecha_gasto': date.today() - timedelta(days=15),
            'fecha_vencimiento': date.today() + timedelta(days=10),
            'es_recurrente': True
        },
        {
            'categoria': 'ALQUILER',
            'concepto': 'Alquiler del local - Febrero 2024',
            'proveedor': 'Inmobiliaria San Martín',
            'monto': Decimal('180000'),
            'iva': Decimal('0'),
            'fecha_gasto': date.today() - timedelta(days=5),
            'fecha_vencimiento': date.today() + timedelta(days=25),
            'es_recurrente': True
        },
        {
            'categoria': 'EQUIPAMIENTO',
            'concepto': 'Camilla nueva consultorio 3',
            'proveedor': 'MediEquip SRL',
            'monto': Decimal('85000'),
            'iva': Decimal('17850'),
            'fecha_gasto': date.today() - timedelta(days=3),
            'estado_pago': 'PAGADO',
            'fecha_pago': date.today() - timedelta(days=1),
            'metodo_pago': 'TRANSFERENCIA'
        }
    ]
    
    for gasto_data in gastos_ejemplo:
        gasto, created = GastoAdministrativo.objects.get_or_create(
            idcentro=centro,
            concepto=gasto_data['concepto'],
            defaults=gasto_data
        )
        
        if created:
            print(f"[OK] Gasto creado: {gasto.concepto} - ${gasto.total}")
        else:
            print(f"[--] Gasto ya existe: {gasto.concepto}")

def mostrar_resumen():
    """Mostrar resumen de datos creados"""
    print("\n=== RESUMEN DE DATOS CREADOS ===")
    
    # Configuraciones de comisión
    configs = ConfiguracionComision.objects.count()
    print(f"Configuraciones de comisión: {configs}")
    
    # Prácticas con precio
    practicas_con_precio = Practica.objects.filter(precio_base__gt=0).count()
    print(f"Prácticas con precio configurado: {practicas_con_precio}")
    
    # Gastos administrativos
    gastos = GastoAdministrativo.objects.count()
    print(f"Gastos administrativos: {gastos}")
    
    print("\n=== PRÓXIMOS PASOS ===")
    print("1. Crear turnos desde la API para probar el flujo completo")
    print("2. Procesar pagos de señas y restos")
    print("3. Generar liquidaciones mensuales")
    print("4. Revisar reportes financieros")

if __name__ == '__main__':
    print("=== CREANDO DATOS FINANCIEROS DE DEMO ===")
    try:
        crear_configuraciones_comision()
        print()
        actualizar_precios_practicas()
        print()
        crear_gastos_administrativos_demo()
        print()
        mostrar_resumen()
        print("\n=== DATOS FINANCIEROS CREADOS EXITOSAMENTE ===")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)