from django.db import models
from ..universal import AuditModel, TenantModel
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

class Persona(models.Model):
    """ Clase para manejar los datos de una persona """
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personas')
    password = models.CharField(max_length=128)  # Considera usar un campo de contraseña más seguro
    mail = models.EmailField(max_length=254, unique=True)  # Agregando el campo mail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    disabled = models.BooleanField(default=False)
    user_id = models.BigIntegerField(default=0)

    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'GRAL - Personas'

    def set_password(self, raw_password):
        """ Setea la password con seguridad """
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """ Valida el password con un metodo seguro """
        return check_password(raw_password, self.password)

    def __str__(self):
        return f'{self.nombre}'
    





    
