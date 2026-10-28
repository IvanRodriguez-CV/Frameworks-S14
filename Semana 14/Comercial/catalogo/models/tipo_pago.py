from django.db import models


class TipoPago(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    descripcion = models.TextField(
        max_length=255,
        blank=True,
        verbose_name="Descripción",
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización",
    )

    class Meta:
        verbose_name = "tipo de pago"
        verbose_name_plural = "tipos de pago"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
