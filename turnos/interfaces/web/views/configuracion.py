from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from portal.models import RecursoTurnos, TurnoCiudadano
from reclamos.models import Area
from tramites.models import TipoTramite

from turnos.interfaces.web.forms import ConfiguracionTurnosForm, DisponibilidadConfiguracionForm, SedeTurnoForm
from turnos.mixins import AdminTurnosRequiredMixin, admin_turnos_required, operador_required
from turnos.models import ConfiguracionTurnos, DisponibilidadConfiguracion, SedeTurno
from turnos.infrastructure.selectors.backoffice import get_configuraciones_list


def _hay_solapamiento(configuracion, dia, hora_inicio, hora_fin, excluir_id=None):
    qs = DisponibilidadConfiguracion.objects.filter(
        configuracion=configuracion,
        dia_semana=dia,
    )
    if excluir_id:
        qs = qs.exclude(pk=excluir_id)
    return qs.filter(hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio).exists()


class ConfiguracionListView(AdminTurnosRequiredMixin, TemplateView):
    template_name = 'turnos/backoffice/configuracion_lista.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        configs = get_configuraciones_list()
        sede_id = (self.request.GET.get("sede") or "").strip()
        area_id = (self.request.GET.get("area") or "").strip()
        subarea_id = (self.request.GET.get("subarea") or "").strip()
        tramite_id = (self.request.GET.get("tramite") or "").strip()
        activo = (self.request.GET.get("activo") or "").strip()

        if sede_id.isdigit():
            configs = configs.filter(sede_id=int(sede_id))
        if area_id.isdigit():
            configs = configs.filter(tipo_tramite__area__parent_id=int(area_id))
        if subarea_id.isdigit():
            configs = configs.filter(tipo_tramite__area_id=int(subarea_id))
        if tramite_id.isdigit():
            configs = configs.filter(tipo_tramite_id=int(tramite_id))
        if activo in {"1", "0"}:
            configs = configs.filter(activo=(activo == "1"))
        tramite_contexto = None
        if tramite_id.isdigit():
            tramite_contexto = (
                TipoTramite.objects.select_related("area", "area__parent")
                .filter(pk=int(tramite_id), activo=True)
                .first()
            )

        areas = Area.objects.filter(activo=True, parent__isnull=True).order_by("orden", "nombre")
        subareas = Area.objects.filter(activo=True, parent__isnull=False).select_related("parent").order_by(
            "parent__nombre", "orden", "nombre"
        )
        tramites = TipoTramite.objects.filter(activo=True).select_related("area", "area__parent").order_by(
            "orden", "nombre"
        )
        context['configs'] = configs
        context["sedes"] = SedeTurno.objects.filter(activo=True).order_by("nombre")
        context["areas"] = areas
        context["subareas"] = subareas
        context["tramites"] = tramites
        context["filtros"] = {
            "sede": sede_id,
            "area": area_id,
            "subarea": subarea_id,
            "tramite": tramite_id,
            "activo": activo,
        }
        context["es_contexto_tramite"] = bool(tramite_contexto)
        context["tramite_contexto"] = tramite_contexto
        return context


class ConfiguracionCreateView(AdminTurnosRequiredMixin, CreateView):
    model = ConfiguracionTurnos
    form_class = ConfiguracionTurnosForm
    template_name = 'turnos/backoffice/configuracion_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Nueva agenda', 'accion': 'Crear'})
        context["es_contexto_tramite"] = self._get_tipo_tramite_contexto() is not None
        return context

    def _get_tipo_tramite_contexto(self):
        tipo_tramite_id = (self.request.GET.get("tipo_tramite") or self.request.GET.get("tramite") or "").strip()
        if not tipo_tramite_id.isdigit():
            return None
        return (
            TipoTramite.objects.select_related("area", "area__parent")
            .filter(pk=int(tipo_tramite_id), activo=True, requiere_turno=True)
            .first()
        )

    def get_initial(self):
        initial = super().get_initial()
        sede_id = (self.request.GET.get("sede") or "").strip()
        if sede_id.isdigit():
            initial["sede"] = int(sede_id)
        tipo = self._get_tipo_tramite_contexto()
        if not tipo:
            return initial
        initial["tipo_tramite"] = tipo.id
        initial["nombre"] = tipo.nombre
        if tipo.area_id:
            if tipo.area.parent_id:
                initial["area_principal"] = tipo.area.parent_id
                initial["subarea"] = tipo.area_id
            else:
                initial["area_principal"] = tipo.area_id
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        tipo = self._get_tipo_tramite_contexto()
        if not tipo:
            return form

        form.fields["tipo_tramite"].queryset = TipoTramite.objects.filter(pk=tipo.pk)
        form.fields["tipo_tramite"].widget.attrs["disabled"] = "disabled"

        if tipo.area_id:
            if tipo.area.parent_id:
                area_principal_id = tipo.area.parent_id
                subarea_id = tipo.area_id
            else:
                area_principal_id = tipo.area_id
                subarea_id = None
            form.fields["area_principal"].queryset = Area.objects.filter(pk=area_principal_id)
            form.fields["area_principal"].widget.attrs["disabled"] = "disabled"
            if subarea_id:
                form.fields["subarea"].queryset = Area.objects.filter(pk=subarea_id)
                form.fields["subarea"].widget.attrs["disabled"] = "disabled"
            else:
                form.fields["subarea"].queryset = Area.objects.none()
        return form

    def form_valid(self, form):
        self.object = form.save()
        sede = form.cleaned_data.get("sede")
        tipo_tramite = form.cleaned_data.get("tipo_tramite")
        if tipo_tramite:
            if sede:
                sede.tramites_habilitados.add(tipo_tramite)
            sede_suffix = f" - {sede.nombre}" if sede else ""
            recurso, _created = RecursoTurnos.objects.get_or_create(
                nombre=f"Agenda {tipo_tramite.nombre}{sede_suffix}",
                defaults={
                    "tipo": RecursoTurnos.Tipo.ORGANISMO,
                    "descripcion": f"Agenda de turnos para {tipo_tramite.nombre}{sede_suffix}",
                    "activo": True,
                },
            )
            if recurso.configuracion_turnos_id != self.object.id:
                recurso.configuracion_turnos = self.object
                recurso.activo = True
                recurso.save(update_fields=["configuracion_turnos", "activo"])
            if tipo_tramite.recurso_turnos_id != recurso.id:
                TipoTramite.objects.filter(pk=tipo_tramite.pk).update(recurso_turnos=recurso)
        messages.success(self.request, f'Configuración "{self.object.nombre}" creada correctamente.')
        return redirect('turnos:disponibilidad_grilla', pk=self.object.pk)


class ConfiguracionUpdateView(AdminTurnosRequiredMixin, UpdateView):
    model = ConfiguracionTurnos
    form_class = ConfiguracionTurnosForm
    template_name = 'turnos/backoffice/configuracion_form.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'config': self.object,
                'titulo': f'Editar: {self.object.nombre}',
                'accion': 'Guardar cambios',
            }
        )
        return context

    def form_valid(self, form):
        self.object = form.save()
        sede = form.cleaned_data.get("sede")
        tipo_tramite = form.cleaned_data.get("tipo_tramite")
        if tipo_tramite and sede:
            sede.tramites_habilitados.add(tipo_tramite)
        recurso = RecursoTurnos.objects.filter(configuracion_turnos=self.object).first()
        if tipo_tramite:
            if recurso:
                sede_suffix = f" - {sede.nombre}" if sede else ""
                recurso.nombre = f"Agenda {tipo_tramite.nombre}{sede_suffix}"
                recurso.descripcion = f"Agenda de turnos para {tipo_tramite.nombre}{sede_suffix}"
                recurso.save(update_fields=["nombre", "descripcion"])
        if recurso and recurso.activo != bool(self.object.activo):
            recurso.activo = bool(self.object.activo)
            recurso.save(update_fields=["activo"])
        messages.success(self.request, 'Configuraci?n actualizada correctamente.')
        return redirect('turnos:disponibilidad_grilla', pk=self.object.pk)


class SedeTurnoListView(AdminTurnosRequiredMixin, ListView):
    model = SedeTurno
    template_name = 'turnos/backoffice/sedes_lista.html'
    context_object_name = 'sedes'
    queryset = SedeTurno.objects.prefetch_related('tramites_habilitados').order_by('nombre')


class SedeTurnoCreateView(AdminTurnosRequiredMixin, CreateView):
    model = SedeTurno
    form_class = SedeTurnoForm
    template_name = 'turnos/backoffice/sede_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Nueva sede', 'accion': 'Crear sede'})
        return context

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Sede creada correctamente.')
        return redirect('turnos:sedes_lista')


class SedeTurnoUpdateView(AdminTurnosRequiredMixin, UpdateView):
    model = SedeTurno
    form_class = SedeTurnoForm
    template_name = 'turnos/backoffice/sede_form.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        configs = (
            ConfiguracionTurnos.objects.filter(sede=self.object)
            .select_related("tipo_tramite")
            .order_by("nombre")
        )
        ids_habilitados = list(self.object.tramites_habilitados.values_list("id", flat=True))
        ids_config = [cfg.tipo_tramite_id for cfg in configs if cfg.tipo_tramite_id]
        ids_union = list({tid for tid in (ids_habilitados + ids_config) if tid})
        tramites = TipoTramite.objects.filter(pk__in=ids_union).order_by("orden", "nombre")
        config_por_tramite = {cfg.tipo_tramite_id: cfg for cfg in configs if cfg.tipo_tramite_id}
        tramites_agenda = []
        for t in tramites:
            cfg = config_por_tramite.get(t.id)
            tramites_agenda.append(
                {
                    "tramite": t,
                    "config_id": cfg.id if cfg else None,
                    "agenda_activa": bool(cfg and cfg.activo),
                }
            )
        context.update({'titulo': f'Editar sede: {self.object.nombre}', 'accion': 'Guardar cambios'})
        context["tramites_agenda"] = tramites_agenda
        return context

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Sede actualizada correctamente.')
        return redirect('turnos:sede_editar', pk=self.object.pk)


class SedeTurnoDetailView(AdminTurnosRequiredMixin, DetailView):
    model = SedeTurno
    template_name = 'turnos/backoffice/sede_detalle.html'
    context_object_name = 'sede'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = (self.request.GET.get("tab") or "detalle").strip().lower()
        if tab not in {"detalle", "tramites"}:
            tab = "detalle"
        configs = (
            ConfiguracionTurnos.objects.filter(sede=self.object, activo=True)
            .select_related("tipo_tramite", "recursoturnos")
            .order_by("nombre")
        )
        ids_habilitados = list(self.object.tramites_habilitados.values_list("id", flat=True))
        ids_config = [cfg.tipo_tramite_id for cfg in configs if cfg.tipo_tramite_id]
        ids_union = list({tid for tid in (ids_habilitados + ids_config) if tid})
        tramites_qs = TipoTramite.objects.filter(pk__in=ids_union).order_by("orden", "nombre")
        config_por_tramite_id = {cfg.tipo_tramite_id: cfg.pk for cfg in configs if cfg.tipo_tramite_id}
        tramites = [
            {"obj": t, "config_id": config_por_tramite_id.get(t.id)}
            for t in tramites_qs
        ]
        context.update(
            {
                "tab": tab,
                "tramites": tramites,
                "configs_sede": configs,
                "pendientes_config": max(0, len(tramites) - len(configs)),
            }
        )
        return context


def _enriquecer_franjas(disponibilidades):
    """Agrega top_px y height_px a cada franja para posicionamiento en grilla."""
    if not disponibilidades:
        return disponibilidades, [f'{h:02d}:00' for h in range(8, 20)], 720

    def to_min(t):
        return t.hour * 60 + t.minute

    hora_min = max(0, min(d.hora_inicio.hour for d in disponibilidades) - 1)
    hora_max = min(24, max(d.hora_fin.hour for d in disponibilidades) + 1)
    offset = hora_min * 60

    for d in disponibilidades:
        d.top_px = to_min(d.hora_inicio) - offset
        d.height_px = max(44, to_min(d.hora_fin) - to_min(d.hora_inicio))

    horas = [{'label': f'{h:02d}:00', 'top': (h - hora_min) * 60} for h in range(hora_min, hora_max)]
    return disponibilidades, horas, (hora_max - hora_min) * 60


class DisponibilidadGrillaView(AdminTurnosRequiredMixin, TemplateView):
    template_name = 'turnos/backoffice/disponibilidad_grilla.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = get_object_or_404(ConfiguracionTurnos, pk=self.kwargs['pk'])
        tramite_id = (self.request.GET.get("tramite") or "").strip()
        volver_url = reverse('turnos:configuracion_lista')
        if tramite_id.isdigit():
            volver_url = f"{volver_url}?tramite={tramite_id}"
        disponibilidades = list(config.disponibilidades.all())
        disponibilidades, horas_grilla, grilla_height = _enriquecer_franjas(disponibilidades)
        por_dia = {i: [] for i in range(7)}
        for disp in disponibilidades:
            por_dia[disp.dia_semana].append(disp)
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        context.update({
            'config': config,
            'dias_con_franjas': [(i, dias[i], por_dia[i]) for i in range(7)],
            'horas_grilla': horas_grilla,
            'grilla_height': grilla_height,
            'volver_url': volver_url,
        })
        return context


class DisponibilidadCreateView(AdminTurnosRequiredMixin, TemplateView):
    template_name = 'turnos/backoffice/disponibilidad_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.config = get_object_or_404(ConfiguracionTurnos, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        if self.request.method == 'POST':
            return DisponibilidadConfiguracionForm(self.request.POST)
        dia = self.request.GET.get('dia')
        initial = {'dia_semana': dia} if dia else {}
        return DisponibilidadConfiguracionForm(initial=initial)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'form': kwargs.get('form', self.get_form()),
                'config': self.config,
                'titulo': 'Agregar franja horaria',
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            cleaned_data = form.cleaned_data
            dias = cleaned_data.get("dias_semana") or [cleaned_data.get("dia_semana")]
            creadas = 0
            repetidas = 0
            for dia in dias:
                hay_solape = _hay_solapamiento(
                    self.config,
                    dia,
                    cleaned_data["hora_inicio"],
                    cleaned_data["hora_fin"],
                )
                existe = DisponibilidadConfiguracion.objects.filter(
                    configuracion=self.config,
                    dia_semana=dia,
                    hora_inicio=cleaned_data["hora_inicio"],
                ).exists()
                if existe:
                    repetidas += 1
                    continue
                DisponibilidadConfiguracion.objects.create(
                    configuracion=self.config,
                    dia_semana=dia,
                    hora_inicio=cleaned_data["hora_inicio"],
                    hora_fin=cleaned_data["hora_fin"],
                    duracion_turno_min=cleaned_data["duracion_turno_min"],
                    cupo_maximo=cleaned_data["cupo_maximo"],
                    activo=cleaned_data["activo"],
                )
                creadas += 1
                if hay_solape:
                    messages.warning(
                        request,
                        f"Atencion: la franja {cleaned_data['hora_inicio']:%H:%M}-{cleaned_data['hora_fin']:%H:%M} "
                        f"en el dia {dia} se superpone con otra existente.",
                    )

            if creadas == 0:
                form.add_error("dias_semana", "No se crearon franjas: todas ya existían para esos días/horarios.")
                return self.render_to_response(self.get_context_data(form=form))

            resto = cleaned_data.get('_resto_min', 0)
            message = (
                f'Se agregaron {creadas} franja(s). Cada una tiene rango de '
                f'{cleaned_data["duracion_turno_min"]} min con {cleaned_data["cupo_maximo"]} slots.'
            )
            if resto:
                message += f' Quedan {resto} min sin cubrir.'
            if repetidas:
                message += f' ({repetidas} franja(s) ya existían y se omitieron).'
            messages.success(request, message)
            return redirect('turnos:disponibilidad_grilla', pk=self.config.pk)
        return self.render_to_response(self.get_context_data(form=form))


class DisponibilidadUpdateView(AdminTurnosRequiredMixin, UpdateView):
    model = DisponibilidadConfiguracion
    form_class = DisponibilidadConfiguracionForm
    template_name = 'turnos/backoffice/disponibilidad_form.html'
    pk_url_kwarg = 'disp_pk'

    def get_queryset(self):
        return DisponibilidadConfiguracion.objects.filter(configuracion_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'config': get_object_or_404(ConfiguracionTurnos, pk=self.kwargs['pk']),
                'disp': self.object,
                'titulo': 'Editar franja horaria',
            }
        )
        return context

    def form_valid(self, form):
        cleaned = form.cleaned_data
        if _hay_solapamiento(
            self.object.configuracion,
            cleaned["dia_semana"],
            cleaned["hora_inicio"],
            cleaned["hora_fin"],
            excluir_id=self.object.pk,
        ):
            messages.warning(
                self.request,
                "Atencion: esta franja se superpone con otra existente en el mismo dia.",
            )
        self.object = form.save()
        messages.success(self.request, 'Franja horaria actualizada.')
        return redirect('turnos:disponibilidad_grilla', pk=self.kwargs['pk'])


@admin_turnos_required
@require_POST
def disponibilidad_eliminar(request, pk, disp_pk):
    config = get_object_or_404(ConfiguracionTurnos, pk=pk)
    disp = get_object_or_404(DisponibilidadConfiguracion, pk=disp_pk, configuracion=config)
    turnos_afectados = TurnoCiudadano.objects.filter(
        configuracion=config,
        fecha__gte=date.today(),
        hora_inicio=disp.hora_inicio,
        estado__in=[TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO],
    ).count()

    if turnos_afectados:
        messages.error(
            request,
            f'No se puede eliminar: hay {turnos_afectados} turno(s) futuro(s) en ese horario.',
        )
        return redirect('turnos:disponibilidad_grilla', pk=config.pk)

    disp.delete()
    messages.success(request, 'Franja horaria eliminada.')
    return redirect('turnos:disponibilidad_grilla', pk=config.pk)


@admin_turnos_required
@require_POST
def configuracion_eliminar(request, pk):
    config = get_object_or_404(ConfiguracionTurnos, pk=pk)
    nombre = config.nombre
    turnos_futuros = TurnoCiudadano.objects.filter(
        configuracion=config,
        fecha__gte=date.today(),
        estado__in=[TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO],
    ).count()

    # Baja logica: conserva historial/turnos ya otorgados y evita nuevos turnos.
    config.activo = False
    config.save(update_fields=["activo", "modificado"])
    recurso = RecursoTurnos.objects.filter(configuracion_turnos=config).first()
    if recurso and recurso.activo:
        recurso.activo = False
        recurso.save(update_fields=["activo"])

    if turnos_futuros:
        messages.success(
            request,
            f'Configuracion "{nombre}" inactivada. Los {turnos_futuros} turno(s) futuro(s) ya otorgados seguiran su curso; no se daran nuevos turnos hasta reactivarla.',
        )
    else:
        messages.success(
            request,
            f'Configuracion "{nombre}" dada de baja logica. Se conserva historial y no se otorgaran nuevos turnos.',
        )
    return redirect('turnos:configuracion_lista')


configuracion_lista = operador_required(ConfiguracionListView.as_view())
configuracion_crear = ConfiguracionCreateView.as_view()
configuracion_editar = ConfiguracionUpdateView.as_view()
sedes_lista = SedeTurnoListView.as_view()
sede_detalle = SedeTurnoDetailView.as_view()
sede_crear = SedeTurnoCreateView.as_view()
sede_editar = SedeTurnoUpdateView.as_view()
disponibilidad_grilla = DisponibilidadGrillaView.as_view()
disponibilidad_agregar = DisponibilidadCreateView.as_view()
disponibilidad_editar = DisponibilidadUpdateView.as_view()


