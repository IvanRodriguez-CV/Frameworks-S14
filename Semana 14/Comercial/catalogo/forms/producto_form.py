from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.validators import FileExtensionValidator

from catalogo.models import Categoria, Producto


class ProductoForm(forms.ModelForm):
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

    class Meta:
        model = Producto
        fields = (
            "nombre",
            "descripcion",
            "precio",
            "stock",
            "categoria",
            "imagen",
        )
        widgets = {
            "nombre": forms.TextInput(
                attrs={"placeholder": "Nombre del producto"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "placeholder": "Descripción del producto",
                    "rows": 4,
                }
            ),
            "precio": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"min": "0"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit("submit", "Guardar producto"))
