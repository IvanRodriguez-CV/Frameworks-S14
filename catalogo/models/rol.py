from django.db import models


class Rol(models.Model):
    nombre = models.TextField(max_length=50, verbose_name="Nombre")
    descripcion = models.TextField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Descripción",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización",
    )

    def __str__(self):
        return self.nombre
