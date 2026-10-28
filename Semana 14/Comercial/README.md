# Comercial - Semana 14

Proyecto de práctica Django: usuarios con roles, registro e inicio de sesión,
permisos por rol, catálogo de productos y reportes PDF.

## Preparar el entorno

Desde esta carpeta, en PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

La configuración predeterminada usa SQLite para que el proyecto funcione sin
un servidor de base de datos. Para usar MariaDB como en la guía, cree la base
de datos `comercial` y configure estas variables antes de ejecutar Django:

```powershell
$env:DB_ENGINE = "mysql"
$env:DB_NAME = "comercial"
$env:DB_USER = "root"
$env:DB_PASSWORD = "su contraseña"
$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "3307"
```

`mysqlclient` es el controlador de MySQL/MariaDB requerido para ese modo. No se
incluyen credenciales reales en el proyecto.
La guía indica Django 6.1 y sus capturas muestran Django 6.1.1. Esta versión
requiere Python 3.12 o posterior; use ese intérprete para crear el entorno
virtual e instalar las dependencias.

## Migraciones y servidor

```powershell
python .\manage.py migrate
python .\manage.py check
python .\manage.py runserver
```

Abra <http://127.0.0.1:8000/> para iniciar sesión o crear una cuenta. El registro
asigna el rol Vendedor; la administración de categorías, productos y reportes
está reservada al rol Administrador. La migración inicial agrega las categorías
de ejemplo `tv` y `Laptop`.

## Productos y categorías

`Producto` se define en `catalogo/models/producto.py` y contiene nombre,
descripción, precio, existencias e imagen. Cada producto pertenece a una
categoría mediante una relación muchos-a-uno (`ForeignKey`): una categoría se
puede consultar con `categoria.productos.all()`. Al eliminar una categoría,
Django elimina también sus productos (`CASCADE`). Las imágenes se almacenan en
`media/productos/` en desarrollo.

Pillow e IPython están incluidos en `requirements.txt`. Pillow permite usar
`ImageField`; IPython habilita la consola interactiva mejorada del comando
`shell`.

## CRUD y paginación de productos

El formulario permite relacionar cada producto con una categoría y cargar una
imagen JPG o PNG (opcional). Las imágenes se guardan en `media/productos/`;
al reemplazar o eliminar un producto también se limpia su imagen anterior.

El listado muestra diez productos por página, con enlaces para ir a la primera,
anterior, siguiente y última página. Django ajusta automáticamente los números
de página inválidos.

Ejecuta `python .\manage.py test catalogo` para probar el CRUD, las imágenes y
la navegación de páginas.

Para crear un producto desde la consola interactiva, sustituye la ruta de
ejemplo por la ruta de una imagen existente:

```powershell
python .\manage.py shell
```

```python
from decimal import Decimal
from pathlib import Path

from django.core.files import File
from catalogo.models import Categoria, Producto

categoria = Categoria.objects.get(nombre="tv")
imagen_path = Path(r"C:\ruta\a\televisor.png")
with imagen_path.open("rb") as archivo:
    producto = Producto.objects.create(
        nombre="Televisor de ejemplo",
        descripcion="Televisor asociado a una categoría",
        precio=Decimal("349.99"),
        stock=5,
        imagen=File(archivo, name=imagen_path.name),
        categoria=categoria,
    )
categoria.productos.all()
```

Para probar la relación, la carga de imágenes y el borrado en cascada:

```powershell
python .\manage.py test catalogo
```

## Probar el modelo desde Django Shell

```powershell
python .\manage.py shell
```

En la consola interactiva:

```python
from django.utils import timezone
from catalogo.models import Categoria

ahora = timezone.now()
categoria = Categoria.objects.create(
    nombre="Electrónicos",
    descripcion="Productos electrónicos",
    created_at=ahora,
    updated_at=ahora,
)
print(categoria)
categoria.nombre = "Televisores"
categoria.save()
categoria.delete()
```

Los otros modelos disponibles son `TipoPago`, `Cliente` y `Rol`. Las plantillas
comparten `templates/base.html`, incluyen el menú desde `templates/menu.html`
y usan Django Crispy Forms con Tailwind en los formularios de alta y edición.

Para ejecutar las pruebas:

```powershell
python .\manage.py test
```

En modo MariaDB también puede inspeccionar las tablas con
`python .\manage.py dbshell` y, dentro de la consola SQL, ejecutar
`SHOW TABLES;` o `DESCRIBE catalogo_categoria;`.

## Práctica 1: cuentas y autenticación

El modelo `Usuario` extiende el usuario de Django con teléfono y rol. Para
crear el administrador inicial, después de aplicar las migraciones, ejecuta:

```powershell
python .\manage.py createsuperuser
```

El comando solicita nombre de usuario, correo, nombres, teléfono y rol. El rol
con ID 1 es Administrador y el rol con ID 2 es Vendedor. Las cuentas creadas
desde la página de registro reciben automáticamente el rol Vendedor.

## Práctica 2: sesión y permisos

La página `/home/` exige una sesión activa. Los usuarios Vendedor no pueden
acceder a las vistas de administración de productos; los usuarios
Administradores y superusuarios sí. El cierre de sesión utiliza un formulario
POST con protección CSRF.

## Práctica 3: reporte imprimible

El botón **Imprimir reporte** genera un PDF con todos los productos y sus
categorías. `WeasyPrint` ya está incluido en `requirements.txt`. En Windows, instala
MSYS2, abre su terminal UCRT64 y ejecuta el comando de Pango indicado en la
guía antes de generar el reporte:

```bash
pacman -S mingw-w64-ucrt-x86_64-pango
```

Este proyecto de la semana 14 parte de una copia independiente de Semana 13.
Su migración inicial incluye el modelo de usuario personalizado; no borres la
base de datos ni las migraciones del proyecto anterior.
