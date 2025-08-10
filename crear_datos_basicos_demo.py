"""
Script simplificado para crear datos básicos de demo
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
from MasterModels.modelos_financieros.gastoadministrativo import GastoAdministrativo
from django.contrib.auth.models import User

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

def crear_usuarios_personas():
    """Crear usuarios y personas básicas"""
    print("\n=== CREANDO USUARIOS Y PERSONAS ===")
    
    usuarios_data = [
        {
            'username': 'dr_perez',
            'email': 'juan.perez@mediflow.com',
            'first_name': 'Juan Carlos',
            'last_name': 'Pérez',
            'persona_data': {
                'nombre': 'Dr. Juan Carlos Pérez',
                'direccion': 'Av. Corrientes 1234',
                'telefono': '011-1234-5678',
                'mail': 'juan.perez@mediflow.com'
            }
        },
        {
            'username': 'dra_gonzalez',
            'email': 'maria.gonzalez@mediflow.com', 
            'first_name': 'María Elena',
            'last_name': 'González',
            'persona_data': {
                'nombre': 'Dra. María Elena González',
                'direccion': 'Av. Santa Fe 5678',
                'telefono': '011-5678-9012',
                'mail': 'maria.gonzalez@mediflow.com'
            }
        },
        {
            'username': 'carlos_martinez',
            'email': 'carlos.martinez@gmail.com',
            'first_name': 'Carlos',
            'last_name': 'Martínez',
            'persona_data': {
                'nombre': 'Carlos Martínez',
                'direccion': 'San Martín 999',
                'telefono': '011-9999-1111',
                'mail': 'carlos.martinez@gmail.com'
            }
        }
    ]
    
    for user_data in usuarios_data:
        # Crear usuario de Django
        user, user_created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name']
            }
        )
        
        if user_created:
            user.set_password('123456')  # Password temporal
            user.save()
            print(f"[OK] Usuario: {user.username}")
        
        # Crear persona
        persona_data = user_data['persona_data']
        persona, persona_created = Persona.objects.get_or_create(
            mail=persona_data['mail'],
            defaults={
                **persona_data,
                'usuario': user,
                'password': 'temp_password'
            }
        )
        
        if persona_created:
            print(f"[OK] Persona: {persona.nombre}")

def crear_profesionales():
    """Crear profesionales usando las personas existentes"""
    print("\n=== CREANDO PROFESIONALES ===")
    
    profesionales_data = [
        {
            'persona_mail': 'juan.perez@mediflow.com',
            'matricula': 'MN12345'
        },
        {
            'persona_mail': 'maria.gonzalez@mediflow.com',
            'matricula': 'MN67890'
        }
    ]
    
    for prof_data in profesionales_data:
        try:
            persona = Persona.objects.get(mail=prof_data['persona_mail'])
            
            profesional, created = Profesional.objects.get_or_create(
                matricula=prof_data['matricula'],
                defaults={'idpersona': persona}
            )
            
            if created:
                print(f"[OK] Profesional: {profesional.matricula} - {persona.nombre}")
        except Persona.DoesNotExist:
            print(f"[ERROR] Persona con email {prof_data['persona_mail']} no encontrada")

def crear_pacientes():
    """Crear pacientes usando personas existentes"""
    print("\n=== CREANDO PACIENTES ===")
    
    try:
        persona = Persona.objects.get(mail='carlos.martinez@gmail.com')
        
        paciente, created = Paciente.objects.get_or_create(
            idpersona=persona
        )
        
        if created:
            print(f"[OK] Paciente: {persona.nombre}")
    except Persona.DoesNotExist:
        print("[ERROR] Persona para paciente no encontrada")

def crear_configuracion_financiera():
    """Crear configuración financiera y gastos de demo"""
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
    
    # Crear algunos gastos de ejemplo
    centro = Centro.objects.first()
    if centro:
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
            }
        ]
        
        for gasto_data in gastos_ejemplo:
            gasto, created = GastoAdministrativo.objects.get_or_create(
                idcentro=centro,
                concepto=gasto_data['concepto'],
                defaults=gasto_data
            )
            
            if created:
                print(f"[OK] Gasto: {gasto.concepto} - ${gasto.total}")

def mostrar_resumen_final():
    """Mostrar resumen final"""
    print("\n=== RESUMEN FINAL ===")
    print(f"Centros: {Centro.objects.count()}")
    print(f"Especialidades: {Especialidad.objects.count()}")
    print(f"Prácticas: {Practica.objects.count()}")
    print(f"Especialidad-Prácticas: {EspecialidadPractica.objects.count()}")
    print(f"Usuarios: {User.objects.count()}")
    print(f"Personas: {Persona.objects.count()}")
    print(f"Profesionales: {Profesional.objects.count()}")
    print(f"Pacientes: {Paciente.objects.count()}")
    print(f"Configuraciones Comisión: {ConfiguracionComision.objects.count()}")
    print(f"Gastos Administrativos: {GastoAdministrativo.objects.count()}")
    
    print("\n=== DATOS PARA PRUEBAS ===")
    print("Usuarios creados (password: 123456):")
    for user in User.objects.all():
        print(f"  - {user.username} ({user.email})")
    
    print("\n=== SISTEMA LISTO PARA USAR ===")
    print("Puedes probar:")
    print("1. Crear turnos via API: POST /api/turnos/turno/")
    print("2. Procesar pagos: POST /api/financieros/pago/") 
    print("3. Ver reportes: GET /api/financieros/movimientocaja/balance_general/")

if __name__ == '__main__':
    try:
        crear_datos_basicos()
        crear_usuarios_personas()
        crear_profesionales()
        crear_pacientes()
        crear_configuracion_financiera()
        mostrar_resumen_final()
        print("\n=== DATOS BÁSICOS CREADOS EXITOSAMENTE ===")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)