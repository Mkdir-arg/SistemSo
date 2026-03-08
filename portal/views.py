from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from core.models import Institucion, Provincia, Municipio, Localidad
from core.forms import InstitucionForm


class PortalHomeView(TemplateView):
    template_name = 'portal/home.html'

    def get_context_data(self, **kwargs):
        from legajos.models_programas import Programa, InscripcionPrograma
        from legajos.models import Ciudadano
        from portal.models import RecursoTurnos
        from core.models import Institucion

        ctx = super().get_context_data(**kwargs)
        ctx['programas'] = Programa.objects.filter(activo=True).order_by('orden')
        ctx['instituciones'] = Institucion.objects.all()[:6]
        ctx['recursos_turnos'] = RecursoTurnos.objects.filter(activo=True)[:6]
        ctx['stats'] = {
            'ciudadanos': Ciudadano.objects.count(),
            'instituciones': Institucion.objects.count(),
            'programas': Programa.objects.filter(activo=True).count(),
            'inscripciones_activas': InscripcionPrograma.objects.filter(estado__in=['ACTIVO', 'EN_SEGUIMIENTO']).count(),
        }
        ctx['ciudadano_items'] = [
            'Mis programas sociales e inscripciones',
            'Solicitar y gestionar turnos online',
            'Consultas y reclamos municipales',
            'Mis datos personales y contraseña',
        ]
        ctx['institucion_items'] = [
            'Registro guiado paso a paso',
            'Seguimiento del estado del trámite',
            'Articulación con programas municipales',
            'Mesa de ayuda especializada',
        ]
        return ctx


@csrf_exempt
def crear_usuario_institucion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return render(request, 'portal/crear_usuario.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False  # Deshabilitado hasta aprobación
        )
        
        grupo_institucion, _ = Group.objects.get_or_create(name='EncargadoInstitucion')
        user.groups.add(grupo_institucion)
        
        # Guardar ID del usuario en sesión para el registro de institución
        request.session['pending_user_id'] = user.id
        messages.success(request, 'Usuario creado exitosamente. Complete ahora los datos de su institución.')
        return redirect('portal:registro_institucion')
    
    return render(request, 'portal/crear_usuario.html')


@csrf_exempt
def registro_institucion(request):
    # Verificar si hay un usuario pendiente en sesión o si está autenticado
    pending_user_id = request.session.get('pending_user_id')
    
    if not request.user.is_authenticated and not pending_user_id:
        return redirect('portal:crear_usuario')
    
    if request.method == 'POST':
        form = InstitucionForm(request.POST)
        if form.is_valid():
            institucion = form.save(commit=False)
            institucion.estado_registro = 'ENVIADO'
            institucion.save()
            
            # Asociar usuario (priorizar pendiente sobre autenticado)
            if pending_user_id:
                try:
                    pending_user = User.objects.get(id=pending_user_id)
                    institucion.encargados.add(pending_user)
                    # Limpiar sesión
                    del request.session['pending_user_id']
                except User.DoesNotExist:
                    messages.error(request, 'Error: Usuario no encontrado')
                    return redirect('portal:crear_usuario')
            elif request.user.is_authenticated:
                institucion.encargados.add(request.user)
            
            messages.success(request, 'Solicitud enviada correctamente. Recibirá notificaciones por email.')
            return redirect('portal:consultar_tramite')
    else:
        form = InstitucionForm()
    
    return render(request, 'portal/registro_institucion.html', {'form': form})


@csrf_exempt
def consultar_tramite(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            instituciones = Institucion.objects.filter(encargados=user).select_related('provincia', 'municipio', 'localidad')
            return render(request, 'portal/consultar_tramite.html', {
                'instituciones': instituciones,
                'email': email
            })
        except User.DoesNotExist:
            messages.error(request, 'No se encontraron trámites con ese email')
    
    return render(request, 'portal/consultar_tramite.html')


def get_municipios(request):
    provincia_id = request.GET.get('provincia_id')
    municipios = Municipio.objects.filter(provincia_id=provincia_id).select_related('provincia').values('id', 'nombre')
    return JsonResponse(list(municipios), safe=False)


def get_localidades(request):
    municipio_id = request.GET.get('municipio_id')
    localidades = Localidad.objects.filter(municipio_id=municipio_id).select_related('municipio').values('id', 'nombre')
    return JsonResponse(list(localidades), safe=False)