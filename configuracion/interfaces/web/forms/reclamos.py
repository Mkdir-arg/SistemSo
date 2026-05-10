from django import forms
from django.contrib.auth import get_user_model

from reclamos.models import (
    Area,
    CampoDinamicoOpcion,
    CampoDinamicoReclamo,
    EstadoReclamo,
    EstadoReclamoTransicion,
    PrioridadReclamo,
    Reclamo,
    TipoReclamo,
)


class StyledModelForm(forms.ModelForm):
    def apply_style(self):
        input_class = "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-arg-azul"
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "rounded border-gray-300 text-arg-azul focus:ring-arg-azul")
                continue
            field.widget.attrs.setdefault("class", input_class)
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 4)


class ReclamoConfigForm(StyledModelForm):
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

    class Meta:
        model = Reclamo
        fields = [
            "titulo",
            "descripcion",
            "tipo_reclamo",
            "estado",
            "prioridad",
            "origen",
            "municipio",
            "asignado_a",
            "canal_detalle",
            "es_anonimo",
            "requiere_inspeccion",
            "visible_ciudadano",
            "area_actual",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipo_reclamo"].queryset = TipoReclamo.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["area_actual"].queryset = Area.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["area_principal"].queryset = Area.objects.filter(activo=True, parent__isnull=True).order_by("orden", "nombre")
        self.fields["subarea"].queryset = Area.objects.filter(activo=True, parent__isnull=False).select_related("parent").order_by(
            "parent__nombre", "orden", "nombre"
        )
        self.fields["estado"].queryset = EstadoReclamo.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["prioridad"].queryset = PrioridadReclamo.objects.filter(activo=True).order_by("nivel", "nombre")

        self.fields["area_actual"].required = False
        self.fields["area_actual"].widget = forms.HiddenInput()
        self.fields["estado"].required = False
        self.fields["prioridad"].required = False
        self.fields["municipio"].required = False
        self.fields["asignado_a"].required = False
        self.fields["canal_detalle"].required = False

        if self.instance and self.instance.pk and self.instance.area_actual:
            if self.instance.area_actual.parent_id:
                self.initial.setdefault("area_principal", self.instance.area_actual.parent_id)
                self.initial.setdefault("subarea", self.instance.area_actual_id)
            else:
                self.initial.setdefault("area_principal", self.instance.area_actual_id)

        self.apply_style()

    def clean(self):
        cleaned_data = super().clean()
        area_principal = cleaned_data.get("area_principal")
        subarea = cleaned_data.get("subarea")

        if subarea and subarea.parent_id:
            if area_principal and subarea.parent_id != area_principal.id:
                self.add_error("subarea", "La subarea seleccionada no corresponde al area.")
                return cleaned_data
            cleaned_data["area_actual"] = subarea
            return cleaned_data

        if area_principal:
            cleaned_data["area_actual"] = area_principal
            return cleaned_data

        cleaned_data["area_actual"] = None
        return cleaned_data


class AreaConfigForm(StyledModelForm):
    class Meta:
        model = Area
        fields = ["nombre", "descripcion", "codigo", "email_contacto", "telefono_contacto", "orden", "parent", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descripcion"].required = False
        self.fields["email_contacto"].required = False
        self.fields["telefono_contacto"].required = False
        self.fields["orden"].required = False
        self.fields["parent"].required = False
        parent_queryset = Area.objects.filter(activo=True).order_by("orden", "nombre", "id")
        if self.instance and self.instance.pk:
            parent_queryset = parent_queryset.exclude(pk=self.instance.pk)
        self.fields["parent"].queryset = parent_queryset
        self.apply_style()


class AreaRaizConfigForm(StyledModelForm):
    class Meta:
        model = Area
        fields = ["nombre", "descripcion", "codigo", "email_contacto", "telefono_contacto", "orden", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descripcion"].required = False
        self.fields["email_contacto"].required = False
        self.fields["telefono_contacto"].required = False
        self.fields["orden"].required = False
        self.apply_style()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.parent = None
        if commit:
            instance.save()
        return instance


class SubareaConfigForm(StyledModelForm):
    class Meta:
        model = Area
        fields = ["parent", "nombre", "descripcion", "codigo", "email_contacto", "telefono_contacto", "orden", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent"].required = True
        self.fields["parent"].queryset = Area.objects.filter(parent__isnull=True, activo=True).order_by("orden", "nombre", "id")
        self.fields["descripcion"].required = False
        self.fields["email_contacto"].required = False
        self.fields["telefono_contacto"].required = False
        self.fields["orden"].required = False
        self.apply_style()


class TipoReclamoConfigForm(StyledModelForm):
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

    class Meta:
        model = TipoReclamo
        fields = [
            "nombre",
            "descripcion",
            "imagen_portada",
            "area",
            "destacado",
            "requiere_ubicacion",
            "requiere_adjunto",
            "permite_anonimo",
            "sla_horas",
            "prioridad_default",
            "orden",
            "activo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descripcion"].required = False
        self.fields["imagen_portada"].required = False
        self.fields["sla_horas"].required = False
        self.fields["prioridad_default"].required = False
        self.fields["area"].queryset = Area.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["area"].required = False
        self.fields["area"].widget = forms.HiddenInput()
        self.fields["area_principal"].queryset = Area.objects.filter(activo=True, parent__isnull=True).order_by(
            "orden", "nombre"
        )
        self.fields["subarea"].queryset = Area.objects.filter(activo=True, parent__isnull=False).select_related(
            "parent"
        ).order_by("parent__nombre", "orden", "nombre")
        self.fields["prioridad_default"].queryset = PrioridadReclamo.objects.filter(activo=True).order_by("nivel", "nombre")

        if self.instance and self.instance.pk and self.instance.area_id:
            if self.instance.area.parent_id:
                self.initial.setdefault("area_principal", self.instance.area.parent_id)
                self.initial.setdefault("subarea", self.instance.area_id)
            else:
                self.initial.setdefault("area_principal", self.instance.area_id)

        self.apply_style()

    def clean(self):
        cleaned_data = super().clean()
        area_principal = cleaned_data.get("area_principal")
        subarea = cleaned_data.get("subarea")

        if subarea and subarea.parent_id:
            if area_principal and subarea.parent_id != area_principal.id:
                self.add_error("subarea", "La subarea seleccionada no corresponde al area.")
                return cleaned_data
            cleaned_data["area"] = subarea
            return cleaned_data

        if area_principal:
            cleaned_data["area"] = area_principal
            return cleaned_data

        self.add_error("area_principal", "Debe seleccionar un area.")
        return cleaned_data


class EstadoReclamoConfigForm(StyledModelForm):
    class Meta:
        model = EstadoReclamo
        fields = ["nombre", "codigo", "descripcion", "es_inicial", "es_final", "color", "orden", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descripcion"].required = False
        self.fields["color"].required = False
        self.apply_style()


class EstadoReclamoTransicionConfigForm(StyledModelForm):
    class Meta:
        model = EstadoReclamoTransicion
        fields = [
            "estado_origen",
            "estado_destino",
            "nombre",
            "descripcion",
            "orden",
            "requiere_comentario",
            "requiere_asignado",
            "requiere_area_responsable",
            "grupos_permitidos",
            "areas_permitidas",
            "activo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["estado_origen"].queryset = EstadoReclamo.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["estado_destino"].queryset = EstadoReclamo.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["areas_permitidas"].queryset = Area.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["descripcion"].required = False
        self.fields["grupos_permitidos"].required = False
        self.fields["areas_permitidas"].required = False
        self.fields["grupos_permitidos"].widget = forms.CheckboxSelectMultiple()
        self.fields["areas_permitidas"].widget = forms.CheckboxSelectMultiple()
        self.apply_style()


class PrioridadReclamoConfigForm(StyledModelForm):
    class Meta:
        model = PrioridadReclamo
        fields = ["nombre", "codigo", "descripcion", "nivel", "color", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descripcion"].required = False
        self.fields["color"].required = False
        self.fields["nivel"].label = "Orden de prioridad"
        self.apply_style()


class CampoDinamicoReclamoConfigForm(StyledModelForm):
    class Meta:
        model = CampoDinamicoReclamo
        fields = [
            "tipo_reclamo",
            "nombre",
            "codigo",
            "descripcion",
            "tipo_dato",
            "obligatorio",
            "orden",
            "placeholder",
            "ayuda",
            "valor_default",
            "longitud_maxima",
            "activo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipo_reclamo"].queryset = TipoReclamo.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["descripcion"].required = False
        self.fields["placeholder"].required = False
        self.fields["ayuda"].required = False
        self.fields["valor_default"].required = False
        self.fields["longitud_maxima"].required = False
        self.apply_style()


class CampoDinamicoReclamoInlineConfigForm(StyledModelForm):
    opciones_texto = forms.CharField(
        required=False,
        label="Opciones (solo selección)",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Una opción por línea"}),
    )

    class Meta:
        model = CampoDinamicoReclamo
        fields = [
            "nombre",
            "codigo",
            "descripcion",
            "tipo_dato",
            "obligatorio",
            "orden",
            "placeholder",
            "ayuda",
            "valor_default",
            "longitud_maxima",
            "activo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descripcion"].required = False
        self.fields["placeholder"].required = False
        self.fields["ayuda"].required = False
        self.fields["valor_default"].required = False
        self.fields["longitud_maxima"].required = False
        if self.instance and self.instance.pk:
            opciones = self.instance.opciones.filter(activo=True).order_by("orden", "id").values_list("etiqueta", flat=True)
            self.initial["opciones_texto"] = "\n".join(opciones)
        self.apply_style()

    def clean(self):
        cleaned_data = super().clean()
        tipo_dato = cleaned_data.get("tipo_dato")
        opciones_texto = (cleaned_data.get("opciones_texto") or "").strip()
        if tipo_dato == CampoDinamicoReclamo.TipoDato.SELECCION and not opciones_texto:
            self.add_error("opciones_texto", "Debe cargar al menos una opción para tipo selección.")
        return cleaned_data


class CampoDinamicoOpcionConfigForm(StyledModelForm):
    class Meta:
        model = CampoDinamicoOpcion
        fields = ["campo", "etiqueta", "valor", "orden", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["campo"].queryset = CampoDinamicoReclamo.objects.filter(activo=True).order_by(
            "tipo_reclamo", "orden", "nombre"
        )
        self.apply_style()


class ReclamoCambioEstadoForm(forms.Form):
    estado_nuevo = forms.ModelChoiceField(
        queryset=EstadoReclamo.objects.none(),
        label="Nuevo estado",
        empty_label="Seleccione un estado",
    )
    comentario = forms.CharField(
        label="Comentario",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        current_estado_id = kwargs.pop("current_estado_id", None)
        super().__init__(*args, **kwargs)
        queryset = EstadoReclamo.objects.filter(activo=True).order_by("orden", "nombre")
        if current_estado_id:
            queryset = queryset.exclude(pk=current_estado_id)
        self.fields["estado_nuevo"].queryset = queryset
        StyledModelForm.apply_style(self)


class ReclamoDerivacionForm(forms.Form):
    area_principal = forms.ModelChoiceField(
        queryset=Area.objects.none(),
        label="Area",
        required=False,
    )
    subarea = forms.ModelChoiceField(
        queryset=Area.objects.none(),
        label="Subarea",
        required=False,
    )
    area = forms.ModelChoiceField(
        queryset=Area.objects.none(),
        label="Area destino",
        required=False,
    )
    usuario = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        label="Usuario asignado",
        required=False,
    )
    motivo = forms.CharField(
        label="Motivo",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["area"].queryset = Area.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["area"].widget = forms.HiddenInput()
        self.fields["area_principal"].queryset = Area.objects.filter(activo=True, parent__isnull=True).order_by(
            "orden", "nombre"
        )
        self.fields["subarea"].queryset = Area.objects.filter(activo=True, parent__isnull=False).select_related(
            "parent"
        ).order_by("parent__nombre", "orden", "nombre")
        self.fields["usuario"].queryset = get_user_model().objects.filter(
            is_active=True, 
            ciudadano_perfil__isnull=True
        ).order_by("username")
        StyledModelForm.apply_style(self)

    def clean(self):
        cleaned_data = super().clean()
        area_principal = cleaned_data.get("area_principal")
        subarea = cleaned_data.get("subarea")

        if subarea and subarea.parent_id:
            if area_principal and subarea.parent_id != area_principal.id:
                self.add_error("subarea", "La subarea seleccionada no corresponde al area.")
                return cleaned_data
            cleaned_data["area"] = subarea
            return cleaned_data

        if area_principal:
            cleaned_data["area"] = area_principal
            return cleaned_data

        self.add_error("area_principal", "Debe seleccionar un area.")
        return cleaned_data


class ReclamoSeguimientoForm(forms.Form):
    comentario = forms.CharField(
        label="Observaciones",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    es_interno = forms.BooleanField(label="Comentario interno", required=False, initial=True)
    visible_ciudadano = forms.BooleanField(label="Visible para ciudadano", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        StyledModelForm.apply_style(self)

    def clean(self):
        cleaned_data = super().clean()
        es_interno = bool(cleaned_data.get("es_interno"))
        visible_ciudadano = bool(cleaned_data.get("visible_ciudadano"))

        if es_interno == visible_ciudadano:
            raise forms.ValidationError(
                "Debe seleccionar una sola opcion: comentario interno o visible para ciudadano."
            )
        return cleaned_data


class ReclamoSolicitudDatoCampoForm(forms.Form):
    campo_objetivo = forms.CharField(label="Campo objetivo", max_length=120)
    motivo = forms.CharField(
        label="Motivo de la solicitud",
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        StyledModelForm.apply_style(self)
