from datetime import datetime, timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from portal.models import RecursoTurnos
from reclamos.models import Area
from tramites.models import TipoTramite
from turnos.models import ConfiguracionTurnos, DisponibilidadConfiguracion, SedeTurno


class ConfiguracionTurnosForm(forms.ModelForm):
    sede = forms.ModelChoiceField(
        queryset=SedeTurno.objects.none(),
        required=False,
        label="Sede",
    )
    area_principal = forms.ModelChoiceField(
        queryset=Area.objects.none(),
        required=False,
        label="Area",
    )
    subarea = forms.ModelChoiceField(
        queryset=Area.objects.none(),
        required=False,
        label="Subarea",
    )
    tipo_tramite = forms.ModelChoiceField(
        queryset=TipoTramite.objects.none(),
        required=False,
        label="Tramite",
    )

    class Meta:
        model = ConfiguracionTurnos
        fields = [
            "sede",
            "area_principal",
            "subarea",
            "tipo_tramite",
            "nombre",
            "activo",
            "requiere_aprobacion",
            "modo_turno",
            "anticipacion_minima_hs",
            "anticipacion_maxima_dias",
            "permite_cancelacion_ciudadano",
            "cancelacion_hasta_hs",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-input w-full rounded-lg border-gray-300"}),
            "modo_turno": forms.Select(attrs={"class": "form-select w-full rounded-lg border-gray-300"}),
            "anticipacion_minima_hs": forms.NumberInput(
                attrs={"class": "form-input w-full rounded-lg border-gray-300", "min": 0}
            ),
            "anticipacion_maxima_dias": forms.NumberInput(
                attrs={"class": "form-input w-full rounded-lg border-gray-300", "min": 1}
            ),
            "cancelacion_hasta_hs": forms.NumberInput(
                attrs={"class": "form-input w-full rounded-lg border-gray-300", "min": 0}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["area_principal"].widget.attrs.update({"class": "form-select w-full rounded-lg border-gray-300"})
        self.fields["subarea"].widget.attrs.update({"class": "form-select w-full rounded-lg border-gray-300"})
        self.fields["sede"].widget.attrs.update({"class": "form-select w-full rounded-lg border-gray-300"})
        self.fields["tipo_tramite"].widget.attrs.update({"class": "form-select w-full rounded-lg border-gray-300"})
        self.fields["nombre"].widget.attrs.update({"readonly": "readonly"})
        self.fields["sede"].queryset = SedeTurno.objects.filter(activo=True, permite_turnos=True).order_by("nombre")
        self.fields["area_principal"].queryset = Area.objects.filter(activo=True, parent__isnull=True).order_by(
            "orden", "nombre"
        )
        self.fields["subarea"].queryset = Area.objects.filter(activo=True, parent__isnull=False).select_related(
            "parent"
        ).order_by("parent__nombre", "orden", "nombre")
        self.fields["tipo_tramite"].queryset = (
            TipoTramite.objects.filter(activo=True, requiere_turno=True)
            .select_related("area", "area__parent", "recurso_turnos")
            .prefetch_related("sedes_turno")
            .order_by("orden", "nombre")
        )

        if self.instance and self.instance.pk:
            if self.instance.sede_id:
                self.initial.setdefault("sede", self.instance.sede_id)
            if self.instance.tipo_tramite_id:
                tipo = self.instance.tipo_tramite
                if tipo and tipo.area_id:
                    if tipo.area.parent_id:
                        self.initial.setdefault("area_principal", tipo.area.parent_id)
                        self.initial.setdefault("subarea", tipo.area_id)
                    else:
                        self.initial.setdefault("area_principal", tipo.area_id)
                self.initial.setdefault("tipo_tramite", tipo.id)
            recurso = RecursoTurnos.objects.filter(configuracion_turnos=self.instance).first()
            if recurso:
                tipo = TipoTramite.objects.filter(recurso_turnos=recurso).select_related("area", "area__parent").first()
                if tipo and tipo.area_id:
                    if tipo.area.parent_id:
                        self.initial.setdefault("area_principal", tipo.area.parent_id)
                        self.initial.setdefault("subarea", tipo.area_id)
                    else:
                        self.initial.setdefault("area_principal", tipo.area_id)
                    self.initial.setdefault("tipo_tramite", tipo.id)

    def clean(self):
        cleaned = super().clean()
        area_principal = cleaned.get("area_principal")
        subarea = cleaned.get("subarea")
        sede = cleaned.get("sede")
        tipo_tramite = cleaned.get("tipo_tramite")

        if tipo_tramite:
            if not tipo_tramite.requiere_turno:
                self.add_error("tipo_tramite", "El tramite seleccionado no requiere turno y no puede tener agenda.")
            if not sede:
                self.add_error("sede", "Debe seleccionar una sede para el trámite.")
            elif not sede.permite_turnos:
                self.add_error("sede", "La sede seleccionada no permite turnos.")
            elif ConfiguracionTurnos.objects.filter(sede=sede, tipo_tramite=tipo_tramite).exclude(pk=self.instance.pk).exists():
                self.add_error("tipo_tramite", "Ya existe una agenda para esta sede y este tramite.")
            tipo_area = tipo_tramite.area
            if area_principal:
                if tipo_area.parent_id and tipo_area.parent_id != area_principal.id:
                    self.add_error("tipo_tramite", "El tramite no pertenece al area seleccionada.")
                if not tipo_area.parent_id and tipo_area.id != area_principal.id:
                    self.add_error("tipo_tramite", "El tramite no pertenece al area seleccionada.")
            if subarea and tipo_area.id != subarea.id:
                self.add_error("tipo_tramite", "El tramite no pertenece a la subarea seleccionada.")
        if tipo_tramite:
            cleaned["nombre"] = tipo_tramite.nombre
        return cleaned


class DisponibilidadConfiguracionForm(forms.ModelForm):
    dias_semana = forms.MultipleChoiceField(
        label="Dias de la semana",
        required=False,
        choices=DisponibilidadConfiguracion._meta.get_field("dia_semana").choices,
        widget=forms.CheckboxSelectMultiple(),
    )
    cantidad_slots = forms.IntegerField(
        label="Slots en este rango",
        min_value=1,
        initial=1,
        widget=forms.NumberInput(
            attrs={"class": "form-input w-full rounded-lg border-gray-300", "min": 1}
        ),
    )

    class Meta:
        model = DisponibilidadConfiguracion
        fields = ["dia_semana", "hora_inicio", "hora_fin", "duracion_turno_min", "cupo_maximo", "activo"]
        widgets = {
            "dia_semana": forms.Select(attrs={"class": "form-select w-full rounded-lg border-gray-300"}),
            "hora_inicio": forms.TimeInput(
                attrs={"type": "time", "class": "form-input w-full rounded-lg border-gray-300"}
            ),
            "hora_fin": forms.TimeInput(
                attrs={"type": "time", "class": "form-input w-full rounded-lg border-gray-300"}
            ),
            "duracion_turno_min": forms.NumberInput(
                attrs={"class": "form-input w-full rounded-lg border-gray-300", "min": 5, "step": 5}
            ),
            "cupo_maximo": forms.NumberInput(
                attrs={"class": "form-input w-full rounded-lg border-gray-300", "min": 1}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_update = bool(getattr(self.instance, "pk", None))
        self.fields["hora_fin"].widget = forms.HiddenInput()
        self.fields["hora_fin"].required = False
        self.fields["cupo_maximo"].widget = forms.HiddenInput()
        self.fields["cupo_maximo"].required = False
        self.initial.setdefault("cupo_maximo", 1)
        if is_update:
            self.fields["dias_semana"].widget = forms.MultipleHiddenInput()
            self.fields["dias_semana"].required = False
            self.fields["dia_semana"].required = True
            if self.instance.hora_inicio and self.instance.hora_fin and self.instance.duracion_turno_min:
                inicio_dt = datetime.combine(datetime.today(), self.instance.hora_inicio)
                fin_dt = datetime.combine(datetime.today(), self.instance.hora_fin)
                minutos_totales = int((fin_dt - inicio_dt).total_seconds() / 60)
                if self.instance.duracion_turno_min > 0 and minutos_totales > 0:
                    self.initial["cantidad_slots"] = max(1, int(self.instance.cupo_maximo or 1))
        else:
            self.fields["dia_semana"].required = False
            dia = self.initial.get("dia_semana")
            if dia is not None and str(dia).isdigit():
                self.initial["dias_semana"] = [str(dia)]

    def clean(self):
        cleaned = super().clean()
        hora_inicio = cleaned.get("hora_inicio")
        duracion = cleaned.get("duracion_turno_min")
        cantidad_slots = cleaned.get("cantidad_slots")

        if hora_inicio and duracion and cantidad_slots:
            inicio_dt = datetime.combine(datetime.today(), hora_inicio)
            minutos_totales = int(duracion)
            fin_dt = inicio_dt + timedelta(minutes=minutos_totales)
            if fin_dt.date() != inicio_dt.date():
                raise ValidationError(
                    "El rango horario no puede cruzar de día. Ajusta duración o cantidad de slots."
                )
            cleaned["hora_fin"] = fin_dt.time()
            cleaned["_slots_preview"] = 1
            cleaned["_resto_min"] = 0
            cleaned["cupo_maximo"] = int(cantidad_slots)

        if not getattr(self.instance, "pk", None):
            dias = cleaned.get("dias_semana") or []
            if not dias:
                self.add_error("dias_semana", "Selecciona al menos un dia de la semana.")
            else:
                cleaned["dias_semana"] = [int(d) for d in dias]
                cleaned["dia_semana"] = cleaned["dias_semana"][0]

        return cleaned


class AprobarTurnoForm(forms.Form):
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "form-textarea w-full rounded-lg border-gray-300",
                "placeholder": "Notas internas opcionales...",
            }
        ),
        label="Notas internas",
    )


class RechazarTurnoForm(forms.Form):
    motivo = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "form-textarea w-full rounded-lg border-gray-300",
                "placeholder": "Motivo de rechazo (visible para el ciudadano)...",
            }
        ),
        label="Motivo de rechazo",
    )


class CancelarTurnoBackofficeForm(forms.Form):
    motivo = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "form-textarea w-full rounded-lg border-gray-300",
                "placeholder": "Motivo de cancelación (visible para el ciudadano)...",
            }
        ),
        label="Motivo de cancelación",
    )


class SedeTurnoForm(forms.ModelForm):
    class Meta:
        model = SedeTurno
        fields = ["nombre", "direccion", "telefono", "permite_turnos", "tramites_habilitados", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-input w-full rounded-lg border-gray-300"}),
            "direccion": forms.TextInput(attrs={"class": "form-input w-full rounded-lg border-gray-300"}),
            "telefono": forms.TextInput(attrs={"class": "form-input w-full rounded-lg border-gray-300"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_class = (
            "block w-full rounded-lg border border-[#D1D5DB] bg-white px-3 py-2 text-sm text-[#252F40] "
            "shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        )
        for field_name in ["nombre", "direccion", "telefono"]:
            self.fields[field_name].widget.attrs["class"] = input_class

        tramites_qs = TipoTramite.objects.filter(activo=True)
        if self.instance and self.instance.pk:
            ids_habilitados = list(self.instance.tramites_habilitados.values_list("id", flat=True))
            ids_con_agenda = list(
                ConfiguracionTurnos.objects.filter(sede=self.instance, tipo_tramite__isnull=False).values_list(
                    "tipo_tramite_id", flat=True
                )
            )
            ids_extra = [tid for tid in (ids_habilitados + ids_con_agenda) if tid]
            if ids_extra:
                tramites_qs = TipoTramite.objects.filter(Q(activo=True) | Q(pk__in=ids_extra))
                self.initial["tramites_habilitados"] = list({tid for tid in ids_extra})
        self.fields["tramites_habilitados"].queryset = tramites_qs.distinct().order_by("orden", "nombre")
        self.fields["tramites_habilitados"].widget = forms.SelectMultiple(
            attrs={"class": "hidden", "id": "id_tramites_habilitados_real"}
        )
        self.fields["tramites_habilitados"].widget.choices = self.fields["tramites_habilitados"].choices


