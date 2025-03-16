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

# URLS GENERALES
router.register('api/general/persona', PersonaViewSet, 'personas')
router.register('api/general/practica', PracticaViewSet, 'practicas')
router.register('api/general/centro', CentroViewSet, 'centros')
router.register('api/general/especialidad', EspecialidadViewSet, 'especialidades')


urlpatterns = [
    path('', include(router.urls)),
    # ... otras URLs ...
]
