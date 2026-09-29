from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="index"),

    path("reservas/", views.reservas_list, name="reservas_list"),
    path("reservas/crear/", views.reserva_create, name="reserva_create"),
    path("reservas/<int:pk>/editar/", views.reserva_update, name="reserva_update"),
    path("reservas/<int:pk>/", views.reserva_detail, name="reserva_detail"),
    path("reservas/<int:pk>/eliminar/", views.reserva_delete, name="reserva_delete"),

    path(
        "reservas/<int:pk>/confirmar/",
        views.confirmar_reserva,
        name="confirmar_reserva",
    ),
    path(
        "reservas/<int:pk>/cancelar/",
        views.cancelar_reserva,
        name="cancelar_reserva",
    ),

    path("gestion-reservas/", views.gestion_reservas, name="gestion_reservas"),
    path("mis-reservas/", views.mis_reservas, name="mis_reservas"),
    path("crear-reserva/", views.crear_reserva, name="crear_reserva"),
]