from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from .rol import Rol


class UsuarioManager(UserManager):
    pass


class Usuario(AbstractUser):
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        related_name="usuarios",
        verbose_name="Rol",
        default=2,
    )

    objects = UsuarioManager()
    REQUIRED_FIELDS = ["email", "first_name", "last_name", "telefono", "rol"]

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return self.get_full_name() or self.username
