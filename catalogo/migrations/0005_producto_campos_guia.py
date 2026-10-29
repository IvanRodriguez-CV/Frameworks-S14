import decimal

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0004_merge_0003_alter_categoria_options_0003_producto"),
    ]

    operations = [
        migrations.AlterField(
            model_name="categoria",
            name="nombre",
            field=models.TextField(max_length=255),
        ),
        migrations.AlterField(
            model_name="categoria",
            name="descripcion",
            field=models.TextField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="categoria",
            name="created_at",
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name="categoria",
            name="updated_at",
            field=models.DateTimeField(),
        ),
        migrations.RenameField(
            model_name="producto",
            old_name="precio",
            new_name="precio_venta",
        ),
        migrations.AlterField(
            model_name="producto",
            name="precio_venta",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.RemoveField(
            model_name="producto",
            name="imagen",
        ),
        migrations.AddField(
            model_name="producto",
            name="precio_compra",
            field=models.DecimalField(
                decimal_places=2,
                default=decimal.Decimal("0.00"),
                max_digits=10,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="producto",
            name="nombre",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="producto",
            name="descripcion",
            field=models.TextField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="producto",
            name="stock",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="producto",
            name="categoria",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="productos",
                to="catalogo.categoria",
            ),
        ),
        migrations.AlterField(
            model_name="producto",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="producto",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterModelOptions(
            name="producto",
            options={},
        ),
    ]
