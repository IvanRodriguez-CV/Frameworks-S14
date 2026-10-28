from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def es_administrador(usuario):
    return usuario.is_superuser or (
        usuario.rol_id is not None
        and usuario.rol.nombre.casefold() == "administrador"
    )


def administrador_requerido(vista):
    @login_required
    @wraps(vista)
    def protegida(request, *args, **kwargs):
        if not es_administrador(request.user):
            return redirect("home")
        return vista(request, *args, **kwargs)

    return protegida
