from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Cliente(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_cliente",
        null=True,
        blank=True,
        verbose_name="user",
    )

    nombre = models.CharField("name", max_length=100)
    email = models.EmailField("email address", unique=True)
    telefono = models.CharField("phone number", max_length=20, blank=True)

    class Meta:
        verbose_name = "customer"
        verbose_name_plural = "customers"

    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_CONFIRMADA = "confirmada"
    ESTADO_CANCELADA = "cancelada"
    ESTADO_FINALIZADA = "finalizada"

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "Pending"),
        (ESTADO_CONFIRMADA, "Confirmed"),
        (ESTADO_CANCELADA, "Cancelled"),
        (ESTADO_FINALIZADA, "Completed"),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        verbose_name="customer",
    )
    fecha_inicio = models.DateField("start date")
    fecha_fin = models.DateField("end date")

    estado = models.CharField(
        "status",
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_PENDIENTE,
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
        verbose_name="created at",
    )

    class Meta:
        verbose_name = "booking"
        verbose_name_plural = "bookings"

    def validar_reserva(self, comprobar_inicio=True):
        errors = {}
        if self.fecha_inicio and comprobar_inicio:
            original = type(self).objects.filter(pk=self.pk).first() if self.pk else None
            changed = original is None or original.fecha_inicio != self.fecha_inicio
            if changed and self.fecha_inicio < timezone.localdate():
                errors["fecha_inicio"] = "The start date cannot be earlier than today."
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            errors["fecha_fin"] = "The end date cannot be earlier than the start date."
        active = [self.ESTADO_PENDIENTE, self.ESTADO_CONFIRMADA]
        if self.cliente_id and self.fecha_inicio and self.fecha_fin and self.estado in active:
            overlaps = type(self).objects.filter(
                cliente_id=self.cliente_id, estado__in=active,
                fecha_inicio__lte=self.fecha_fin, fecha_fin__gte=self.fecha_inicio,
            ).exclude(pk=self.pk).exists()
            if overlaps:
                errors["__all__"] = "The customer already has an active booking that overlaps these dates."
        if errors:
            raise ValidationError(errors)

    def clean(self):
        super().clean()
        self.validar_reserva()

    def __str__(self):
        return f"{self.cliente} ({self.fecha_inicio} - {self.fecha_fin})"
