from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


GROUP_NAMES = {
    "cliente": "customers",
    "empleado": "employees",
    "administradores": "administrators",
}

PERMISSION_NAMES = {
    "add_cliente": "Can add customer",
    "change_cliente": "Can change customer",
    "delete_cliente": "Can delete customer",
    "view_cliente": "Can view customer",
    "add_reserva": "Can add booking",
    "change_reserva": "Can change booking",
    "delete_reserva": "Can delete booking",
    "view_reserva": "Can view booking",
}


def translate_admin_data(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    for old_name, new_name in GROUP_NAMES.items():
        if not Group.objects.filter(name=new_name).exists():
            Group.objects.filter(name=old_name).update(name=new_name)

    for codename, name in PERMISSION_NAMES.items():
        Permission.objects.filter(
            content_type__app_label="main",
            codename=codename,
        ).update(name=name)


def restore_admin_data(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    for old_name, new_name in GROUP_NAMES.items():
        if not Group.objects.filter(name=old_name).exists():
            Group.objects.filter(name=new_name).update(name=old_name)

    reverse_permissions = {
        "add_cliente": "Can add cliente",
        "change_cliente": "Can change cliente",
        "delete_cliente": "Can delete cliente",
        "view_cliente": "Can view cliente",
        "add_reserva": "Can add reserva",
        "change_reserva": "Can change reserva",
        "delete_reserva": "Can delete reserva",
        "view_reserva": "Can view reserva",
    }

    for codename, name in reverse_permissions.items():
        Permission.objects.filter(
            content_type__app_label="main",
            codename=codename,
        ).update(name=name)


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0004_reserva_estado_reserva_fecha_creacion"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="cliente",
            options={
                "verbose_name": "customer",
                "verbose_name_plural": "customers",
            },
        ),
        migrations.AlterModelOptions(
            name="reserva",
            options={
                "verbose_name": "booking",
                "verbose_name_plural": "bookings",
            },
        ),
        migrations.AlterField(
            model_name="cliente",
            name="usuario",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="perfil_cliente",
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="nombre",
            field=models.CharField(max_length=100, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="email",
            field=models.EmailField(
                max_length=254,
                unique=True,
                verbose_name="email address",
            ),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="telefono",
            field=models.CharField(
                blank=True,
                max_length=20,
                verbose_name="phone number",
            ),
        ),
        migrations.AlterField(
            model_name="reserva",
            name="cliente",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="main.cliente",
                verbose_name="customer",
            ),
        ),
        migrations.AlterField(
            model_name="reserva",
            name="fecha_inicio",
            field=models.DateField(verbose_name="start date"),
        ),
        migrations.AlterField(
            model_name="reserva",
            name="fecha_fin",
            field=models.DateField(verbose_name="end date"),
        ),
        migrations.AlterField(
            model_name="reserva",
            name="estado",
            field=models.CharField(
                choices=[
                    ("pendiente", "Pending"),
                    ("confirmada", "Confirmed"),
                    ("cancelada", "Cancelled"),
                    ("finalizada", "Completed"),
                ],
                default="pendiente",
                max_length=20,
                verbose_name="status",
            ),
        ),
        migrations.AlterField(
            model_name="reserva",
            name="fecha_creacion",
            field=models.DateTimeField(
                auto_now_add=True,
                blank=True,
                null=True,
                verbose_name="created at",
            ),
        ),
        migrations.RunPython(translate_admin_data, restore_admin_data),
    ]
