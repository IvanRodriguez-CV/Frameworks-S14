from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views.categoria import (
    add_categoria,
    delete_categoria,
    lista_categorias,
    update_categoria,
)
from .views.inicio import home, inicio
from .views.producto import (
    add_producto,
    delete_producto,
    lista_productos,
    reporte_producto,
    update_producto,
)
from .views.registrarUsuario import registrar_usuario


urlpatterns = [
    path("", inicio, name="inicio"),
    path("home/", home, name="home"),
    path(
        "login/",
        LoginView.as_view(template_name="login/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("registro/", registrar_usuario, name="registrar_usuario"),
    path("categoria/", lista_categorias, name="list_categoria"),
    path("categoria/agregar/", add_categoria, name="add_categoria"),
    path(
        "categoria/actualizar/<int:id>/",
        update_categoria,
        name="update_categoria",
    ),
    path(
        "categoria/eliminar/<int:id>/",
        delete_categoria,
        name="delete_categoria",
    ),
    path("producto/", lista_productos, name="list_producto"),
    path("producto/agregar/", add_producto, name="add_producto"),
    path(
        "producto/actualizar/<int:id>/",
        update_producto,
        name="update_producto",
    ),
    path(
        "producto/eliminar/<int:id>/",
        delete_producto,
        name="delete_producto",
    ),
    path("producto/reporte/", reporte_producto, name="reporte_producto"),
]
