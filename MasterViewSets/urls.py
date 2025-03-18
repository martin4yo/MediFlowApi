"""
Urls
"""
from django.urls import path, include
from rest_framework import routers

class Router(routers.DefaultRouter):
    """
    Para PascalName
    """
    pass

router = Router()

# URLS GENERALES

from MasterViewSets.viewsets_general import PracticaViewSet, CentroViewSet, PersonaViewSet, EspecialidadViewSet
from MasterViewSets.viewsets_general import EspecialidadPracticaViewSet, CoberturaViewSet, CoberturaPlanViewSet
from MasterViewSets.viewsets_general import PracticaPlanViewSet, DocumentoViewSet, GeneroViewSet

# URLS PROFESIONALES 
from MasterViewSets.viewsets_profesionales import ProfesionalViewSet, ProfesionalEmailViewSet, ProfesionalTelefonoViewSet
from MasterViewSets.viewsets_profesionales import ProfesionalDocumentoViewSet, ProfesionalPracticaViewSet, ProfesionalPracticaCentroViewSet

#URL PACIENTES
from MasterViewSets.viewsets_pacientes import PacienteViewSet, PacienteHistoriaViewSet, PacienteHistoriaAdjuntoViewSet, PacienteTelefonoViewSet
from MasterViewSets.viewsets_pacientes import PacienteEmailViewSet, PacienteHistoriaRecetaViewSet

# ROUTERS 
router.register('api/general/persona', PersonaViewSet, 'personas')
router.register('api/general/practica', PracticaViewSet, 'practicas')
router.register('api/general/centro', CentroViewSet, 'centros')
router.register('api/general/especialidad', EspecialidadViewSet, 'especialidades')
router.register('api/general/especialidadpractica', EspecialidadPracticaViewSet, 'especialidadespracticas')
router.register('api/general/cobertura', CoberturaViewSet, 'coberturas')
router.register('api/general/coberturaplan', CoberturaPlanViewSet, 'coberturasplanes')
router.register('api/general/practicaplan', PracticaPlanViewSet, 'practicasplanes')
router.register('api/general/documento', DocumentoViewSet, 'documentos')
router.register('api/general/genero', GeneroViewSet, 'generos')

# ROUTERS PROFESIONALES
router.register('api/profesionales/profesional', ProfesionalViewSet, 'profesionales')
router.register('api/profesionales/profesionalemail', ProfesionalEmailViewSet, 'profesionalemails') 
router.register('api/profesionales/profesionaltelefono', ProfesionalTelefonoViewSet, 'profesionaltelefonos')        
router.register('api/profesionales/profesionaldocumento', ProfesionalDocumentoViewSet, 'profesionaldocumentos')
router.register('api/profesionales/profesionalpractica', ProfesionalPracticaViewSet, 'profesionalpracticas')    
router.register('api/profesionales/profesionalpracticacentro', ProfesionalPracticaCentroViewSet, 'profesionalpracticacentros')  

# ROUTERS PACIENTES
router.register('api/pacientes/paciente', PacienteViewSet, 'pacientes')
router.register('api/pacientes/pacienteemail', PacienteEmailViewSet, 'pacienteemails')
router.register('api/pacientes/pacientetelefono', PacienteTelefonoViewSet, 'pacientetelefonos')
router.register('api/pacientes/pacientehistoria', PacienteHistoriaViewSet, 'pacientehistorias')
router.register('api/pacientes/pacientehistoriaadjunto', PacienteHistoriaAdjuntoViewSet, 'pacientehistoriasadjuntos')
router.register('api/pacientes/pacientehistoriareceta', PacienteHistoriaRecetaViewSet, 'pacientehistoriasrecetas')

urlpatterns = [
    path('', include(router.urls)),
    # ... otras URLs ...
]
