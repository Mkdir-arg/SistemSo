"""
Validación del JSON de definición de flujo.
"""
from datetime import date
from decimal import Decimal

from django import forms
from django.contrib.auth import get_user_model

from flujos.application.dto import normalize_flow_definition
from flujos.infrastructure.selectors import get_assignable_users_queryset


DISPLAY_UI_FIELD_KINDS = {'info', 'summary', 'table'}
INFO_ALERT_CLASS_BY_TONE = {
    'info': 'info',
    'success': 'success',
    'warning': 'warning',
    'danger': 'danger',
    'neutral': 'secondary',
}


class DefinicionFlujoForm(forms.Form):
    def __init__(self, *args, validation_mode="draft", programa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.validation_mode = validation_mode
        self.programa = programa

    definicion = forms.JSONField(
        label='Definición',
        help_text='JSON con nodos y transiciones del flujo',
    )

    def clean_definicion(self):
        data = self.cleaned_data['definicion']
        try:
            return normalize_flow_definition(
                data,
                validation_mode=self.validation_mode,
                programa_id=self.programa.pk if self.programa is not None else None,
            )
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc


class TareaResolverForm(forms.Form):
    form_kind = 'json'

    datos = forms.JSONField(
        required=False,
        label='Datos de resolución',
        help_text='JSON con los datos que el runtime usará para evaluar la salida de este paso.',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control font-monospace',
                'rows': 10,
                'placeholder': '{\n  "campo": "valor"\n}',
            }
        ),
    )

    def clean_datos(self):
        return self.cleaned_data.get('datos') or {}

    def to_runtime_data(self):
        return self.cleaned_data['datos']


class TareaDecisionBinariaForm(forms.Form):
    form_kind = 'boolean_decision'

    decision = forms.ChoiceField(
        choices=[],
        widget=forms.RadioSelect,
        label='Decision',
    )
    observacion = forms.CharField(
        required=False,
        label='Observacion',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observacion opcional...',
            }
        ),
    )

    def __init__(self, *args, schema=None, **kwargs):
        self.schema = schema or {}
        super().__init__(*args, **kwargs)
        self.fields['decision'].label = self.schema.get('field_label', 'Decision')
        self.fields['decision'].choices = [
            ('true', self.schema.get('true_label', 'Si')),
            ('false', self.schema.get('false_label', 'No')),
        ]
        self.fields['observacion'].label = self.schema.get(
            'observacion_label',
            'Observacion',
        )
        self.fields['observacion'].required = self.schema.get(
            'observacion_required',
            False,
        )
        if not self.schema.get('include_observacion', True):
            self.fields.pop('observacion')

    def to_runtime_data(self):
        data = {
            self.schema['field_name']: self.cleaned_data['decision'] == 'true',
        }
        observacion = self.cleaned_data.get('observacion', '').strip()
        if observacion:
            data['observacion'] = observacion
        return data


class TareaTextoTipadoForm(forms.Form):
    form_kind = 'text_input'

    value = forms.CharField(required=False)

    def __init__(self, *args, schema=None, **kwargs):
        self.schema = schema or {}
        super().__init__(*args, **kwargs)
        widget_attrs = {
            'class': 'form-control',
        }
        placeholder = self.schema.get('placeholder')
        if placeholder:
            widget_attrs['placeholder'] = placeholder

        multiline = self.schema.get('multiline', False)
        if multiline:
            widget_attrs['rows'] = self.schema.get('rows', 4)
            widget = forms.Textarea(attrs=widget_attrs)
        else:
            widget = forms.TextInput(attrs=widget_attrs)

        self.fields['value'] = forms.CharField(
            required=self.schema.get('required', True),
            label=self.schema.get('field_label', 'Valor'),
            help_text=self.schema.get('help_text', ''),
            widget=widget,
        )

    def to_runtime_data(self):
        value = self.cleaned_data['value']
        if isinstance(value, str):
            value = value.strip()
        return {
            self.schema['field_name']: value,
        }


class TareaSeleccionTipadaForm(forms.Form):
    form_kind = 'choice_select'

    value = forms.ChoiceField(required=False)

    def __init__(self, *args, schema=None, **kwargs):
        self.schema = schema or {}
        super().__init__(*args, **kwargs)
        choices = [
            (opcion['value'], opcion['label'])
            for opcion in self.schema.get('options', [])
        ]
        placeholder = self.schema.get('placeholder') or 'Seleccionar una opcion'
        choices = [('', placeholder)] + choices
        self.fields['value'] = forms.ChoiceField(
            required=self.schema.get('required', True),
            label=self.schema.get('field_label', 'Seleccion'),
            help_text=self.schema.get('help_text', ''),
            choices=choices,
            widget=forms.Select(attrs={'class': 'form-select'}),
        )

    def to_runtime_data(self):
        return {
            self.schema['field_name']: self.cleaned_data['value'],
        }


class TareaFormularioDeclarativoForm(forms.Form):
    form_kind = 'ui_form'

    def __init__(self, *args, schema=None, initial=None, **kwargs):
        self.schema = schema or {}
        initial = initial or {}
        super().__init__(*args, initial=initial, **kwargs)
        self.sections = []

        for section in self.schema.get('sections', []):
            items = []
            bound_fields = []
            for field_schema in section.get('fields', []):
                if field_schema.get('kind') in DISPLAY_UI_FIELD_KINDS:
                    items.append(self._build_display_item(field_schema))
                    continue
                field_name = field_schema['id']
                self.fields[field_name] = self._build_declared_field(field_schema)
                bound_field = self[field_name]
                bound_fields.append(bound_field)
                items.append(
                    {
                        'type': 'field',
                        'bound_field': bound_field,
                        'schema': field_schema,
                    }
                )
            self.sections.append(
                {
                    'id': section['id'],
                    'title': section.get('title', ''),
                    'description': section.get('description', ''),
                    'items': items,
                    'bound_fields': bound_fields,
                }
            )

    def _build_display_item(self, field_schema):
        if field_schema['kind'] == 'info':
            return {
                'type': 'display',
                'display_kind': 'info',
                'schema': field_schema,
                'alert_class': INFO_ALERT_CLASS_BY_TONE.get(field_schema.get('tone', 'info'), 'info'),
            }

        if field_schema['kind'] == 'summary':
            items = [
                {
                    'label': item.get('label', ''),
                    'value': item.get('value', ''),
                }
                for item in field_schema.get('items', [])
            ]
            return {
                'type': 'display',
                'display_kind': 'summary',
                'schema': field_schema,
                'items': items,
                'empty_message': field_schema.get('empty_message', 'Sin indicadores para mostrar.'),
            }

        if field_schema['kind'] == 'table':
            columns = field_schema.get('columns', [])
            rows = [
                {
                    'cells': [
                        {
                            'key': column['key'],
                            'label': column['label'],
                            'value': row.get(column['key'], ''),
                        }
                        for column in columns
                    ]
                }
                for row in field_schema.get('rows', [])
            ]
            return {
                'type': 'display',
                'display_kind': 'table',
                'schema': field_schema,
                'columns': columns,
                'rows': rows,
                'empty_message': field_schema.get('empty_message', 'Sin registros para mostrar.'),
            }

        raise ValueError(f'Tipo de bloque declarativo no soportado: {field_schema["kind"]}')

    def _build_declared_field(self, field_schema):
        kind = field_schema['kind']
        required = field_schema.get('required', False)
        label = field_schema['label']
        help_text = field_schema.get('help_text', '')

        widget_attrs = {'class': 'form-control'}
        placeholder = field_schema.get('placeholder')
        if placeholder:
            widget_attrs['placeholder'] = placeholder

        if kind == 'textarea':
            widget_attrs['rows'] = field_schema.get('rows', 4)
            return forms.CharField(
                required=required,
                label=label,
                help_text=help_text,
                widget=forms.Textarea(attrs=widget_attrs),
            )

        if kind == 'number':
            widget_attrs['step'] = 'any'
            return forms.DecimalField(
                required=required,
                label=label,
                help_text=help_text,
                widget=forms.NumberInput(attrs=widget_attrs),
            )

        if kind == 'date':
            widget_attrs['type'] = 'date'
            return forms.DateField(
                required=required,
                label=label,
                help_text=help_text,
                widget=forms.DateInput(attrs=widget_attrs),
            )

        if kind == 'radio':
            choices = [
                (option['value'], option['label'])
                for option in field_schema.get('options', [])
            ]
            return forms.ChoiceField(
                required=required,
                label=label,
                help_text=help_text,
                choices=choices,
                widget=forms.RadioSelect,
            )

        if kind == 'select':
            choices = [
                (option['value'], option['label'])
                for option in field_schema.get('options', [])
            ]
            if not required:
                choices = [('', placeholder or 'Seleccionar una opcion')] + choices
            return forms.ChoiceField(
                required=required,
                label=label,
                help_text=help_text,
                choices=choices,
                widget=forms.Select(attrs={'class': 'form-select'}),
            )

        if kind == 'checkbox':
            return forms.BooleanField(
                required=required,
                label=label,
                help_text=help_text,
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            )

        return forms.CharField(
            required=required,
            label=label,
            help_text=help_text,
            widget=forms.TextInput(attrs=widget_attrs),
        )

    def to_runtime_data(self):
        payload = {}
        for key, value in self.cleaned_data.items():
            if isinstance(value, str):
                payload[key] = value.strip()
            elif isinstance(value, Decimal):
                payload[key] = int(value) if value == value.to_integral_value() else float(value)
            elif isinstance(value, date):
                payload[key] = value.isoformat()
            else:
                payload[key] = value
        return payload


def build_tarea_resolution_form(*, tarea, data=None, initial_runtime_data=None):
    initial_runtime_data = initial_runtime_data or {}
    resolution_schema = getattr(tarea, 'resolution_schema', {'type': 'json'}) or {'type': 'json'}

    if data is not None and 'datos' in data:
        return TareaResolverForm(data, initial={'datos': initial_runtime_data})

    if resolution_schema.get('type') == 'boolean_decision':
        initial = {}
        decision_value = initial_runtime_data.get(resolution_schema['field_name'])
        if decision_value is True:
            initial['decision'] = 'true'
        elif decision_value is False:
            initial['decision'] = 'false'
        if 'observacion' in initial_runtime_data:
            initial['observacion'] = initial_runtime_data.get('observacion', '')
        return TareaDecisionBinariaForm(data=data, initial=initial, schema=resolution_schema)

    if resolution_schema.get('type') == 'text_input':
        initial = {
            'value': initial_runtime_data.get(resolution_schema['field_name'], ''),
        }
        return TareaTextoTipadoForm(data=data, initial=initial, schema=resolution_schema)

    if resolution_schema.get('type') == 'choice_select':
        initial = {
            'value': initial_runtime_data.get(resolution_schema['field_name'], ''),
        }
        return TareaSeleccionTipadaForm(data=data, initial=initial, schema=resolution_schema)

    if resolution_schema.get('type') == 'ui_form':
        return TareaFormularioDeclarativoForm(
            data=data,
            initial=initial_runtime_data,
            schema=resolution_schema,
        )

    return TareaResolverForm(data, initial={'datos': initial_runtime_data})


class RolProgramaForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border border-gray-300 py-2 px-3 text-sm',
            'placeholder': 'Ej: Evaluador',
        }),
    )
    descripcion = forms.CharField(
        required=False,
        label='Descripción',
        widget=forms.Textarea(attrs={
            'class': 'block w-full rounded-md border border-gray-300 py-2 px-3 text-sm',
            'rows': 2,
        }),
    )

    def __init__(self, *args, programa=None, **kwargs):
        self.programa = programa
        super().__init__(*args, **kwargs)

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if not nombre:
            raise forms.ValidationError('El nombre no puede estar vacío.')
        from flujos.models import RolPrograma
        if self.programa is not None and RolPrograma.objects.filter(
            programa=self.programa, nombre__iexact=nombre,
        ).exists():
            raise forms.ValidationError('Ya existe un rol con ese nombre en este programa.')
        return nombre


class AsignacionRolProgramaForm(forms.Form):
    usuario = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        label='Usuario',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['usuario'].queryset = get_assignable_users_queryset()


class TareaAsignacionForm(forms.Form):
    asignado_a = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        required=False,
        label='Asignado a',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['asignado_a'].queryset = get_assignable_users_queryset()
