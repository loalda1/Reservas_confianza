from datetime import date, timedelta
from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse
from .models import Cliente, Reserva


class ReservationAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        group = Group.objects.create(name="customers")
        cls.customer = User.objects.create_user("customer")
        cls.customer.groups.add(group)
        perms = Permission.objects.filter(content_type__app_label="main", content_type__model="reserva")
        cls.customer.user_permissions.set(perms)
        cls.employee = User.objects.create_user("employee")
        cls.employee.user_permissions.set(perms)
        cls.unlinked = User.objects.create_user("unlinked", email="other@example.com")
        cls.unlinked.groups.add(group)
        cls.unlinked.user_permissions.set(perms)
        cls.owner = Cliente.objects.create(usuario=cls.customer, nombre="Owner", email="owner@example.com")
        cls.other = Cliente.objects.create(nombre="Other", email="other@example.com")
        cls.start = date.today() + timedelta(days=10)
        cls.end = cls.start + timedelta(days=2)
        cls.own = Reserva.objects.create(cliente=cls.owner, fecha_inicio=cls.start, fecha_fin=cls.end)
        cls.foreign = Reserva.objects.create(cliente=cls.other, fecha_inicio=cls.start, fecha_fin=cls.end)

    def payload(self):
        return {"cliente": self.other.pk, "fecha_inicio": self.start + timedelta(days=20),
                "fecha_fin": self.end + timedelta(days=20)}

    def test_anonymous_cannot_read_booking_pages(self):
        for name, args in [("reservas_list", []), ("reserva_detail", [self.foreign.pk]),
                           ("mis_reservas", []), ("gestion_reservas", [])]:
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, 302)
                self.assertIn("/accounts/login/", response.url)

    def test_user_needs_view_permission(self):
        self.client.force_login(User.objects.create_user("no-permissions"))
        self.assertEqual(self.client.get(reverse("reservas_list")).status_code, 403)

    def test_customer_list_search_and_personal_page_are_scoped(self):
        self.client.force_login(self.customer)
        for name in ["reservas_list", "mis_reservas"]:
            response = self.client.get(reverse(name))
            self.assertEqual([r.pk for r in response.context["reservas"]], [self.own.pk])
        response = self.client.get(reverse("reservas_list"), {"q": self.other.email})
        self.assertEqual(list(response.context["reservas"]), [])

    def test_foreign_booking_cannot_be_read_edited_or_deleted(self):
        self.client.force_login(self.customer)
        for name in ["reserva_detail", "reserva_update", "reserva_delete"]:
            for method in ["get", "post"]:
                with self.subTest(name=name, method=method):
                    response = getattr(self.client, method)(reverse(name, args=[self.foreign.pk]), self.payload())
                    self.assertEqual(response.status_code, 404)
        self.foreign.refresh_from_db()
        self.assertEqual(self.foreign.cliente_id, self.other.pk)

    def test_generic_creation_ignores_forged_customer(self):
        self.client.force_login(self.customer)
        response = self.client.post(reverse("reserva_create"), self.payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Reserva.objects.latest("pk").cliente_id, self.owner.pk)

    def test_personal_creation_ignores_forged_customer(self):
        self.client.force_login(self.customer)
        response = self.client.post(reverse("crear_reserva"), self.payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Reserva.objects.latest("pk").cliente_id, self.owner.pk)

    def test_customer_cannot_transfer_own_booking(self):
        self.client.force_login(self.customer)
        response = self.client.post(reverse("reserva_update", args=[self.own.pk]), self.payload())
        self.assertEqual(response.status_code, 302)
        self.own.refresh_from_db()
        self.assertEqual(self.own.cliente_id, self.owner.pk)

    def test_customer_cannot_manage_or_change_status(self):
        self.client.force_login(self.customer)
        self.assertEqual(self.client.get(reverse("gestion_reservas")).status_code, 403)
        for name in ["confirmar_reserva", "cancelar_reserva"]:
            for booking in [self.own, self.foreign]:
                self.assertEqual(self.client.post(reverse(name, args=[booking.pk])).status_code, 403)
        self.own.refresh_from_db()
        self.assertEqual(self.own.estado, Reserva.ESTADO_PENDIENTE)

    def test_email_match_does_not_grant_access_without_link(self):
        self.client.force_login(self.unlinked)
        for name in ["reservas_list", "mis_reservas", "reserva_create", "crear_reserva"]:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 403)

    def test_employee_can_manage_all_bookings(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse("reservas_list"))
        self.assertEqual({r.pk for r in response.context["reservas"]}, {self.own.pk, self.foreign.pk})
        self.assertEqual(self.client.get(reverse("gestion_reservas")).status_code, 200)
        response = self.client.post(reverse("confirmar_reserva", args=[self.foreign.pk]), HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["estado"], Reserva.ESTADO_CONFIRMADA)
        self.assertEqual(self.client.post(reverse("reserva_update", args=[self.foreign.pk]), self.payload()).status_code, 302)
        self.assertEqual(self.client.post(reverse("reserva_delete", args=[self.foreign.pk])).status_code, 302)
        self.assertFalse(Reserva.objects.filter(pk=self.foreign.pk).exists())

    def test_invalid_dates_and_missing_customer_return_form_errors(self):
        self.client.force_login(self.employee)
        invalid = [
            {"cliente": self.owner.pk, "fecha_inicio": "bad", "fecha_fin": "bad"},
            {"cliente": self.owner.pk, "fecha_inicio": date.today() - timedelta(days=1), "fecha_fin": self.end},
            {"cliente": self.owner.pk, "fecha_inicio": self.end, "fecha_fin": self.start},
            {"cliente": 999999, "fecha_inicio": self.start, "fecha_fin": self.end},
            {"fecha_inicio": self.start, "fecha_fin": self.end},
        ]
        for route in ["reserva_create", "crear_reserva"]:
            for data in invalid:
                response = self.client.post(reverse(route), data)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
        self.assertEqual(Reserva.objects.count(), 2)

    def test_overlap_including_boundary_is_rejected_in_both_forms(self):
        self.client.force_login(self.customer)
        for name in ["reserva_create", "crear_reserva"]:
            response = self.client.post(reverse(name), {
                "fecha_inicio": self.end, "fecha_fin": self.end + timedelta(days=2),
            })
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].non_field_errors())

    def test_cancelled_booking_does_not_block_new_booking(self):
        self.own.estado = Reserva.ESTADO_CANCELADA
        self.own.save()
        self.client.force_login(self.customer)
        response = self.client.post(reverse("reserva_create"), {
            "fecha_inicio": self.start, "fecha_fin": self.end,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Reserva.objects.filter(cliente=self.owner).count(), 2)

    def test_completed_booking_does_not_block_new_booking(self):
        self.own.estado = Reserva.ESTADO_FINALIZADA
        self.own.save()
        self.client.force_login(self.customer)
        response = self.client.post(reverse("crear_reserva"), {
            "fecha_inicio": self.start, "fecha_fin": self.end,
        })
        self.assertEqual(response.status_code, 302)

    def test_reconfirming_cancelled_booking_revalidates_overlap(self):
        self.own.estado = Reserva.ESTADO_CANCELADA
        self.own.save()
        Reserva.objects.create(cliente=self.owner, fecha_inicio=self.start, fecha_fin=self.end)
        self.client.force_login(self.employee)
        response = self.client.post(reverse("confirmar_reserva", args=[self.own.pk]),
                                    HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 400)
        self.own.refresh_from_db()
        self.assertEqual(self.own.estado, Reserva.ESTADO_CANCELADA)

    def test_model_validation_covers_admin_modelform(self):
        from django.forms import modelform_factory
        AdminForm = modelform_factory(Reserva, fields=["cliente", "fecha_inicio", "fecha_fin", "estado"])
        form = AdminForm(data={"cliente": self.owner.pk, "fecha_inicio": self.start,
                              "fecha_fin": self.end, "estado": Reserva.ESTADO_PENDIENTE})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.non_field_errors())

    def test_historical_booking_can_be_confirmed_and_edited_unchanged(self):
        Reserva.objects.filter(pk=self.own.pk).update(fecha_inicio=date.today() - timedelta(days=5),
                                                     fecha_fin=date.today() - timedelta(days=2))
        self.own.refresh_from_db()
        self.client.force_login(self.employee)
        response = self.client.post(reverse("confirmar_reserva", args=[self.own.pk]))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse("reserva_update", args=[self.own.pk]), {
            "cliente": self.owner.pk, "fecha_inicio": self.own.fecha_inicio, "fecha_fin": self.own.fecha_fin,
        })
        self.assertEqual(response.status_code, 302)

    def test_status_get_is_not_allowed(self):
        self.client.force_login(self.employee)
        for name in ["confirmar_reserva", "cancelar_reserva"]:
            self.assertEqual(self.client.get(reverse(name, args=[self.own.pk])).status_code, 405)
        self.own.refresh_from_db()
        self.assertEqual(self.own.estado, Reserva.ESTADO_PENDIENTE)

    def test_status_post_requires_csrf_and_accepts_valid_token(self):
        from django.test import Client
        browser = Client(enforce_csrf_checks=True)
        browser.force_login(self.employee)
        url = reverse("cancelar_reserva", args=[self.own.pk])
        self.assertEqual(browser.post(url).status_code, 403)
        browser.get(reverse("reserva_detail", args=[self.own.pk]))
        token = browser.cookies["csrftoken"].value
        self.assertEqual(browser.post(url, {"csrfmiddlewaretoken": token}).status_code, 302)
        self.own.refresh_from_db()
        self.assertEqual(self.own.estado, Reserva.ESTADO_CANCELADA)

    def test_date_input_uses_iso_format_when_editing(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse("reserva_update", args=[self.own.pk]))
        self.assertContains(response, 'value="' + self.start.isoformat() + '"')

    def test_ajax_script_is_discoverable_and_detail_uses_post(self):
        from django.contrib.staticfiles import finders
        self.assertIsNotNone(finders.find("js/reservas.js"))
        self.client.force_login(self.employee)
        response = self.client.get(reverse("reserva_detail", args=[self.own.pk]))
        self.assertContains(response, 'method="post" action="' + reverse("confirmar_reserva", args=[self.own.pk]) + '"')

    def test_pagination_search_and_sessions(self):
        for offset in range(6):
            Reserva.objects.create(cliente=self.other, fecha_inicio=self.start + timedelta(days=offset * 5 + 30),
                                   fecha_fin=self.end + timedelta(days=offset * 5 + 30))
        self.client.force_login(self.employee)
        response = self.client.get(reverse("reservas_list"), {"q": "Other", "page": 1})
        self.assertEqual(len(response.context["reservas"]), 5)
        self.assertEqual(response.context["page_obj"].paginator.count, 7)
        self.assertEqual(self.client.session["last_search"], "Other")
        self.assertEqual(self.client.session["visits_reservas_list"], 1)
        self.assertEqual(self.client.get(reverse("reservas_list"), {"page": "bad"}).status_code, 200)

    def test_customer_does_not_see_management_buttons(self):
        self.client.force_login(self.customer)
        for name, args in [("index", []), ("reserva_detail", [self.own.pk]), ("reservas_list", [])]:
            response = self.client.get(reverse(name, args=args))
            self.assertNotContains(response, reverse("gestion_reservas"))
            self.assertNotContains(response, reverse("confirmar_reserva", args=[self.own.pk]))


class RegistrationTests(TestCase):
    def data(self, **changes):
        data = {"username": "newcustomer", "nombre": "New Customer", "email": "NEW@example.com",
                "telefono": "123456", "password1": "A-long-private-pass-947!",
                "password2": "A-long-private-pass-947!"}
        data.update(changes)
        return data

    def test_register_login_and_create_own_booking(self):
        self.assertEqual(self.client.get(reverse("register")).status_code, 200)
        response = self.client.post(reverse("register"), self.data(is_staff="true", is_superuser="true"))
        self.assertRedirects(response, reverse("login"))
        user = User.objects.get(username="newcustomer")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(self.data()["password1"]))
        self.assertEqual(user.perfil_cliente.email, "new@example.com")
        self.assertTrue(user.groups.filter(name="customers").exists())
        self.assertTrue(user.has_perm("main.view_reserva"))
        self.assertTrue(user.has_perm("main.add_reserva"))
        self.assertFalse(user.has_perm("main.change_reserva"))
        response = self.client.post(reverse("login"), {"username": user.username, "password": self.data()["password1"]})
        self.assertEqual(response.status_code, 302)
        start = date.today() + timedelta(days=5)
        response = self.client.post(reverse("crear_reserva"), {"fecha_inicio": start, "fecha_fin": start})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Reserva.objects.get().cliente_id, user.perfil_cliente.pk)
        self.assertEqual(self.client.get(reverse("mis_reservas")).status_code, 200)
        self.assertEqual(self.client.get(reverse("gestion_reservas")).status_code, 403)

    def test_duplicate_username_and_case_insensitive_email(self):
        self.client.post(reverse("register"), self.data())
        for changes in [{"username": "another"}, {"email": "different@example.com"}]:
            response = self.client.post(reverse("register"), self.data(**changes))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Cliente.objects.count(), 1)

    def test_existing_unlinked_customer_email_cannot_be_claimed(self):
        Cliente.objects.create(nombre="Existing", email="new@example.com")
        response = self.client.post(reverse("register"), self.data())
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(User.objects.exists())

    def test_invalid_password_and_fields_do_not_create_accounts(self):
        for changes in [{"password2": "different"}, {"password1": "123", "password2": "123"},
                        {"nombre": ""}, {"email": "bad"}]:
            response = self.client.post(reverse("register"), self.data(**changes))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
        self.assertFalse(User.objects.exists())
        self.assertFalse(Cliente.objects.exists())

    def test_authenticated_user_is_redirected(self):
        self.client.force_login(User.objects.create_user("existing"))
        self.assertRedirects(self.client.get(reverse("register")), reverse("index"))
        self.assertRedirects(self.client.post(reverse("register"), self.data()), reverse("index"))
        self.assertEqual(User.objects.count(), 1)

    def test_registration_requires_csrf(self):
        from django.test import Client
        browser = Client(enforce_csrf_checks=True)
        self.assertEqual(browser.post(reverse("register"), self.data()).status_code, 403)
        browser.get(reverse("register"))
        data = self.data(csrfmiddlewaretoken=browser.cookies["csrftoken"].value)
        self.assertEqual(browser.post(reverse("register"), data).status_code, 302)

    def test_failure_rolls_back_user_creation(self):
        from unittest.mock import patch
        from django.db import IntegrityError
        with patch("main.views.Cliente.objects.create", side_effect=IntegrityError):
            response = self.client.post(reverse("register"), self.data())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertFalse(User.objects.exists())
