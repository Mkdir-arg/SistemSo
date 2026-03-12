from .models import EvaluacionInicial, Profesional


class LegajoWorkflowService:
    @staticmethod
    def get_or_create_profesional(usuario):
        profesional, _ = Profesional.objects.get_or_create(
            usuario=usuario,
            defaults={'rol': 'Operador'},
        )
        return profesional

    @classmethod
    def get_or_create_evaluacion(cls, legajo):
        evaluacion, _ = EvaluacionInicial.objects.get_or_create(
            legajo=legajo,
            defaults={},
        )
        return evaluacion

    @staticmethod
    def save_evaluacion_from_form(form, legajo):
        evaluacion = form.save(commit=False)
        evaluacion.legajo = legajo
        evaluacion.tamizajes = form.build_tamizajes_payload()
        evaluacion.save()
        return evaluacion

    @classmethod
    def save_plan_from_form(cls, form, legajo, usuario):
        plan = form.save(commit=False)
        plan.legajo = legajo
        if not plan.profesional_id:
            plan.profesional = cls.get_or_create_profesional(usuario)
        plan.actividades = form.get_actividades_payload()
        plan.save()
        return plan

    @classmethod
    def save_seguimiento_from_form(cls, form, legajo, usuario):
        seguimiento = form.save(commit=False)
        seguimiento.legajo = legajo
        if not seguimiento.profesional_id:
            seguimiento.profesional = cls.get_or_create_profesional(usuario)
        seguimiento.save()
        return seguimiento

    @staticmethod
    def save_derivacion_from_form(form, legajo):
        derivacion = form.save(commit=False)
        derivacion.legajo = legajo
        derivacion.save()
        return derivacion

    @staticmethod
    def close_legajo(legajo, motivo_cierre, usuario):
        legajo.cerrar(motivo_cierre=motivo_cierre, usuario=usuario)
        return legajo

    @staticmethod
    def reopen_legajo(legajo, motivo_reapertura, usuario):
        legajo.reabrir(motivo_reapertura=motivo_reapertura, usuario=usuario)
        return legajo
