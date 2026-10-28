from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views.inicio import home, inicio
from .views.registrarUsuario import registrar_usuario
from .views.categoria import (
    actualizar_categoria,
    agregar_categoria,
    eliminar_categoria,
    lista_categorias,
)
from .views.producto import (
    actualizar_producto,
    agregar_producto,
    eliminar_producto,
    lista_productos,
    reporte_productos,
)


urlpatterns = [
    path("", inicio, name="inicio"),
    path("home/", home, name="home"),
    path(
        "login/",
        LoginView.as_view(
            template_name="login/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("registrar/", registrar_usuario, name="registrar_usuario"),
    path("categoria/", lista_categorias, name="list_categorias"),
    path("categoria/add/", agregar_categoria, name="add_categoria"),
    path(
        "categoria/<int:id>/update/",
        actualizar_categoria,
        name="update_categoria",
    ),
    path(
        "categoria/<int:id>/delete/",
        eliminar_categoria,
        name="delete_categoria",
    ),
    path("productos/", lista_productos, name="list_productos"),
    path("productos/reporte/", reporte_productos, name="reporte_productos"),
    path("productos/add/", agregar_producto, name="add_producto"),
    path(
        "productos/<int:id>/update/",
        actualizar_producto,
        name="update_producto",
    ),
    path(
        "productos/<int:id>/delete/",
        eliminar_producto,
        name="delete_producto",
    ),
]
