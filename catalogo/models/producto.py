from django.db import models

from .categoria import Categoria


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=255, null=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    stock = models.PositiveIntegerField()
    imagen = models.ImageField(upload_to="productos/", blank=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="productos",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"id: {self.id} Nombre: {self.nombre} "
            f"Precio de compra: {self.precio_compra} "
            f"Precio de venta: {self.precio_venta} Stock: {self.stock}"
        )
