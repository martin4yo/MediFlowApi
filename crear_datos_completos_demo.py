"""
Script para crear datos completos de demo (centros, prácticas, profesionales, etc.)
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

from MasterModels.modelos_general.centro import Centro
from MasterModels.modelos_general.especialidad import Especialidad
from MasterModels.modelos_general.practica import Practica
from MasterModels.modelos_general.especialidadpractica import EspecialidadPractica
from MasterModels.modelos_general.persona import Persona
from MasterModels.modelos_profesionales.profesional import Profesional
from MasterModels.modelos_pacientes.paciente import Paciente
from MasterModels.modelos_general.documento import Documento
from MasterModels.modelos_general.genero import Genero
from MasterModels.modelos_financieros.configuracioncomision import ConfiguracionComision

def crear_datos_basicos():
    """Crear centros, especialidades, prácticas básicas"""
    print("=== CREANDO DATOS BÁSICOS ===")
    
    # Crear géneros
    generos = [
        {'codigo': 'M', 'nombre': 'Masculino'},
        {'codigo': 'F', 'nombre': 'Femenino'},
        {'codigo': 'O', 'nombre': 'Otro'}
    ]
    
    for genero_data in generos:
        genero, created = Genero.objects.get_or_create(
            codigo=genero_data['codigo'],
            defaults=genero_data
        )
        if created:
            print(f"[OK] Género: {genero.nombre}")
    
    # Crear documentos
    documentos = [
        {'codigo': 'DNI', 'nombre': 'Documento Nacional de Identidad'},
        {'codigo': 'PAS', 'nombre': 'Pasaporte'},
        {'codigo': 'LE', 'nombre': 'Libreta de Enrolamiento'}
    ]
    
    for doc_data in documentos:
        documento, created = Documento.objects.get_or_create(
            codigo=doc_data['codigo'],
            defaults=doc_data
        )
        if created:
            print(f"[OK] Documento: {documento.nombre}")
    
    # Crear centros
    centros = [
        {
            'codigo': 'CENT01',
            'nombre': 'Centro Médico San Martín',
            'direccion': 'Av. San Martín 1234',
            'localidad': 'Capital Federal',
            'telefono': '011-4567-8900',
            'mail': 'info@centrosanmartin.com'
        },
        {
            'codigo': 'CENT02', 
            'nombre': 'Clínica del Norte',
            'direccion': 'Maipú 567',
            'localidad': 'Vicente López',
            'telefono': '011-4789-0123',
            'mail': 'contacto@clinicadelnorte.com'
        }
    ]
    
    for centro_data in centros:
        centro, created = Centro.objects.get_or_create(
            codigo=centro_data['codigo'],
            defaults=centro_data
        )
        if created:
            print(f"[OK] Centro: {centro.nombre}")
    
    # Crear especialidades
    especialidades = [
        {'codigo': 'CARD', 'nombre': 'Cardiología'},
        {'codigo': 'CLIN', 'nombre': 'Clínica Médica'}, 
        {'codigo': 'DERM', 'nombre': 'Dermatología'},
        {'codigo': 'GINE', 'nombre': 'Ginecología'},
        {'codigo': 'NEUR', 'nombre': 'Neurología'}
    ]
    
    for esp_data in especialidades:
        especialidad, created = Especialidad.objects.get_or_create(
            codigo=esp_data['codigo'],
            defaults=esp_data
        )
        if created:
            print(f"[OK] Especialidad: {especialidad.nombre}")
    
    # Crear prácticas con precios
    practicas = [
        {'codigo': 'CONS', 'nombre': 'Consulta', 'precio_base': 8000, 'duracion': 30},
        {'codigo': 'CTRL', 'nombre': 'Control', 'precio_base': 6000, 'duracion': 20},
        {'codigo': 'ECG', 'nombre': 'Electrocardiograma', 'precio_base': 4500, 'duracion': 15},
        {'codigo': 'ECO', 'nombre': 'Ecocardiograma', 'precio_base': 12000, 'duracion': 45},
        {'codigo': 'LAB', 'nombre': 'Análisis de laboratorio', 'precio_base': 15000, 'duracion': 10}
    ]
    
    for prac_data in practicas:
        practica, created = Practica.objects.get_or_create(
            codigo=prac_data['codigo'],
            defaults={
                'nombre': prac_data['nombre'],
                'precio_base': Decimal(str(prac_data['precio_base'])),
                'duracion_estimada_minutos': prac_data['duracion']
            }
        )
        if created:
            print(f"[OK] Práctica: {practica.nombre} - ${practica.precio_base}")
    
    # Crear relaciones especialidad-práctica
    relaciones = [
        ('CARD', 'CONS'), ('CARD', 'ECG'), ('CARD', 'ECO'),
        ('CLIN', 'CONS'), ('CLIN', 'CTRL'), ('CLIN', 'LAB'),
        ('DERM', 'CONS'), ('DERM', 'CTRL'),
        ('GINE', 'CONS'), ('GINE', 'CTRL'),
        ('NEUR', 'CONS'), ('NEUR', 'CTRL')
    ]
    
    for esp_cod, prac_cod in relaciones:
        try:
            especialidad = Especialidad.objects.get(codigo=esp_cod)
            practica = Practica.objects.get(codigo=prac_cod)
            
            esp_prac, created = EspecialidadPractica.objects.get_or_create(
                idespecialidad=especialidad,
                idpractica=practica
            )
            if created:
                print(f"[OK] Relación: {especialidad.nombre} - {practica.nombre}")
        except Exception as e:
            print(f"[ERROR] Error creando relación {esp_cod}-{prac_cod}: {e}")

def crear_profesionales_demo():
    """Crear profesionales de ejemplo"""
    print("\n=== CREANDO PROFESIONALES ===")
    
    genero_m = Genero.objects.get(codigo='M')
    genero_f = Genero.objects.get(codigo='F')
    documento_dni = Documento.objects.get(codigo='DNI')
    
    profesionales = [
        {
            'persona': {
                'nombre': 'Dr. Juan Carlos',
                'apellido': 'Pérez',
                'fecha_nacimiento': date(1975, 3, 15),
                'numero_documento': '25456789',
                'idgenero': genero_m,
                'iddocumento': documento_dni
            },
            'matricula': 'MN12345',
            'especialidades': ['CARD', 'CLIN']
        },
        {
            'persona': {
                'nombre': 'Dra. María Elena',
                'apellido': 'González',
                'fecha_nacimiento': date(1980, 8, 22),
                'numero_documento': '30789123',
                'idgenero': genero_f,
                'iddocumento': documento_dni
            },
            'matricula': 'MN67890',
            'especialidades': ['GINE', 'CLIN']
        }
    ]
    
    for prof_data in profesionales:
        # Crear persona
        persona, created = Persona.objects.get_or_create(
            numero_documento=prof_data['persona']['numero_documento'],
            defaults=prof_data['persona']
        )
        
        if created:
            print(f"[OK] Persona: {persona.nombre} {persona.apellido}")
        
        # Crear profesional
        profesional, created = Profesional.objects.get_or_create(
            matricula=prof_data['matricula'],
            defaults={'idpersona': persona}
        )
        
        if created:
            print(f"[OK] Profesional: {profesional.matricula}")

def crear_pacientes_demo():
    """Crear pacientes de ejemplo"""
    print("\n=== CREANDO PACIENTES ===")
    
    genero_m = Genero.objects.get(codigo='M')
    genero_f = Genero.objects.get(codigo='F')
    documento_dni = Documento.objects.get(codigo='DNI')
    
    pacientes = [
        {
            'nombre': 'Carlos',
            'apellido': 'Martínez',
            'fecha_nacimiento': date(1985, 5, 10),
            'numero_documento': '32456789',
            'idgenero': genero_m,
            'iddocumento': documento_dni
        },
        {
            'nombre': 'Ana',
            'apellido': 'López',
            'fecha_nacimiento': date(1992, 12, 3),
            'numero_documento': '38789456',
            'idgenero': genero_f,
            'iddocumento': documento_dni
        }
    ]
    
    for pac_data in pacientes:
        # Crear persona
        persona, created = Persona.objects.get_or_create(
            numero_documento=pac_data['numero_documento'],
            defaults=pac_data
        )
        
        if created:
            print(f"[OK] Persona: {persona.nombre} {persona.apellido}")
        
        # Crear paciente
        paciente, created = Paciente.objects.get_or_create(
            idpersona=persona
        )
        
        if created:
            print(f"[OK] Paciente: {paciente.idpersona.nombre} {paciente.idpersona.apellido}")

def crear_configuracion_financiera():
    """Crear configuración financiera"""
    print("\n=== CONFIGURACIÓN FINANCIERA ===")
    
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
            'descripcion': 'Configuración general por defecto - 70% profesional, 30% centro'
        }
    )
    
    if created:
        print(f"[OK] Configuración general: 70% prof / 30% centro")

def mostrar_resumen_final():
    """Mostrar resumen final"""
    print("\n=== RESUMEN FINAL ===")
    print(f"Centros: {Centro.objects.count()}")
    print(f"Especialidades: {Especialidad.objects.count()}")
    print(f"Prácticas: {Practica.objects.count()}")
    print(f"Especialidad-Prácticas: {EspecialidadPractica.objects.count()}")
    print(f"Profesionales: {Profesional.objects.count()}")
    print(f"Pacientes: {Paciente.objects.count()}")
    print(f"Configuraciones Comisión: {ConfiguracionComision.objects.count()}")
    
    print("\n=== SISTEMA LISTO PARA USAR ===")
    print("Puedes probar:")
    print("1. Crear turnos via API: POST /api/turnos/turno/")
    print("2. Procesar pagos: POST /api/financieros/pago/") 
    print("3. Ver reportes: GET /api/financieros/movimientocaja/balance_general/")

if __name__ == '__main__':
    try:
        crear_datos_basicos()
        crear_profesionales_demo()
        crear_pacientes_demo()
        crear_configuracion_financiera()
        mostrar_resumen_final()
        print("\n=== DATOS COMPLETOS CREADOS EXITOSAMENTE ===")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)