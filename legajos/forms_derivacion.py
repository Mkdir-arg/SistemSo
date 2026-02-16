from django import forms
from .models_programas import Programa, DerivacionPrograma


class DerivarProgramaForm(forms.ModelForm):
    """Formulario para derivar ciudadano a un programa"""
    
    class Meta:
        model = DerivacionPrograma
        fields = ['programa_origen', 'programa_destino', 'motivo', 'urgencia']
        widgets = {
            'programa_origen': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'programa_destino': forms.Select(attrs={
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
        ciudadano = kwargs.pop('ciudadano', None)
        super().__init__(*args, **kwargs)
        
        if ciudadano:
            from .services_solapas import SolapasService
            
            # Programas activos del ciudadano (para origen)
            programas_activos = SolapasService.obtener_programas_activos(ciudadano)
            self.fields['programa_origen'].queryset = Programa.objects.filter(
                id__in=[p.programa.id for p in programas_activos]
            )
            self.fields['programa_origen'].required = False
            self.fields['programa_origen'].empty_label = "Derivación espontánea"
            
            # Todos los programas activos disponibles para derivación
            self.fields['programa_destino'].queryset = Programa.objects.filter(activo=True).order_by('orden', 'nombre')
            self.fields['programa_destino'].empty_label = "Seleccionar programa..."
