from django import forms


class SolicitudDetalleBaseForm(forms.Form):
    descripcion = forms.CharField(
        label="Descripcion",
        required=True,
        widget=forms.Textarea(
            attrs={
                "rows": 6,
                "placeholder": "Describi el problema con el mayor detalle posible",
            }
        ),
    )
    fecha_aproximada = forms.DateField(
        label="Fecha aproximada",
        required=True,
        input_formats=["%Y-%m-%d", "%d/%m/%Y"],
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    adjuntos = forms.FileField(
        label="Archivos adjuntos (opcional)",
        required=False,
        widget=forms.ClearableFileInput(),
    )


class ReclamoDetalleForm(SolicitudDetalleBaseForm):
    area_id = forms.IntegerField(widget=forms.HiddenInput())
    tipo_id = forms.IntegerField(required=True)
    titulo_solicitud = forms.CharField(required=True, max_length=200)
    direccion_ubicacion = forms.CharField(required=True, max_length=255)


class TramiteDetalleForm(SolicitudDetalleBaseForm):
    tipo_id = forms.IntegerField(widget=forms.HiddenInput())
