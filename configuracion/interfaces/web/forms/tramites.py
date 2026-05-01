from django import forms
from django.contrib.auth import get_user_model

from reclamos.models import Area
from tramites.models import (
    CampoDinamicoOpcion,
    CampoDinamicoTramite,
    EstadoTramite,
    EstadoTramiteTransicion,
    PrioridadTramite,
    RequisitoTramite,
    TipoTramite,
    Tramite,
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


class AreaTramiteConfigForm(StyledModelForm):
    class Meta:
        model = Area
        fields = ["nombre", "descripcion", "codigo", "email_contacto", "telefono_contacto", "orden", "municipio", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descripcion"].required = False
        self.fields["email_contacto"].required = False
        self.fields["telefono_contacto"].required = False
        self.fields["orden"].required = False
        self.fields["municipio"].required = False
        self.apply_style()


class TipoTramiteConfigForm(StyledModelForm):
    class Meta:
        model = TipoTramite
        fields = [
            "nombre",
            "descripcion",
            "codigo",
            "area",
            "requiere_pago",
            "requiere_turno",
            "permite_online",
            "permite_presencial",
            "requiere_adjunto",
            "requiere_validacion_manual",
            "sla_horas",
            "prioridad_default",
            "orden",
            "municipio",
            "activo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descripcion"].required = False
        self.fields["sla_horas"].required = False
        self.fields["prioridad_default"].required = False
        self.fields["municipio"].required = False
        self.fields["area"].queryset = Area.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["prioridad_default"].queryset = PrioridadTramite.objects.filter(activo=True).order_by("nivel", "nombre")
        self.apply_style()


class EstadoTramiteConfigForm(StyledModelForm):
    class Meta:
        model = EstadoTramite
        fields = ["nombre", "codigo", "descripcion", "es_inicial", "es_final", "color", "orden", "municipio", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descripcion"].required = False
        self.fields["color"].required = False
        self.fields["municipio"].required = False
        self.apply_style()


class EstadoTramiteTransicionConfigForm(StyledModelForm):
    class Meta:
        model = EstadoTramiteTransicion
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
        self.fields["estado_origen"].queryset = EstadoTramite.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["estado_destino"].queryset = EstadoTramite.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["areas_permitidas"].queryset = Area.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["descripcion"].required = False
        self.fields["grupos_permitidos"].required = False
        self.fields["areas_permitidas"].required = False
        self.fields["grupos_permitidos"].widget = forms.CheckboxSelectMultiple()
        self.fields["areas_permitidas"].widget = forms.CheckboxSelectMultiple()
        self.apply_style()


class PrioridadTramiteConfigForm(StyledModelForm):
    class Meta:
        model = PrioridadTramite
        fields = ["nombre", "codigo", "descripcion", "nivel", "color", "municipio", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descripcion"].required = False
        self.fields["color"].required = False
        self.fields["municipio"].required = False
        self.apply_style()


class RequisitoTramiteConfigForm(StyledModelForm):
    class Meta:
        model = RequisitoTramite
        fields = [
            "tipo_tramite",
            "nombre",
            "codigo",
            "descripcion",
            "campo_dinamico",
            "obligatorio",
            "requiere_adjunto",
            "orden",
            "activo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipo_tramite"].queryset = TipoTramite.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["campo_dinamico"].queryset = CampoDinamicoTramite.objects.filter(activo=True).order_by(
            "tipo_tramite",
            "orden",
            "nombre",
        )
        self.fields["codigo"].required = False
        self.fields["descripcion"].required = False
        self.fields["campo_dinamico"].required = False
        self.apply_style()


class CampoDinamicoTramiteConfigForm(StyledModelForm):
    class Meta:
        model = CampoDinamicoTramite
        fields = [
            "tipo_tramite",
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
        self.fields["tipo_tramite"].queryset = TipoTramite.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["descripcion"].required = False
        self.fields["placeholder"].required = False
        self.fields["ayuda"].required = False
        self.fields["valor_default"].required = False
        self.fields["longitud_maxima"].required = False
        self.apply_style()


class CampoDinamicoOpcionConfigForm(StyledModelForm):
    class Meta:
        model = CampoDinamicoOpcion
        fields = ["campo", "etiqueta", "valor", "orden", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["campo"].queryset = CampoDinamicoTramite.objects.filter(activo=True).order_by(
            "tipo_tramite", "orden", "nombre"
        )
        self.apply_style()


class TramiteConfigForm(StyledModelForm):
    class Meta:
        model = Tramite
        fields = [
            "titulo",
            "descripcion",
            "tipo_tramite",
            "area_actual",
            "estado",
            "prioridad",
            "origen",
            "municipio",
            "asignado_a",
            "canal_detalle",
            "requiere_inspeccion",
            "requiere_documentacion_adicional",
            "visible_ciudadano",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipo_tramite"].queryset = TipoTramite.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["area_actual"].queryset = Area.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["estado"].queryset = EstadoTramite.objects.filter(activo=True).order_by("orden", "nombre")
        self.fields["prioridad"].queryset = PrioridadTramite.objects.filter(activo=True).order_by("nivel", "nombre")

        self.fields["area_actual"].required = False
        self.fields["estado"].required = False
        self.fields["prioridad"].required = False
        self.fields["municipio"].required = False
        self.fields["asignado_a"].required = False
        self.fields["canal_detalle"].required = False
        self.apply_style()


class TramiteCambioEstadoForm(forms.Form):
    estado_nuevo = forms.ModelChoiceField(
        queryset=EstadoTramite.objects.none(),
        label="Nuevo estado",
    )
    comentario = forms.CharField(
        label="Comentario",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["estado_nuevo"].queryset = EstadoTramite.objects.filter(activo=True).order_by("orden", "nombre")
        StyledModelForm.apply_style(self)


class TramiteDerivacionForm(forms.Form):
    area = forms.ModelChoiceField(
        queryset=Area.objects.none(),
        label="Area destino",
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
        self.fields["usuario"].queryset = get_user_model().objects.filter(
            is_active=True, 
            ciudadano_perfil__isnull=True
        ).order_by("username")
        StyledModelForm.apply_style(self)


class TramiteSeguimientoForm(forms.Form):
    comentario = forms.CharField(
        label="Seguimiento",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    es_interno = forms.BooleanField(label="Comentario interno", required=False, initial=True)
    visible_ciudadano = forms.BooleanField(label="Visible para ciudadano", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        StyledModelForm.apply_style(self)
