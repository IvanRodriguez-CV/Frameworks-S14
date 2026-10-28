from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from catalogo.decorators import administrador_requerido
from catalogo.forms.categoria_form import CategoriaForm
from catalogo.models import Categoria


def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(
        request,
        "categoria/lista.html",
        {"categorias": categorias},
    )


@administrador_requerido
def agregar_categoria(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.created_at = timezone.now()
            categoria.updated_at = categoria.created_at
            categoria.save()
            messages.success(request, "La categoría se creó correctamente.")
            return redirect("list_categorias")
    else:
        form = CategoriaForm()

    return render(
        request,
        "categoria/add.html",
        {"form": form},
    )


@administrador_requerido
def actualizar_categoria(request, id):
    categoria = get_object_or_404(Categoria, pk=id)
    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.updated_at = timezone.now()
            categoria.save()
            messages.success(request, "La categoría se actualizó correctamente.")
            return redirect("list_categorias")
    else:
        form = CategoriaForm(instance=categoria)

    return render(
        request,
        "categoria/update.html",
        {"form": form, "categoria": categoria},
    )


@administrador_requerido
@require_POST
def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categoria, pk=id)
    categoria.delete()
    messages.success(request, "La categoría se eliminó correctamente.")
    return redirect("list_categorias")
