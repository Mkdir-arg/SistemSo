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


class TipoTramiteConfigForm(StyledModelForm):
    ICON_CHOICES = [
        ("", "Automatico (portada o icono por defecto)"),
        ("far fa-file-alt", "Archivo"),
        ("far fa-id-card", "Identificacion"),
        ("fas fa-university", "Institucional"),
        ("fas fa-tools", "Servicios"),
        ("far fa-calendar-check", "Turno"),
        ("far fa-folder-open", "Carpeta"),
        ("far fa-money-bill-alt", "Pago"),
        ("far fa-handshake", "Acuerdo"),
        ("fas fa-car", "Conducir"),
        ("fas fa-home", "Vivienda"),
        ("fas fa-briefcase", "Trabajo"),
        ("fas fa-graduation-cap", "Educacion"),
        ("fas fa-hospital", "Salud"),
        ("fas fa-tree", "Ambiente"),
        ("fas fa-road", "Transito"),
        ("fas fa-hard-hat", "Obra"),
        ("fas fa-store", "Comercio"),
        ("fas fa-file-signature", "Solicitud"),
        ("fas fa-stamp", "Certificacion"),
        ("fas fa-users", "Comunidad"),
        ("fas fa-balance-scale", "Legal"),
        ("fas fa-shield-alt", "Seguridad"),
        ("fas fa-wheelchair", "Accesibilidad"),
        ("fas fa-leaf", "Ecologia"),
        ("fas fa-bus", "Transporte"),
        ("fas fa-lightbulb", "Innovacion"),
        ("fas fa-globe", "General"),
    ]
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
        model = TipoTramite
        fields = [
            "nombre",
            "descripcion",
            "codigo",
            "icono",
            "imagen_portada",
            "area",
            "destacado",
            "requiere_pago",
            "requiere_turno",
            "permite_online",
            "permite_presencial",
            "requiere_adjunto",
            "requiere_validacion_manual",
            "costo",
            "requisitos_info",
            "informacion_extra",
            "sla_horas",
            "prioridad_default",
            "orden",
            "activo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descripcion"].required = False
        self.fields["icono"].required = False
        self.fields["imagen_portada"].required = False
        self.fields["costo"].required = False
        self.fields["requisitos_info"].required = False
        self.fields["informacion_extra"].required = False
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
        self.fields["prioridad_default"].queryset = PrioridadTramite.objects.filter(activo=True).order_by("nivel", "nombre")
        self.fields["icono"].widget = forms.Select(choices=self.ICON_CHOICES)

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
        else:
            self.add_error("area_principal", "Debe seleccionar un area.")
            return cleaned_data

        permite_online = bool(cleaned_data.get("permite_online"))
        permite_presencial = bool(cleaned_data.get("permite_presencial"))

        if not (permite_online or permite_presencial):
            self.add_error("permite_online", "Debe habilitar al menos una modalidad: online o presencial.")
            self.add_error("permite_presencial", "Debe habilitar al menos una modalidad: online o presencial.")

        return cleaned_data


class EstadoTramiteConfigForm(StyledModelForm):
    class Meta:
        model = EstadoTramite
        fields = ["nombre", "codigo", "descripcion", "es_inicial", "es_final", "color", "orden", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descripcion"].required = False
        self.fields["color"].required = False
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
        fields = ["nombre", "codigo", "descripcion", "nivel", "color", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descripcion"].required = False
        self.fields["color"].required = False
        self.fields["nivel"].label = "Orden de prioridad"
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


class CampoDinamicoTramiteInlineConfigForm(StyledModelForm):
    opciones_texto = forms.CharField(
        required=False,
        label="Opciones (solo selección)",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Una opción por línea"}),
    )

    class Meta:
        model = CampoDinamicoTramite
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
        self.fields["codigo"].required = False
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
        if tipo_dato == CampoDinamicoTramite.TipoDato.SELECCION and not opciones_texto:
            self.add_error("opciones_texto", "Debe cargar al menos una opción para tipo selección.")
        return cleaned_data


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
        queryset = EstadoTramite.objects.filter(activo=True).order_by("orden", "nombre")
        if current_estado_id:
            queryset = queryset.exclude(pk=current_estado_id)
        self.fields["estado_nuevo"].queryset = queryset
        StyledModelForm.apply_style(self)


class TramiteDerivacionForm(forms.Form):
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


class TramiteSeguimientoForm(forms.Form):
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


class TramiteSolicitudDatoCampoForm(forms.Form):
    campo_objetivo = forms.CharField(label="Campo objetivo", max_length=120)
    motivo = forms.CharField(
        label="Motivo de la solicitud",
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        StyledModelForm.apply_style(self)
