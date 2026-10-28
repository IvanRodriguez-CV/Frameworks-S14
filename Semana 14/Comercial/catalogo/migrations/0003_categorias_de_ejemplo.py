from django.db import migrations
from django.utils import timezone


def crear_categorias_de_ejemplo(apps, schema_editor):
    Categoria = apps.get_model("catalogo", "Categoria")
    db_alias = schema_editor.connection.alias
    categorias = Categoria.objects.using(db_alias)

    if categorias.exists():
        return

    ahora = timezone.now()
    categorias.bulk_create(
        [
            Categoria(
                nombre="tv",
                descripcion="Televisores de alta gama",
                created_at=ahora,
                updated_at=ahora,
            ),
            Categoria(
                nombre="Laptop",
                descripcion="Computadoras portátiles",
                created_at=ahora,
                updated_at=ahora,
            ),
        ]
    )


class Migration(migrations.Migration):
    dependencies = [
        ("catalogo", "0002_roles_iniciales"),
    ]

    operations = [
        migrations.RunPython(
            crear_categorias_de_ejemplo,
            migrations.RunPython.noop,
        ),
    ]
