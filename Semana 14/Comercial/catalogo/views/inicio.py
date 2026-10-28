from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def inicio(request):
    return render(request, "inicio/inicio.html")


@login_required
def home(request):
    return render(request, "home/home.html")
