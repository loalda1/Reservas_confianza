from django.contrib import admin
from .models import Cliente, Reserva


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "telefono", "usuario")
    search_fields = ("nombre", "email", "usuario__username")


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        "cliente",
        "fecha_inicio",
        "fecha_fin",
        "estado",
        "fecha_creacion",
    )
    list_filter = (
        "estado",
        "fecha_inicio",
        "fecha_fin",
    )
    search_fields = (
        "cliente__nombre",
        "cliente__email",
    )