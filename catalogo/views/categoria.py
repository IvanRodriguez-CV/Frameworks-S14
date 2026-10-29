from django.shortcuts import get_object_or_404, redirect, render

from ..forms.categoria_form import CategoriaForm
from ..models.categoria import Categoria


def lista_categorias(request):
    lista_categorias = Categoria.objects.all()
    return render(
        request,
        "categoria/lista.html",
        {"categorias": lista_categorias},
    )


def delete_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    categoria.delete()
    return redirect("list_categoria")


def add_categoria(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("list_categoria")
        else:
            return render(
                request,
                "categoria/add.html",
                {"form": form},
            )

    return render(
        request,
        "categoria/add.html",
        {"form": CategoriaForm()},
    )


def update_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.update(categoria)
            return redirect("list_categoria")
        else:
            return render(
                request,
                "categoria/update.html",
                {"form": form, "categoria": categoria},
            )

    form = CategoriaForm(
        initial={
            "nombre": categoria.nombre,
            "descripcion": categoria.descripcion,
        }
    )
    return render(
        request,
        "categoria/update.html",
        {"form": form, "categoria": categoria},
    )
