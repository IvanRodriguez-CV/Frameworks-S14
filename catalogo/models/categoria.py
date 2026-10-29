from django.db import models


class Categoria(models.Model):
    nombre = models.TextField(max_length=255)
    descripcion = models.TextField(max_length=255, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return (
            f"id: {self.id} Nombre: {self.nombre} "
            f"Description: {self.descripcion} "
            f"Fecha de creación : {self.created_at} "
            f"Fecha de actualización {self.updated_at}"
        )
