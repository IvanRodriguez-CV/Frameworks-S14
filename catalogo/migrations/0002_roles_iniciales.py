from django.db import migrations


def crear_roles_iniciales(apps, schema_editor):
    Rol = apps.get_model("catalogo", "Rol")
    db_alias = schema_editor.connection.alias
    roles = Rol.objects.using(db_alias)
    roles.get_or_create(
        pk=1,
        defaults={
            "nombre": "Administrador",
            "descripcion": "Administra el catálogo comercial.",
            "activo": True,
        },
    )
    roles.get_or_create(
        pk=2,
        defaults={
            "nombre": "Vendedor",
            "descripcion": "Usuario vendedor del sistema.",
            "activo": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("catalogo", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            crear_roles_iniciales,
            migrations.RunPython.noop,
        ),
    ]
