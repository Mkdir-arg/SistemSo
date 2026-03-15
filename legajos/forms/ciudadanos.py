from django import forms
from django.contrib.auth.models import User

from ..models import Ciudadano, Consentimiento, LegajoAtencion


class ConsultaRenaperForm(forms.Form):
    """Formulario para consultar datos en RENAPER"""

    GENERO_CHOICES = [
        ('', 'Seleccionar...'),
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('X', 'No binario'),
    ]

    dni = forms.CharField(
        max_length=8,
        label='DNI',
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'placeholder': 'Ingrese el DNI (ej: 12345678)',
            }
        ),
    )

    sexo = forms.ChoiceField(
        choices=GENERO_CHOICES,
        label='Sexo',
        widget=forms.Select(
            attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }
        ),
    )

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if dni:
            dni_limpio = ''.join(filter(str.isdigit, dni))
            if len(dni_limpio) < 7 or len(dni_limpio) > 8:
                raise forms.ValidationError('El DNI debe tener entre 7 y 8 dígitos.')
            return dni_limpio
        return dni


class CiudadanoForm(forms.ModelForm):
    """Formulario para crear/editar ciudadanos con datos de RENAPER"""

    class Meta:
        model = Ciudadano
        fields = [
            'dni',
            'nombre',
            'apellido',
            'fecha_nacimiento',
            'genero',
            'telefono',
            'email',
            'domicilio',
            'provincia',
            'municipio',
            'localidad',
        ]
        widgets = {
            'dni': forms.TextInput(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'readonly': True,
                }
            ),
            'nombre': forms.TextInput(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'apellido': forms.TextInput(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'fecha_nacimiento': forms.DateInput(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'type': 'date',
                }
            ),
            'genero': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'telefono': forms.TextInput(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'domicilio': forms.TextInput(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'provincia': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'municipio': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'localidad': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
        }


class CiudadanoManualForm(CiudadanoForm):
    class Meta(CiudadanoForm.Meta):
        widgets = {
            **CiudadanoForm.Meta.widgets,
            'dni': forms.TextInput(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'placeholder': 'Ingrese el DNI',
                }
            ),
        }


class CiudadanoConfirmarForm(CiudadanoForm):
    pass


class CiudadanoUpdateForm(CiudadanoForm):
    pass


class BuscarCiudadanoForm(forms.Form):
    """Paso 1: Buscar ciudadano para el legajo"""

    dni = forms.CharField(
        max_length=20,
        label='DNI del Ciudadano',
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'placeholder': 'Ingrese el DNI',
            }
        ),
    )


class AdmisionLegajoForm(forms.ModelForm):
    """Paso 2: Datos de admisión del legajo"""

    class Meta:
        model = LegajoAtencion
        fields = ['responsable', 'via_ingreso', 'nivel_riesgo', 'notas']
        widgets = {
            'dispositivo': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'responsable': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'via_ingreso': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'nivel_riesgo': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'notas': forms.Textarea(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'rows': 4,
                    'placeholder': 'Observaciones iniciales (opcional)',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['responsable'].queryset = User.objects.filter(is_active=True).order_by('username')
        self.fields['responsable'].empty_label = "Seleccionar responsable (opcional)"
        self.fields['responsable'].required = False

        if self.instance and self.instance.pk and self.instance.responsable_id:
            if not User.objects.filter(id=self.instance.responsable_id).exists():
                self.instance.responsable = None

    def clean_responsable(self):
        """Validar que el responsable existe en la base de datos"""
        responsable = self.cleaned_data.get('responsable')
        if responsable and not User.objects.filter(id=responsable.id, is_active=True).exists():
            raise forms.ValidationError('El usuario seleccionado no existe o no está activo.')
        return responsable


class ConsentimientoForm(forms.ModelForm):
    """Formulario para consentimientos"""

    class Meta:
        model = Consentimiento
        fields = ['texto', 'firmado_por', 'fecha_firma', 'archivo']
        widgets = {
            'texto': forms.Textarea(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'rows': 6,
                    'placeholder': 'Texto del consentimiento informado',
                }
            ),
            'firmado_por': forms.TextInput(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'placeholder': 'Nombre completo de quien firma',
                }
            ),
            'fecha_firma': forms.DateInput(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'type': 'date',
                }
            ),
            'archivo': forms.FileInput(
                attrs={
                    'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100',
                }
            ),
        }
