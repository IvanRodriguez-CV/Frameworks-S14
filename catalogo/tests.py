from decimal import Decimal
from io import BytesIO
from types import SimpleNamespace
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from .models import Categoria, Producto, Rol, Usuario


class CategoriaTests(TestCase):
    def test_lista_sin_categorias_se_muestra(self):
        respuesta = self.client.get("/categoria/")

        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(respuesta.context["categorias"])

    def test_categoria_se_guarda_y_se_muestra_en_la_lista(self):
        ahora = timezone.now()
        categoria = Categoria.objects.create(
            nombre="Electrónicos",
            descripcion="Productos electrónicos",
            created_at=ahora,
            updated_at=ahora,
        )

        respuesta = self.client.get("/categoria/")

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Electrónicos")
        self.assertContains(respuesta, str(categoria.id))
        self.assertIn(categoria, respuesta.context["categorias"])

    def test_str_incluye_nombre_y_datos_del_registro(self):
        ahora = timezone.now()
        categoria = Categoria.objects.create(
            nombre="Libros",
            descripcion="Libros de práctica",
            created_at=ahora,
            updated_at=ahora,
        )

        self.assertIn("Libros", str(categoria))
        self.assertIn("id:", str(categoria))


class UsuarioTests(TestCase):
    def test_login_y_logout_redirigen_a_las_vistas_de_la_guia(self):
        Usuario.objects.create_user(
            username="usuario",
            password="UnaClaveSegura123!",
            rol_id=2,
        )

        respuesta = self.client.post(
            reverse("login"),
            {
                "username": "usuario",
                "password": "UnaClaveSegura123!",
            },
        )
        self.assertRedirects(respuesta, reverse("home"))
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)

        respuesta = self.client.post(reverse("logout"))
        self.assertRedirects(respuesta, reverse("inicio"))

    def test_superusuario_admite_el_id_del_rol(self):
        usuario = Usuario.objects.create_superuser(
            username="administrador",
            email="admin@example.com",
            password="UnaClaveSegura123!",
            telefono="123456789",
            rol="1",
        )

        self.assertTrue(usuario.is_superuser)
        self.assertTrue(usuario.is_staff)
        self.assertEqual(usuario.rol_id, 1)

    def test_registro_crea_vendedor_e_inicia_sesion(self):
        respuesta = self.client.post(
            reverse("registrar_usuario"),
            {
                "username": "vendedor1",
                "first_name": "Ana",
                "last_name": "Pérez",
                "email": "ana@example.com",
                "telefono": "123456789",
                "password1": "UnaClaveSegura123!",
                "password2": "UnaClaveSegura123!",
            },
        )

        usuario = Usuario.objects.get(username="vendedor1")
        self.assertRedirects(respuesta, reverse("home"))
        self.assertEqual(usuario.rol_id, 2)
        self.assertEqual(int(self.client.session["_auth_user_id"]), usuario.pk)

    def test_producto_requiere_sesion_y_rol_admin(self):
        respuesta = self.client.get(reverse("list_producto"))
        self.assertRedirects(
            respuesta,
            f"{reverse('login')}?next={reverse('list_producto')}",
        )

        vendedor = Usuario.objects.create_user(
            username="vendedor",
            password="UnaClaveSegura123!",
            rol_id=2,
        )
        self.client.force_login(vendedor)
        respuesta = self.client.get(reverse("list_producto"))

        self.assertRedirects(respuesta, reverse("home"))


class ProductoTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            username="admin",
            password="UnaClaveSegura123!",
            rol=Rol.objects.get(pk=1),
        )
        self.client.force_login(self.admin)
        ahora = timezone.now()
        self.categoria = Categoria.objects.create(
            nombre="Electrónicos",
            descripcion="Productos electrónicos",
            created_at=ahora,
            updated_at=ahora,
        )

    def crear_producto(self, nombre):
        return Producto.objects.create(
            nombre=nombre,
            descripcion="Descripción de prueba",
            precio_compra=Decimal("10.00"),
            precio_venta=Decimal("15.00"),
            stock=3,
            categoria=self.categoria,
        )

    def crear_imagen(self, nombre):
        contenido = BytesIO()
        Image.new("RGB", (1, 1), color="red").save(contenido, format="PNG")
        return SimpleUploadedFile(
            nombre,
            contenido.getvalue(),
            content_type="image/png",
        )

    def test_lista_pagina_productos_y_ajusta_numeros_invalidos(self):
        for numero in range(3):
            self.crear_producto(f"Producto {numero}")

        primera_pagina = self.client.get("/producto/")
        segunda_pagina = self.client.get("/producto/?page=2")
        pagina_invalida = self.client.get("/producto/?page=desconocida")
        pagina_fuera_de_rango = self.client.get("/producto/?page=99")

        self.assertEqual(primera_pagina.status_code, 200)
        self.assertEqual(len(primera_pagina.context["productos"]), 1)
        self.assertEqual(segunda_pagina.context["productos"].number, 2)
        self.assertEqual(len(segunda_pagina.context["productos"]), 1)
        self.assertEqual(pagina_invalida.context["productos"].number, 1)
        self.assertEqual(pagina_fuera_de_rango.context["productos"].number, 3)

    def test_reporte_devuelve_pdf_con_datos_de_productos(self):
        self.crear_producto("Producto de reporte")
        html = Mock()
        html.write_pdf.return_value = b"%PDF-1.4"
        weasyprint = SimpleNamespace(HTML=Mock(return_value=html))

        with patch.dict("sys.modules", {"weasyprint": weasyprint}):
            respuesta = self.client.get(reverse("reporte_producto"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta["Content-Type"], "application/pdf")
        self.assertEqual(
            respuesta["Content-Disposition"],
            'inline; filename="documento.ico.pdf"',
        )
        self.assertEqual(respuesta.content, b"%PDF-1.4")
        html_kwargs = weasyprint.HTML.call_args.kwargs
        self.assertIn("Producto de reporte", html_kwargs["string"])
        self.assertIn("Precio de venta", html_kwargs["string"])

    def test_crud_de_producto_guarda_y_limpia_imagenes(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                respuesta = self.client.post(
                    "/producto/agregar/",
                    {
                        "nombre": "Producto nuevo",
                        "descripcion": "Descripción del producto",
                        "precio_compra": "10.00",
                        "precio_venta": "15.00",
                        "stock": "3",
                        "categoria": str(self.categoria.pk),
                        "imagen": self.crear_imagen("producto.png"),
                    },
                )
                self.assertRedirects(respuesta, "/producto/")

                producto = Producto.objects.get(nombre="Producto nuevo")
                almacenamiento = producto.imagen.storage
                imagen_anterior = producto.imagen.name
                self.assertTrue(almacenamiento.exists(imagen_anterior))

                respuesta = self.client.post(
                    f"/producto/actualizar/{producto.pk}/",
                    {
                        "nombre": "Producto actualizado",
                        "descripcion": "Descripción actualizada",
                        "precio_compra": "12.00",
                        "precio_venta": "20.00",
                        "stock": "4",
                        "categoria": str(self.categoria.pk),
                        "imagen": self.crear_imagen("producto-nuevo.png"),
                    },
                )
                self.assertRedirects(respuesta, "/producto/")

                producto.refresh_from_db()
                imagen_nueva = producto.imagen.name
                self.assertEqual(producto.precio_compra, Decimal("12.00"))
                self.assertEqual(producto.precio_venta, Decimal("20.00"))
                self.assertFalse(almacenamiento.exists(imagen_anterior))
                self.assertTrue(almacenamiento.exists(imagen_nueva))

                respuesta = self.client.post(
                    f"/producto/actualizar/{producto.pk}/",
                    {
                        "nombre": "Producto sin cambiar imagen",
                        "descripcion": "Descripción actualizada",
                        "precio_compra": "12.00",
                        "precio_venta": "20.00",
                        "stock": "4",
                        "categoria": str(self.categoria.pk),
                    },
                )
                self.assertRedirects(respuesta, "/producto/")
                producto.refresh_from_db()
                self.assertEqual(producto.imagen.name, imagen_nueva)
                self.assertTrue(almacenamiento.exists(imagen_nueva))

                respuesta = self.client.get(
                    f"/producto/eliminar/{producto.pk}/"
                )
                self.assertRedirects(respuesta, "/producto/")
                self.assertFalse(Producto.objects.filter(pk=producto.pk).exists())
                self.assertFalse(almacenamiento.exists(imagen_nueva))

    def test_formulario_rechaza_extensiones_no_permitidas(self):
        respuesta = self.client.post(
            "/producto/agregar/",
            {
                "nombre": "Producto con imagen inválida",
                "descripcion": "Descripción del producto",
                "precio_compra": "10.00",
                "precio_venta": "15.00",
                "stock": "3",
                "categoria": str(self.categoria.pk),
                "imagen": self.crear_imagen("producto.gif"),
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("imagen", respuesta.context["form"].errors)
        self.assertFalse(Producto.objects.exists())

    def test_formulario_valida_que_el_precio_de_venta_sea_mayor(self):
        respuesta = self.client.post(
            "/producto/agregar/",
            {
                "nombre": "Producto con precio inválido",
                "descripcion": "Descripción del producto",
                "precio_compra": "15.00",
                "precio_venta": "15.00",
                "stock": "3",
                "categoria": str(self.categoria.pk),
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("precio_venta", respuesta.context["form"].errors)
        self.assertFalse(Producto.objects.exists())
