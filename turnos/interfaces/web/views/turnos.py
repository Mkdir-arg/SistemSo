from datetime import date
from urllib.parse import urlencode
import re

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, TemplateView

from portal.models import TurnoCiudadano

from turnos.interfaces.web.forms import AprobarTurnoForm, CancelarTurnoBackofficeForm, RechazarTurnoForm
from turnos.mixins import OperadorRequiredMixin, TurnoOperarRequiredMixin, operador_required, turno_operar_required
from turnos.models import ConfiguracionTurnos
from turnos.infrastructure.selectors.backoffice import (
    build_agenda_context,
    build_bandeja_pendientes_context,
    get_backoffice_home_context,
    get_turno_detalle_queryset,
)
from turnos.interfaces.module_api import (
    TurnoActionError,
    actualizar_notas_turno_backoffice,
    aprobar_turno_backoffice,
    cancelar_turno_backoffice,
    completar_turno_backoffice,
    rechazar_turno_backoffice,
)


class BackofficeHomeView(OperadorRequiredMixin, TemplateView):
    template_name = 'turnos/backoffice/home.html'

    def get_context_data(self, **kwargs):
        return get_backoffice_home_context()


class AgendaView(TurnoOperarRequiredMixin, TemplateView):
    template_name = 'turnos/backoffice/agenda.html'

    def get_context_data(self, **kwargs):
        hoy = date.today()
        fecha_str = self.request.GET.get('fecha', hoy.isoformat())
        config_id = self.request.GET.get('config')
        try:
            fecha = date.fromisoformat(fecha_str)
        except ValueError:
            fecha = hoy
        estado_filter = self.request.GET.get('estado')
        return build_agenda_context(fecha, config_id=config_id, estado_filter=estado_filter)


class BandejaPendientesView(TurnoOperarRequiredMixin, TemplateView):
    template_name = 'turnos/backoffice/bandeja_pendientes.html'

    def get_context_data(self, **kwargs):
        return build_bandeja_pendientes_context()


class TurnoDetailView(TurnoOperarRequiredMixin, DetailView):
    template_name = 'turnos/backoffice/turno_detalle.html'
    context_object_name = 'turno'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return get_turno_detalle_queryset()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        next_url = request.GET.get('next', '')
        if 'notas_backoffice' in request.POST:
            nota_nueva = (request.POST.get('notas_backoffice') or '').strip()
            if nota_nueva:
                autor = request.user.get_full_name() or request.user.username
                marca_tiempo = timezone.localtime().strftime('%d/%m/%Y %H:%M')
                entrada = f"[{marca_tiempo}] {autor}: {nota_nueva}"
                notas_previas = (self.object.notas_backoffice or '').strip()
                notas_finales = f"{notas_previas}\n{entrada}".strip() if notas_previas else entrada
            else:
                notas_finales = (self.object.notas_backoffice or '').strip()
            actualizar_notas_turno_backoffice(
                self.object, notas_finales
            )
            messages.success(request, 'Nota agregada al historial interno.')

        redirect_url = f"/turnos/turnos/{self.object.pk}/"
        if next_url:
            redirect_url = f"{redirect_url}?{urlencode({'next': next_url})}"
        return redirect(redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        turno = self.object
        next_url = self.request.GET.get('next')
        if next_url:
            agenda_url = next_url
        else:
            agenda_url = f"/turnos/agenda/?fecha={turno.fecha.isoformat()}"
            config = getattr(turno, 'config_efectiva', None)
            if config and getattr(config, 'pk', None):
                agenda_url = f"{agenda_url}&config={config.pk}"

        notas_brutas = (turno.notas_backoffice or '').strip()
        notas_historial = []
        motivo_cancelacion_sistema = ''
        patron_nota = re.compile(r'^\[(?P<fecha>[^\]]+)\]\s+(?P<autor>[^:]+):\s*(?P<texto>.*)$')
        for linea in [ln.strip() for ln in notas_brutas.splitlines() if ln.strip()]:
            if '[CANCELACION_SISTEMA]' in linea:
                if not motivo_cancelacion_sistema:
                    motivo_cancelacion_sistema = linea.split('[CANCELACION_SISTEMA]', 1)[1].strip()
                continue
            if '[RECHAZO_SISTEMA]' in linea:
                if not motivo_cancelacion_sistema:
                    motivo_cancelacion_sistema = linea.split('[RECHAZO_SISTEMA]', 1)[1].strip()
                continue
            match = patron_nota.match(linea)
            if match:
                notas_historial.append(
                    {
                        'fecha': match.group('fecha').strip(),
                        'autor': match.group('autor').strip(),
                        'texto': match.group('texto').strip(),
                    }
                )
            else:
                notas_historial.append({'fecha': '', 'autor': 'Sistema', 'texto': linea})
        notas_historial.reverse()

        context.update(
            {
                'form_aprobar': AprobarTurnoForm(),
                'form_rechazar': RechazarTurnoForm(),
                'form_cancelar': CancelarTurnoBackofficeForm(),
                'next_url': next_url or '',
                'agenda_url': agenda_url,
                'puede_aprobar': turno.estado == TurnoCiudadano.Estado.PENDIENTE,
                'puede_completar': (
                    turno.estado == TurnoCiudadano.Estado.CONFIRMADO and turno.fecha <= date.today()
                ),
                'puede_cancelar': turno.estado
                in [TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO],
                'notas_historial': notas_historial,
                'motivo_cancelacion_sistema': motivo_cancelacion_sistema,
            }
        )
        return context


def _detail_redirect(pk, next_url=''):
    if next_url:
        return redirect(f"/turnos/turnos/{pk}/?{urlencode({'next': next_url})}")
    return redirect(f"/turnos/turnos/{pk}/")


@turno_operar_required
@require_POST
def turno_aprobar(request, pk):
    turno = get_object_or_404(TurnoCiudadano, pk=pk)
    next_url = request.POST.get('next') or ''
    if turno.estado != TurnoCiudadano.Estado.PENDIENTE:
        messages.warning(request, 'Este turno ya fue procesado.')
        return _detail_redirect(pk, next_url)

    form = AprobarTurnoForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Datos inválidos.')
        return _detail_redirect(pk, next_url)

    try:
        turno = aprobar_turno_backoffice(
            pk, request.user, notas=form.cleaned_data.get('notas', '')
        )
    except TurnoActionError as exc:
        messages.warning(request, str(exc))
        return _detail_redirect(pk, next_url)

    messages.success(
        request,
        f'Turno {turno.codigo_turno} confirmado. Se notificó al ciudadano por email.',
    )
    return redirect(next_url or 'turnos:bandeja_pendientes')


@turno_operar_required
@require_POST
def turno_rechazar(request, pk):
    turno = get_object_or_404(TurnoCiudadano, pk=pk)
    next_url = request.POST.get('next') or ''
    if turno.estado != TurnoCiudadano.Estado.PENDIENTE:
        messages.warning(request, 'Este turno ya fue procesado.')
        return _detail_redirect(pk, next_url)

    form = RechazarTurnoForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Debe ingresar un motivo de rechazo.')
        return _detail_redirect(pk, next_url)

    try:
        turno = rechazar_turno_backoffice(pk, request.user, form.cleaned_data['motivo'])
    except TurnoActionError as exc:
        messages.warning(request, str(exc))
        return _detail_redirect(pk, next_url)

    messages.success(request, f'Turno {turno.codigo_turno} rechazado. Se notificó al ciudadano.')
    return redirect(next_url or 'turnos:bandeja_pendientes')


@turno_operar_required
@require_POST
def turno_cancelar(request, pk):
    turno = get_object_or_404(TurnoCiudadano, pk=pk)
    next_url = request.POST.get('next') or ''
    form = CancelarTurnoBackofficeForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Debe ingresar un motivo de cancelación.')
        return _detail_redirect(pk, next_url)

    try:
        turno = cancelar_turno_backoffice(turno, form.cleaned_data['motivo'], user=request.user)
    except TurnoActionError as exc:
        messages.warning(request, str(exc))
        return _detail_redirect(pk, next_url)

    messages.success(request, f'Turno {turno.codigo_turno} cancelado. Se notificó al ciudadano.')
    return redirect(next_url or 'turnos:agenda')


@turno_operar_required
@require_POST
def turno_completar(request, pk):
    turno = get_object_or_404(TurnoCiudadano, pk=pk)
    next_url = request.POST.get('next') or ''
    try:
        turno = completar_turno_backoffice(turno)
    except TurnoActionError as exc:
        messages.warning(request, str(exc))
        return _detail_redirect(pk, next_url)
    messages.success(request, f'Turno {turno.codigo_turno} marcado como completado.')
    return redirect(next_url or 'turnos:agenda')


@operador_required
def api_slots_configuracion(request):
    config_id = request.GET.get('config_id')
    fecha_str = request.GET.get('fecha')

    try:
        config = ConfiguracionTurnos.objects.get(pk=config_id, activo=True)
        fecha = date.fromisoformat(fecha_str)
    except (ConfiguracionTurnos.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'error': 'Parámetros inválidos'}, status=400)

    from turnos.turnos_utils import get_slots_por_configuracion

    slots = get_slots_por_configuracion(config, fecha)
    return JsonResponse(
        {
            'slots': [
                {
                    'hora_inicio': slot['hora_inicio'].strftime('%H:%M'),
                    'hora_fin': slot['hora_fin'].strftime('%H:%M'),
                    'disponible': slot['disponible'],
                    'cupo_restante': slot['cupo_restante'],
                }
                for slot in slots
            ]
        }
    )


backoffice_home = BackofficeHomeView.as_view()
agenda = AgendaView.as_view()
bandeja_pendientes = BandejaPendientesView.as_view()
turno_detalle = TurnoDetailView.as_view()
