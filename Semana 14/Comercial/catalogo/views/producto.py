from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from catalogo.decorators import administrador_requerido
from catalogo.forms.producto_form import ProductoForm
from catalogo.models import Producto


@administrador_requerido
def lista_productos(request):
    productos = Paginator(
        Producto.objects.select_related("categoria").all(),
        10,
    ).get_page(request.GET.get("page"))
    return render(
        request,
        "producto/lista.html",
        {"productos": productos},
    )


@administrador_requerido
def agregar_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "El producto se creó correctamente.")
            return redirect("list_productos")
    else:
        form = ProductoForm()

    return render(request, "producto/add.html", {"form": form})


@administrador_requerido
def actualizar_producto(request, id):
    producto = get_object_or_404(Producto, pk=id)

    if request.method == "POST":
        nombre_imagen_anterior = producto.imagen.name
        almacenamiento_imagen = producto.imagen.storage
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto_guardado = form.save()
            nombre_imagen_nueva = producto_guardado.imagen.name
            if (
                nombre_imagen_anterior
                and nombre_imagen_nueva != nombre_imagen_anterior
            ):
                almacenamiento_imagen.delete(nombre_imagen_anterior)
            messages.success(request, "El producto se actualizó correctamente.")
            return redirect("list_productos")
    else:
        form = ProductoForm(instance=producto)

    return render(
        request,
        "producto/update.html",
        {"form": form, "producto": producto},
    )


@administrador_requerido
@require_POST
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, pk=id)
    nombre_imagen = producto.imagen.name
    almacenamiento_imagen = producto.imagen.storage
    producto.delete()
    if nombre_imagen:
        almacenamiento_imagen.delete(nombre_imagen)
    messages.success(request, "El producto se eliminó correctamente.")
    return redirect("list_productos")


@administrador_requerido
def reporte_productos(request):
    from weasyprint import HTML

    productos = Producto.objects.select_related("categoria").all()
    html = render_to_string(
        "producto/reporte.html",
        {"productos": productos, "fecha_reporte": timezone.localtime()},
        request=request,
    )
    pdf = HTML(
        string=html,
        base_url=request.build_absolute_uri("/"),
    ).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="reporte-productos.pdf"'
    return response
