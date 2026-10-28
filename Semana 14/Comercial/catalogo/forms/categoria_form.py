from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from catalogo.models import Categoria


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ("nombre", "descripcion")
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "placeholder": "Nombre de la categoría",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "placeholder": "Descripción de la categoría",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit("submit", "Guardar categoría"))
