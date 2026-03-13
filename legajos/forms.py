from django import forms
from django.contrib.auth.models import User
from django.db import models
from .models import Ciudadano, LegajoAtencion, Consentimiento, EvaluacionInicial, Objetivo, PlanIntervencion, SeguimientoContacto, Derivacion, EventoCritico, InscriptoActividad, PlanFortalecimiento
from core.models import DispositivoRed


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
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'Ingrese el DNI (ej: 12345678)'
        })
    )
    
    sexo = forms.ChoiceField(
        choices=GENERO_CHOICES,
        label='Sexo',
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
        })
    )
    
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if dni:
            # Limpiar el DNI de caracteres no numéricos
            dni_limpio = ''.join(filter(str.isdigit, dni))
            
            # Validar que tenga 7 u 8 dígitos
            if len(dni_limpio) < 7 or len(dni_limpio) > 8:
                raise forms.ValidationError('El DNI debe tener entre 7 y 8 dígitos.')
            
            return dni_limpio
        
        return dni


class CiudadanoForm(forms.ModelForm):
    """Formulario para crear/editar ciudadanos con datos de RENAPER"""
    
    class Meta:
        model = Ciudadano
        fields = ['dni', 'nombre', 'apellido', 'fecha_nacimiento', 'genero', 'telefono', 'email', 'domicilio', 'provincia', 'municipio', 'localidad']
        widgets = {
            'dni': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'readonly': True
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'type': 'date'
            }),
            'genero': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'domicilio': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'provincia': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'municipio': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'localidad': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
        }


class BuscarCiudadanoForm(forms.Form):
    """Paso 1: Buscar ciudadano para el legajo"""
    
    dni = forms.CharField(
        max_length=20,
        label='DNI del Ciudadano',
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'Ingrese el DNI'
        })
    )


class AdmisionLegajoForm(forms.ModelForm):
    """Paso 2: Datos de admisión del legajo"""
    
    class Meta:
        model = LegajoAtencion
        fields = ['responsable', 'via_ingreso', 'nivel_riesgo', 'notas']
        widgets = {
            'dispositivo': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'responsable': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'via_ingreso': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'nivel_riesgo': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 4,
                'placeholder': 'Observaciones iniciales (opcional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Mostrar solo usuarios activos que existen en la base de datos
        self.fields['responsable'].queryset = User.objects.filter(is_active=True).order_by('username')
        self.fields['responsable'].empty_label = "Seleccionar responsable (opcional)"
        self.fields['responsable'].required = False
        
        # Limpiar el valor inicial si el usuario no existe
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
            'texto': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 6,
                'placeholder': 'Texto del consentimiento informado'
            }),
            'firmado_por': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'placeholder': 'Nombre completo de quien firma'
            }),
            'fecha_firma': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'type': 'date'
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            }),
        }


class EvaluacionInicialForm(forms.ModelForm):
    """Formulario para evaluación inicial"""
    
    # Campos adicionales para tamizajes comunes
    assist_puntaje = forms.IntegerField(
        required=False,
        label='ASSIST - Puntaje Total',
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'min': '0',
            'max': '100'
        })
    )
    
    phq9_puntaje = forms.IntegerField(
        required=False,
        label='PHQ-9 - Puntaje Total',
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'min': '0',
            'max': '27'
        })
    )
    
    class Meta:
        model = EvaluacionInicial
        fields = [
            'situacion_consumo', 'antecedentes', 'red_apoyo', 'condicion_social',
            'riesgo_suicida', 'violencia'
        ]
        widgets = {
            'situacion_consumo': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 4,
                'placeholder': 'Describe la situación actual de consumo...'
            }),
            'antecedentes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 4,
                'placeholder': 'Antecedentes médicos, psiquiátricos y de consumo...'
            }),
            'red_apoyo': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 3,
                'placeholder': 'Describe la red de apoyo familiar y social...'
            }),
            'condicion_social': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 3,
                'placeholder': 'Situación socioeconómica, vivienda, trabajo, educación...'
            }),
            'riesgo_suicida': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-red-600 shadow-sm focus:border-red-500 focus:ring-red-500'
            }),
            'violencia': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-red-600 shadow-sm focus:border-red-500 focus:ring-red-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cargar datos de tamizajes si existen
        if self.instance and self.instance.tamizajes:
            tamizajes = self.instance.tamizajes
            if 'ASSIST' in tamizajes:
                self.fields['assist_puntaje'].initial = tamizajes['ASSIST'].get('puntaje')
            if 'PHQ9' in tamizajes:
                self.fields['phq9_puntaje'].initial = tamizajes['PHQ9'].get('puntaje')
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Construir JSON de tamizajes
        tamizajes = {}
        
        assist_puntaje = self.cleaned_data.get('assist_puntaje')
        if assist_puntaje is not None:
            tamizajes['ASSIST'] = {
                'puntaje': assist_puntaje,
                'fecha': self.cleaned_data.get('fecha_assist') or str(instance.modificado.date() if instance.pk else instance.creado.date())
            }
        
        phq9_puntaje = self.cleaned_data.get('phq9_puntaje')
        if phq9_puntaje is not None:
            tamizajes['PHQ9'] = {
                'puntaje': phq9_puntaje,
                'fecha': self.cleaned_data.get('fecha_phq9') or str(instance.modificado.date() if instance.pk else instance.creado.date())
            }
        
        instance.tamizajes = tamizajes if tamizajes else None
        
        if commit:
            instance.save()
        return instance


class PlanIntervencionForm(forms.ModelForm):
    """Formulario para plan de intervención"""
    
    actividad_1 = forms.CharField(max_length=100, required=False, label="Actividad 1")
    frecuencia_1 = forms.CharField(max_length=50, required=False, label="Frecuencia 1")
    responsable_1 = forms.CharField(max_length=50, required=False, label="Responsable 1")
    
    actividad_2 = forms.CharField(max_length=100, required=False, label="Actividad 2")
    frecuencia_2 = forms.CharField(max_length=50, required=False, label="Frecuencia 2")
    responsable_2 = forms.CharField(max_length=50, required=False, label="Responsable 2")
    
    actividad_3 = forms.CharField(max_length=100, required=False, label="Actividad 3")
    frecuencia_3 = forms.CharField(max_length=50, required=False, label="Frecuencia 3")
    responsable_3 = forms.CharField(max_length=50, required=False, label="Responsable 3")
    
    class Meta:
        model = PlanIntervencion
        fields = ['vigente']
        widgets = {
            'vigente': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.actividades:
            for i, actividad in enumerate(self.instance.actividades[:3], 1):
                self.fields[f'actividad_{i}'].initial = actividad.get('accion')
                self.fields[f'frecuencia_{i}'].initial = actividad.get('freq')
                self.fields[f'responsable_{i}'].initial = actividad.get('responsable')
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # No procesar actividades aquí, se hace en la vista
        
        if commit:
            instance.save()
        return instance


class SeguimientoForm(forms.ModelForm):
    """Formulario para seguimientos"""
    
    class Meta:
        model = SeguimientoContacto
        fields = ['tipo', 'descripcion', 'adherencia', 'adjuntos']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 4,
                'placeholder': 'Describe el contacto o actividad realizada...'
            }),
            'adherencia': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'adjuntos': forms.FileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            }),
        }


class DerivacionForm(forms.ModelForm):
    """Formulario para derivaciones"""
    
    class Meta:
        model = Derivacion
        fields = ['destino', 'actividad_destino', 'motivo', 'urgencia']
        widgets = {
            'destino': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'actividad_destino': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 4,
                'placeholder': 'Describe el motivo de la derivación...'
            }),
            'urgencia': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        legajo = kwargs.pop('legajo', None)
        super().__init__(*args, **kwargs)
        
        self.fields['destino'].queryset = self.fields['destino'].queryset.filter(activo=True)
        self.fields['actividad_destino'].required = False
        
        from .models import PlanFortalecimiento
        # Si hay una instancia con destino, cargar sus actividades
        if self.instance and self.instance.pk and self.instance.destino:
            self.fields['actividad_destino'].queryset = PlanFortalecimiento.objects.filter(
                legajo_institucional__institucion=self.instance.destino,
                estado='ACTIVO'
            )
        # Si hay datos POST con destino, cargar actividades de ese destino
        elif self.data.get('destino'):
            try:
                destino_id = int(self.data.get('destino'))
                self.fields['actividad_destino'].queryset = PlanFortalecimiento.objects.filter(
                    legajo_institucional__institucion_id=destino_id,
                    estado='ACTIVO'
                )
            except (ValueError, TypeError):
                self.fields['actividad_destino'].queryset = PlanFortalecimiento.objects.none()
        else:
            self.fields['actividad_destino'].queryset = PlanFortalecimiento.objects.none()


class EventoCriticoForm(forms.ModelForm):
    """Formulario para eventos críticos"""
    
    # Campos para notificaciones
    notificar_familia = forms.BooleanField(required=False, label="Notificar a familia")
    notificar_autoridades = forms.BooleanField(required=False, label="Notificar a autoridades")
    notificar_otros = forms.CharField(max_length=200, required=False, label="Otros notificados")
    
    class Meta:
        model = EventoCritico
        fields = ['tipo', 'detalle']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'detalle': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 4,
                'placeholder': 'Describe el evento crítico...'
            }),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Construir JSON de notificaciones
        notificaciones = []
        if self.cleaned_data.get('notificar_familia'):
            notificaciones.append('Familia')
        if self.cleaned_data.get('notificar_autoridades'):
            notificaciones.append('Autoridades')
        if self.cleaned_data.get('notificar_otros'):
            notificaciones.append(self.cleaned_data['notificar_otros'])
        
        instance.notificado_a = notificaciones if notificaciones else None
        
        if commit:
            instance.save()
        return instance


class LegajoCerrarForm(forms.Form):
    """Formulario para cerrar legajo"""
    motivo_cierre = forms.CharField(
        max_length=500,
        required=False,
        label='Motivo de cierre',
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 3,
            'placeholder': 'Motivo del cierre (opcional)'
        })
    )


class InscribirActividadForm(forms.ModelForm):
    """Formulario para inscribir ciudadano a actividad del centro"""
    
    class Meta:
        model = InscriptoActividad
        fields = ['actividad', 'observaciones']
        widgets = {
            'actividad': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 3,
                'placeholder': 'Observaciones sobre la inscripción (opcional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        legajo = kwargs.pop('legajo', None)
        super().__init__(*args, **kwargs)
        
        if legajo:
            # Filtrar actividades del dispositivo del legajo que estén activas
            self.fields['actividad'].queryset = PlanFortalecimiento.objects.filter(
                legajo_institucional__institucion=legajo.dispositivo,
                estado='ACTIVO'
            ).select_related('legajo_institucional__institucion')
            self.fields['actividad'].label_from_instance = lambda obj: f"{obj.nombre} ({obj.get_tipo_display()})"
        else:
            self.fields['actividad'].queryset = PlanFortalecimiento.objects.none()