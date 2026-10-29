from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0005_producto_campos_guia"),
    ]

    operations = [
        migrations.AddField(
            model_name="producto",
            name="imagen",
            field=models.ImageField(blank=True, upload_to="productos/"),
        ),
    ]
