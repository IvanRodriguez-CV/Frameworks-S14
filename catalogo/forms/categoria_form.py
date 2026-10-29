from django import forms
from django.utils import timezone

from ..models.categoria import Categoria


class CategoriaForm(forms.Form):
    nombre = forms.CharField(max_length=255, label="Nombre", required=True)
    descripcion = forms.CharField(
        max_length=255,
        label="Descripción",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def save(self):
        Categoria.objects.create(
            nombre=self.cleaned_data["nombre"],
            descripcion=self.cleaned_data["descripcion"],
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

    def update(self, categoria):
        categoria.nombre = self.cleaned_data["nombre"]
        categoria.descripcion = self.cleaned_data["descripcion"]
        categoria.updated_at = timezone.now()
        categoria.save()
