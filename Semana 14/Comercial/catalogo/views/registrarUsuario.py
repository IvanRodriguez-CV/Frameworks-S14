from django.contrib.auth import login
from django.shortcuts import redirect, render

from catalogo.forms.registrarUser_form import RegistrarUsuarioForm
from catalogo.models import Rol


def registrar_usuario(request):
    if request.method == "POST":
        form = RegistrarUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.rol = Rol.objects.get(nombre="Vendedor")
            usuario.save()
            login(request, usuario)
            return redirect("home")
    else:
        form = RegistrarUsuarioForm()

    return render(request, "registraUsuario/registraUsuario.html", {"form": form})
