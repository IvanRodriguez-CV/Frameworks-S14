from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from .rol import Rol


class UsuarioManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        rol = extra_fields.get("rol")
        if rol is not None and not isinstance(rol, Rol):
            extra_fields["rol"] = Rol.objects.db_manager(self.db).get(pk=rol)

        return super().create_superuser(
            username,
            email=email,
            password=password,
            **extra_fields,
        )


class Usuario(AbstractUser):
    telefono = models.TextField(max_length=9, verbose_name="Teléfono")
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        related_name="usuarios",
        verbose_name="Rol",
        default=2,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización",
    )

    objects = UsuarioManager()
    REQUIRED_FIELDS = ["email", "first_name", "last_name", "telefono", "rol"]

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return f"Nombre: {self.first_name} Apellido: {self.last_name}"
