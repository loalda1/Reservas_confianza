from django import forms
from .models import Cliente, Reserva
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class ReservaForm(forms.ModelForm):
    """
    ModelForm = automatic form based on the Reserva model.
    Django generates fields and basic validation (DateField, FK, etc.).
    """

    def __init__(self, *args, cliente_actual=None, **kwargs):
        super().__init__(*args, **kwargs)
        if cliente_actual is not None:
            self.fields["cliente"].queryset = type(cliente_actual).objects.filter(pk=cliente_actual.pk)
            self.fields["cliente"].initial = cliente_actual.pk
            self.initial["cliente"] = cliente_actual.pk
            self.fields["cliente"].disabled = True

    class Meta:
        model = Reserva

        # Fields to display in the form
        fields = ["cliente", "fecha_inicio", "fecha_fin"]

        labels = {
            "cliente": "Customer",
            "fecha_inicio": "Start date",
            "fecha_fin": "End date",
        }

        # Widgets control how each input is rendered in HTML.
        # type="date" displays the browser's date picker.
        widgets = {
            "fecha_inicio": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        }


class RegistroForm(UserCreationForm):
    nombre = forms.CharField(label="Full name", max_length=100)
    email = forms.EmailField(label="Email address")
    telefono = forms.CharField(label="Phone number", max_length=20, required=False)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "nombre", "email", "telefono", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if (Cliente.objects.filter(email__iexact=email).exists()
                or get_user_model().objects.filter(email__iexact=email).exists()):
            raise forms.ValidationError("This email address is already in use.")
        return email
