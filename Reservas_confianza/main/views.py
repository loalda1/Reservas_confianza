from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import RegistroForm, ReservaForm
from .models import Cliente, Reserva


def es_cliente(user):
    return user.is_authenticated and user.groups.filter(
        Q(name__iexact="customer") | Q(name__iexact="customers")
        | Q(name__iexact="cliente") | Q(name__iexact="clientes")
    ).exists()


def obtener_cliente_del_usuario(user):
    try:
        return user.perfil_cliente
    except Cliente.DoesNotExist:
        raise PermissionDenied("No customer profile is linked to this account.")


def reservas_accesibles(user):
    qs = Reserva.objects.select_related("cliente")
    if es_cliente(user):
        qs = qs.filter(cliente=obtener_cliente_del_usuario(user))
    return qs


def exigir_gestion(user):
    if es_cliente(user):
        raise PermissionDenied


def home(request):
    return render(request, "main/home.html")


@login_required
@permission_required("main.view_reserva", raise_exception=True)
def reservas_list(request):
    qs = reservas_accesibles(request.user).order_by("-fecha_inicio", "-fecha_fin", "-pk")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(cliente__nombre__icontains=q) | Q(cliente__email__icontains=q))
    request.session["last_search"] = q
    request.session["visits_reservas_list"] = request.session.get("visits_reservas_list", 0) + 1
    page = Paginator(qs, 5).get_page(request.GET.get("page"))
    return render(request, "reservas/reservas_list.html", {"reservas": page, "page_obj": page, "q": q})


def editar_formulario(request, instance=None, personal=False):
    cliente = obtener_cliente_del_usuario(request.user) if es_cliente(request.user) else None
    form = ReservaForm(request.POST if request.method == "POST" else None,
                       instance=instance, cliente_actual=cliente)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                # Serialize validation for the same customer on databases supporting row locks.
                Cliente.objects.select_for_update().get(pk=form.cleaned_data["cliente"].pk)
                reserva = form.save(commit=False)
                reserva.full_clean()
                reserva.save()
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Booking saved successfully.")
            return redirect("mis_reservas" if personal and cliente else "reservas_list")
    return render(request, "reservas/reserva_form.html", {
        "form": form, "titulo": "Edit booking" if instance else "Create booking",
        "boton": "Save changes" if instance else "Save booking",
    })


@login_required
@permission_required("main.add_reserva", raise_exception=True)
def reserva_create(request):
    return editar_formulario(request)


@login_required
@permission_required("main.add_reserva", raise_exception=True)
def crear_reserva(request):
    return editar_formulario(request, personal=True)


@login_required
@permission_required("main.change_reserva", raise_exception=True)
def reserva_update(request, pk):
    return editar_formulario(request, get_object_or_404(reservas_accesibles(request.user), pk=pk))


@login_required
@permission_required("main.view_reserva", raise_exception=True)
def reserva_detail(request, pk):
    return render(request, "reservas/reserva_detail.html", {
        "reserva": get_object_or_404(reservas_accesibles(request.user), pk=pk),
    })


@login_required
@permission_required("main.delete_reserva", raise_exception=True)
def reserva_delete(request, pk):
    reserva = get_object_or_404(reservas_accesibles(request.user), pk=pk)
    if request.method == "POST":
        reserva.delete()
        messages.success(request, "Booking deleted successfully.")
        return redirect("reservas_list")
    return render(request, "reservas/reserva_confirm_delete.html", {"reserva": reserva})


@login_required
@permission_required("main.change_reserva", raise_exception=True)
def gestion_reservas(request):
    exigir_gestion(request.user)
    return render(request, "main/gestion_reservas.html", {
        "reservas": reservas_accesibles(request.user).order_by("-fecha_inicio", "-fecha_fin", "-pk"),
    })


@login_required
@permission_required("main.view_reserva", raise_exception=True)
def mis_reservas(request):
    cliente = obtener_cliente_del_usuario(request.user)
    return render(request, "main/mis_reservas.html", {
        "reservas": Reserva.objects.filter(cliente=cliente).order_by("-fecha_inicio", "-fecha_fin", "-pk"),
    })


def cambiar_estado(request, pk, estado):
    exigir_gestion(request.user)
    ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    with transaction.atomic():
        reserva = get_object_or_404(Reserva.objects.select_for_update(), pk=pk)
        Cliente.objects.select_for_update().get(pk=reserva.cliente_id)
        anterior = reserva.estado
        reserva.estado = estado
        try:
            # Status changes keep historical dates, but must obey overlap rules.
            reserva.validar_reserva(comprobar_inicio=False)
        except ValidationError as error:
            reserva.estado = anterior
            if ajax:
                return JsonResponse({"ok": False, "errors": error.messages}, status=400)
            messages.error(request, " ".join(error.messages))
        else:
            reserva.save(update_fields=["estado"])
            if ajax:
                return JsonResponse({"ok": True, "id": reserva.pk, "estado": reserva.estado,
                                     "estado_display": reserva.get_estado_display()})
            messages.success(request, "Booking status updated successfully.")
    return redirect("reservas_list")


@login_required
@permission_required("main.change_reserva", raise_exception=True)
@require_POST
def confirmar_reserva(request, pk):
    return cambiar_estado(request, pk, Reserva.ESTADO_CONFIRMADA)


@login_required
@permission_required("main.change_reserva", raise_exception=True)
@require_POST
def cancelar_reserva(request, pk):
    return cambiar_estado(request, pk, Reserva.ESTADO_CANCELADA)


@transaction.non_atomic_requests
def registro(request):
    if request.user.is_authenticated:
        return redirect("index")
    form = RegistroForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        from django.contrib.auth.models import Group, Permission
        try:
            with transaction.atomic():
                user = form.save(commit=False)
                user.email = form.cleaned_data["email"]
                user.is_staff = False
                user.is_superuser = False
                user.save()
                Cliente.objects.create(
                    usuario=user, nombre=form.cleaned_data["nombre"],
                    email=user.email, telefono=form.cleaned_data["telefono"],
                )
                group, _ = Group.objects.get_or_create(name="customers")
                user.groups.add(group)
                user.user_permissions.add(*Permission.objects.filter(
                    content_type__app_label="main", content_type__model="reserva",
                    codename__in=["view_reserva", "add_reserva"],
                ))
        except IntegrityError:
            form.add_error(None, "The username or email is already in use. Please try again.")
        else:
            messages.success(request, "Account created successfully. You can now log in.")
            return redirect("login")
    return render(request, "registration/register.html", {"form": form})
