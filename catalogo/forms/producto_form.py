from django import forms
from django.core.validators import FileExtensionValidator

from ..models.categoria import Categoria
from ..models.producto import Producto


class ProductoForm(forms.Form):
    nombre = forms.CharField(max_length=100, label="Nombre")
    descripcion = forms.CharField(
        max_length=255,
        required=False,
        label="Descripción",
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    precio_compra = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Precio de compra",
        min_value=0,
    )
    precio_venta = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Precio de venta",
        min_value=0,
    )
    stock = forms.IntegerField(min_value=0, label="Stock")
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        label="Categoría",
        empty_label="Seleccione una categoría",
    )
    imagen = forms.ImageField(
        required=False,
        label="Imagen",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png"])],
    )

    def clean(self):
        cleaned_data = super().clean()
        precio_compra = cleaned_data.get("precio_compra")
        precio_venta = cleaned_data.get("precio_venta")

        if (
            precio_compra is not None
            and precio_venta is not None
            and precio_venta <= precio_compra
        ):
            self.add_error(
                "precio_venta",
                "El precio de venta debe ser mayor que el precio de compra.",
            )

        return cleaned_data

    def save(self):
        return Producto.objects.create(
            nombre=self.cleaned_data["nombre"],
            descripcion=self.cleaned_data["descripcion"],
            precio_compra=self.cleaned_data["precio_compra"],
            precio_venta=self.cleaned_data["precio_venta"],
            stock=self.cleaned_data["stock"],
            categoria=self.cleaned_data["categoria"],
            imagen=self.cleaned_data.get("imagen", None),
        )

    def update(self, producto):
        producto.nombre = self.cleaned_data["nombre"]
        producto.descripcion = self.cleaned_data["descripcion"]
        producto.precio_compra = self.cleaned_data["precio_compra"]
        producto.precio_venta = self.cleaned_data["precio_venta"]
        producto.stock = self.cleaned_data["stock"]
        producto.categoria = self.cleaned_data["categoria"]
        imagen = self.cleaned_data.get("imagen")
        if imagen:
            producto.imagen = imagen
        producto.save()
        return producto
