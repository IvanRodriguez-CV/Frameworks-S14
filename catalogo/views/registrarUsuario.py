from django.contrib.auth import login
from django.shortcuts import redirect, render

from catalogo.forms.registrarUser_form import RegistrarUsuarioForm


def registrar_usuario(request):
    if request.method == "POST":
        form = RegistrarUsuarioForm(request.POST)
        if form.is_valid():
            form.instance.rol_id = 2
            usuario = form.save()
            login(request, usuario)
            return redirect("home")
    else:
        form = RegistrarUsuarioForm()

    return render(request, "registraUsuario/registraUsuario.html", {"form": form})
