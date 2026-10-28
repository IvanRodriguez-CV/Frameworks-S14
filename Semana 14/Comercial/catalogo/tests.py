from decimal import Decimal
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from .models import Categoria, Cliente, Producto, Rol, TipoPago


class CategoriaTests(TestCase):
    def setUp(self):
        usuario_admin = get_user_model().objects.create_user(
            username="admin_categoria",
            password="Practica-2026-Segura!",
            rol=Rol.objects.get(nombre="Administrador"),
        )
        self.client.force_login(usuario_admin)

    def test_categorias_de_ejemplo_se_crean_con_la_migracion(self):
        self.assertTrue(
            Categoria.objects.filter(
                nombre="tv",
                descripcion="Televisores de alta gama",
            ).exists()
        )
        self.assertTrue(
            Categoria.objects.filter(
                nombre="Laptop",
                descripcion="Computadoras portátiles",
            ).exists()
        )

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
        self.assertContains(respuesta, "Productos electrónicos")
        self.assertIn(categoria, respuesta.context["categorias"])

    def test_lista_vacia_se_muestra_sin_error(self):
        Categoria.objects.all().delete()
        respuesta = self.client.get("/categoria/")

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Aún no hay categorías registradas.")

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

    def test_crear_categoria_desde_formulario(self):
        respuesta = self.client.post(
            reverse("add_categoria"),
            {"nombre": "Accesorios", "descripcion": "Accesorios varios"},
        )

        self.assertRedirects(respuesta, reverse("list_categorias"))
        categoria = Categoria.objects.get(nombre="Accesorios")
        self.assertEqual(categoria.descripcion, "Accesorios varios")
        self.assertIsNotNone(categoria.created_at)
        self.assertIsNotNone(categoria.updated_at)

    def test_formulario_invalido_muestra_errores(self):
        respuesta = self.client.post(
            reverse("add_categoria"),
            {"nombre": "", "descripcion": "Sin nombre"},
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Este campo es obligatorio.")
        self.assertEqual(Categoria.objects.count(), 2)

    def test_actualizar_categoria_existente(self):
        categoria = Categoria.objects.get(nombre="tv")

        respuesta = self.client.post(
            reverse("update_categoria", args=[categoria.pk]),
            {"nombre": "Televisores", "descripcion": "Pantallas"},
        )

        self.assertRedirects(respuesta, reverse("list_categorias"))
        categoria.refresh_from_db()
        self.assertEqual(categoria.nombre, "Televisores")
        self.assertEqual(categoria.descripcion, "Pantallas")

    def test_actualizar_categoria_inexistente_responde_404(self):
        respuesta = self.client.get(
            reverse("update_categoria", args=[9999]),
        )

        self.assertEqual(respuesta.status_code, 404)

    def test_eliminar_categoria_requiere_post_y_elimina(self):
        categoria = Categoria.objects.get(nombre="tv")
        url = reverse("delete_categoria", args=[categoria.pk])

        self.assertEqual(self.client.get(url).status_code, 405)
        respuesta = self.client.post(url)

        self.assertRedirects(respuesta, reverse("list_categorias"))
        self.assertFalse(Categoria.objects.filter(pk=categoria.pk).exists())


class ModelosDeTareasTests(TestCase):
    def test_tipos_de_pago_clientes_y_roles_se_guardan(self):
        tipo_pago = TipoPago.objects.create(nombre="Tarjeta")
        cliente = Cliente.objects.create(
            nombres="Ana",
            apellidos="Pérez",
            email="ana@example.com",
        )
        rol = Rol.objects.create(nombre="Supervisor")

        self.assertEqual(TipoPago.objects.get(pk=tipo_pago.pk).nombre, "Tarjeta")
        self.assertEqual(str(cliente), "Ana Pérez")
        self.assertEqual(Rol.objects.get(pk=rol.pk).nombre, "Supervisor")


class ProductoTests(TestCase):
    def test_categoria_se_relaciona_con_producto_y_lo_elimina_en_cascada(self):
        categoria = Categoria.objects.create(
            nombre="Televisores",
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
        image_buffer = BytesIO()
        Image.new("RGB", (1, 1)).save(image_buffer, format="PNG")

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                producto = Producto.objects.create(
                    nombre="Televisor",
                    descripcion="Televisor de prueba",
                    precio=Decimal("349.99"),
                    stock=3,
                    imagen=SimpleUploadedFile(
                        "televisor.png",
                        image_buffer.getvalue(),
                        content_type="image/png",
                    ),
                    categoria=categoria,
                )

                self.assertEqual(producto.categoria, categoria)
                self.assertEqual(list(categoria.productos.all()), [producto])
                self.assertTrue(producto.imagen.name.startswith("productos/"))
                self.assertEqual(str(producto), "Televisor")

                categoria.delete()

                self.assertFalse(Producto.objects.filter(pk=producto.pk).exists())

                producto.imagen.delete(save=False)


class CrudProductoTests(TestCase):
    def setUp(self):
        self.media_directory = TemporaryDirectory()
        media_settings = override_settings(MEDIA_ROOT=self.media_directory.name)
        media_settings.enable()
        self.addCleanup(media_settings.disable)
        self.addCleanup(self.media_directory.cleanup)
        ahora = timezone.now()
        self.categoria = Categoria.objects.create(
            nombre="Electrónica",
            created_at=ahora,
            updated_at=ahora,
        )
        self.rol_admin = Rol.objects.get(nombre="Administrador")
        self.usuario_admin = get_user_model().objects.create_user(
            username="admin_prueba",
            password="Practica-2026-Segura!",
            rol=self.rol_admin,
        )
        self.client.force_login(self.usuario_admin)

    def _imagen(self, nombre="producto.png", formato="PNG"):
        image_buffer = BytesIO()
        Image.new("RGB", (1, 1)).save(image_buffer, format=formato)
        content_type = "image/png" if formato == "PNG" else "image/jpeg"
        return SimpleUploadedFile(
            nombre,
            image_buffer.getvalue(),
            content_type=content_type,
        )

    def _crear_producto(self, nombre):
        return Producto.objects.create(
            nombre=nombre,
            precio=Decimal("10.00"),
            stock=1,
            categoria=self.categoria,
        )

    def test_lista_productos_muestra_diez_por_pagina_y_navegacion(self):
        for numero in range(12):
            self._crear_producto(f"Producto {numero:02}")

        primera_pagina = self.client.get(reverse("list_productos"))
        segunda_pagina = self.client.get(
            reverse("list_productos"),
            {"page": 2},
        )

        self.assertEqual(primera_pagina.status_code, 200)
        self.assertEqual(len(primera_pagina.context["productos"]), 10)
        self.assertContains(primera_pagina, "Siguiente")
        self.assertContains(primera_pagina, "Última")
        self.assertEqual(len(segunda_pagina.context["productos"]), 2)
        self.assertContains(segunda_pagina, "Anterior")
        self.assertNotContains(segunda_pagina, "Siguiente")

    def test_pagina_invalida_muestra_la_primera_pagina(self):
        self._crear_producto("Producto inicial")

        respuesta = self.client.get(
            reverse("list_productos"),
            {"page": "no-valida"},
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["productos"].number, 1)

    def test_crear_producto_con_imagen(self):
        respuesta = self.client.post(
            reverse("add_producto"),
            {
                "nombre": "Teclado",
                "descripcion": "Teclado de prueba",
                "precio": "24.99",
                "stock": "4",
                "categoria": self.categoria.pk,
                "imagen": self._imagen(),
            },
        )

        self.assertRedirects(respuesta, reverse("list_productos"))
        producto = Producto.objects.get(nombre="Teclado")
        self.assertEqual(producto.categoria, self.categoria)
        self.assertTrue(
            (Path(self.media_directory.name) / producto.imagen.name).is_file()
        )

    def test_crear_producto_sin_imagen(self):
        respuesta = self.client.post(
            reverse("add_producto"),
            {
                "nombre": "Producto sin imagen",
                "precio": "12.00",
                "stock": "1",
                "categoria": self.categoria.pk,
            },
        )

        self.assertRedirects(respuesta, reverse("list_productos"))
        producto = Producto.objects.get(nombre="Producto sin imagen")
        self.assertFalse(producto.imagen)

    def test_rechazar_imagen_con_extension_no_permitida(self):
        respuesta = self.client.post(
            reverse("add_producto"),
            {
                "nombre": "Producto inválido",
                "precio": "12.00",
                "stock": "1",
                "categoria": self.categoria.pk,
                "imagen": self._imagen("producto.gif"),
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["form"].has_error("imagen"))
        self.assertIn("jpg, png", str(respuesta.context["form"].errors["imagen"]))
        self.assertFalse(Producto.objects.filter(nombre="Producto inválido").exists())

    def test_actualizar_producto_reemplaza_y_elimina_imagen_anterior(self):
        producto = self._crear_producto("Teclado")
        producto.imagen.save("anterior.png", self._imagen(), save=True)
        imagen_anterior = Path(self.media_directory.name) / producto.imagen.name

        respuesta = self.client.post(
            reverse("update_producto", args=[producto.pk]),
            {
                "nombre": "Teclado actualizado",
                "descripcion": "Descripción actualizada",
                "precio": "30.00",
                "stock": "5",
                "categoria": self.categoria.pk,
                "imagen": self._imagen("nueva.jpg", "JPEG"),
            },
        )

        self.assertRedirects(respuesta, reverse("list_productos"))
        producto.refresh_from_db()
        self.assertEqual(producto.nombre, "Teclado actualizado")
        self.assertFalse(imagen_anterior.exists())
        self.assertTrue(
            (Path(self.media_directory.name) / producto.imagen.name).is_file()
        )

    def test_eliminar_producto_requiere_post_y_borra_su_imagen(self):
        producto = self._crear_producto("Teclado")
        producto.imagen.save("teclado.png", self._imagen(), save=True)
        url = reverse("delete_producto", args=[producto.pk])
        ruta_imagen = Path(self.media_directory.name) / producto.imagen.name

        self.assertEqual(self.client.get(url).status_code, 405)
        respuesta = self.client.post(url)

        self.assertRedirects(respuesta, reverse("list_productos"))
        self.assertFalse(Producto.objects.filter(pk=producto.pk).exists())
        self.assertFalse(ruta_imagen.exists())


class AutenticacionYPermisosTests(TestCase):
    def setUp(self):
        self.rol_vendedor = Rol.objects.get(nombre="Vendedor")
        self.usuario_vendedor = get_user_model().objects.create_user(
            username="vendedor_prueba",
            password="Practica-2026-Segura!",
            rol=self.rol_vendedor,
        )

    def test_home_requiere_sesion_iniciada(self):
        respuesta = self.client.get(reverse("home"))

        self.assertRedirects(
            respuesta,
            f"{reverse('login')}?next={reverse('home')}",
        )

    def test_pagina_inicial_es_publica(self):
        respuesta = self.client.get(reverse("inicio"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Iniciar sesión")

    def test_registro_crea_vendedor_e_inicia_sesion(self):
        respuesta = self.client.post(
            reverse("registrar_usuario"),
            {
                "username": "nuevo_vendedor",
                "first_name": "Ana",
                "last_name": "Pérez",
                "email": "ana@example.com",
                "telefono": "555-0101",
                "password1": "Practica-2026-Segura!",
                "password2": "Practica-2026-Segura!",
            },
        )

        self.assertRedirects(respuesta, reverse("home"))
        usuario = get_user_model().objects.get(username="nuevo_vendedor")
        self.assertEqual(usuario.rol, self.rol_vendedor)
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            usuario.pk,
        )

    def test_login_autentica_al_usuario_registrado(self):
        respuesta = self.client.post(
            reverse("login"),
            {
                "username": "vendedor_prueba",
                "password": "Practica-2026-Segura!",
            },
        )

        self.assertRedirects(respuesta, reverse("home"))
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.usuario_vendedor.pk,
        )

    def test_cierre_de_sesion_usa_post(self):
        self.client.force_login(self.usuario_vendedor)

        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        respuesta = self.client.post(reverse("logout"))

        self.assertRedirects(respuesta, reverse("inicio"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_vendedor_no_puede_ver_productos_de_administracion(self):
        self.client.force_login(self.usuario_vendedor)

        respuesta = self.client.get(reverse("list_productos"))

        self.assertRedirects(respuesta, reverse("home"))

    def test_vendedor_no_puede_crear_categorias(self):
        self.client.force_login(self.usuario_vendedor)

        respuesta = self.client.get(reverse("add_categoria"))

        self.assertRedirects(respuesta, reverse("home"))

    def test_reporte_es_pdf_para_administrador(self):
        import sys
        from types import SimpleNamespace
        from unittest.mock import Mock, patch

        self.client.force_login(
            get_user_model().objects.create_user(
                username="admin_reporte",
                password="Practica-2026-Segura!",
                rol=Rol.objects.get(nombre="Administrador"),
            )
        )
        html = Mock()
        html.return_value.write_pdf.return_value = b"%PDF-1.7"
        with patch.dict(
            sys.modules,
            {"weasyprint": SimpleNamespace(HTML=html)},
        ):
            respuesta = self.client.get(reverse("reporte_productos"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta["Content-Type"], "application/pdf")
        self.assertEqual(respuesta.content, b"%PDF-1.7")
        self.assertIn("Reporte de productos", html.call_args.kwargs["string"])
