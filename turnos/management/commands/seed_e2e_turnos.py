from datetime import time, timedelta

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from legajos.models import Ciudadano
from portal.models import DisponibilidadTurnos, RecursoTurnos, TurnoCiudadano
from system_modules.infrastructure.services import set_module_enabled, sync_installed_modules


E2E_PREFIX = "E2E Turnos"
E2E_PASSWORD = "E2eTurnos123!"
E2E_CITIZEN_DNI = "88000001"
E2E_CITIZEN_EMAIL = "e2e.turnos.ciudadano@example.test"
E2E_OPERATOR_USERNAME = "e2e_turnos_operador"
E2E_OPERATOR_EMAIL = "e2e.turnos.operador@example.test"
E2E_RESOURCE_NAME = f"{E2E_PREFIX} Recurso"


class Command(BaseCommand):
    help = "Seeds deterministic data for the Turnos UI E2E flow."

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            sync_installed_modules()
            set_module_enabled("turnos", True)
        except Exception as exc:
            raise CommandError(f"No se pudo activar el modulo turnos: {exc}") from exc

        groups = {
            name: Group.objects.get_or_create(name=name)[0]
            for name in ("Ciudadanos", "turnoOperar", "turnoConfigurar")
        }

        citizen_user = self._upsert_user(
            username=E2E_CITIZEN_DNI,
            email=E2E_CITIZEN_EMAIL,
            first_name="E2E",
            last_name="Ciudadano",
            is_staff=False,
        )
        citizen_user.groups.set([groups["Ciudadanos"]])

        operator_user = self._upsert_user(
            username=E2E_OPERATOR_USERNAME,
            email=E2E_OPERATOR_EMAIL,
            first_name="E2E",
            last_name="Operador Turnos",
            is_staff=True,
        )
        operator_user.groups.set([groups["turnoOperar"], groups["turnoConfigurar"]])

        Ciudadano.objects.filter(usuario=citizen_user).exclude(dni=E2E_CITIZEN_DNI).update(
            usuario=None
        )
        Ciudadano.objects.update_or_create(
            dni=E2E_CITIZEN_DNI,
            defaults={
                "nombre": "E2E",
                "apellido": "Ciudadano",
                "genero": Ciudadano.Genero.NO_BINARIO,
                "telefono": "2600000000",
                "email": E2E_CITIZEN_EMAIL,
                "domicilio": "Domicilio E2E",
                "activo": True,
                "usuario": citizen_user,
            },
        )

        e2e_resources = RecursoTurnos.objects.filter(nombre__startswith=E2E_PREFIX)
        deleted_turnos, _ = TurnoCiudadano.objects.filter(
            Q(recurso__in=e2e_resources)
            | Q(ciudadano__dni=E2E_CITIZEN_DNI)
            | Q(motivo_consulta__startswith=E2E_PREFIX)
        ).delete()
        DisponibilidadTurnos.objects.filter(recurso__in=e2e_resources).delete()
        e2e_resources.exclude(nombre=E2E_RESOURCE_NAME).delete()

        resource, _ = RecursoTurnos.objects.update_or_create(
            nombre=E2E_RESOURCE_NAME,
            defaults={
                "tipo": RecursoTurnos.Tipo.ORGANISMO,
                "descripcion": "Recurso deterministico para pruebas UI E2E.",
                "direccion": "Domicilio E2E",
                "telefono": "2600000000",
                "email": "e2e.turnos.recurso@example.test",
                "activo": True,
                "requiere_aprobacion": True,
            },
        )

        target_date = timezone.localdate() + timedelta(days=1)
        for weekday in range(7):
            DisponibilidadTurnos.objects.update_or_create(
                recurso=resource,
                dia_semana=weekday,
                hora_inicio=time(9, 0),
                defaults={
                    "hora_fin": time(10, 0),
                    "duracion_turno_min": 30,
                    "cupo_maximo": 1,
                    "activo": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Seed E2E Turnos listo."))
        self.stdout.write(f"  Ciudadano: {E2E_CITIZEN_DNI} / {E2E_PASSWORD}")
        self.stdout.write(f"  Operador: {E2E_OPERATOR_USERNAME} / {E2E_PASSWORD}")
        self.stdout.write(f"  Recurso: {resource.nombre} (id={resource.pk})")
        self.stdout.write(f"  Fecha objetivo: {target_date.isoformat()}")
        self.stdout.write("  Disponibilidad: todos los dias 09:00-10:00")
        self.stdout.write(f"  Turnos E2E limpiados: {deleted_turnos}")

    def _upsert_user(self, *, username, email, first_name, last_name, is_staff):
        user, _ = User.objects.get_or_create(username=username)
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = True
        user.is_staff = is_staff
        user.is_superuser = False
        user.set_password(E2E_PASSWORD)
        user.save()
        return user
