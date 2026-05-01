from datetime import date, time

from django.contrib.auth.models import User
from django.test import TestCase

from legajos.models import Ciudadano
from portal.models import TurnoCiudadano
from turnos.interfaces.module_api import (
    TurnoActionError,
    aprobar_turno_backoffice,
    completar_turno_backoffice,
    rechazar_turno_backoffice,
)


class TurnosBackofficeServiceTests(TestCase):
    def setUp(self):
        self.operador = User.objects.create_user(
            username="operador-turnos", password="clave-segura-123"
        )
        self.ciudadano = Ciudadano.objects.create(
            dni="12345678",
            nombre="Ana",
            apellido="Perez",
            genero="F",
            email="ana@example.com",
        )

    def create_turno(self, estado=TurnoCiudadano.Estado.PENDIENTE):
        return TurnoCiudadano.objects.create(
            ciudadano=self.ciudadano,
            fecha=date.today(),
            hora_inicio=time(10, 0),
            hora_fin=time(10, 30),
            estado=estado,
        )

    def test_aprobar_turno_confirma_y_audita(self):
        turno = self.create_turno()

        aprobar_turno_backoffice(
            turno.pk, self.operador, notas="Confirmado por backoffice"
        )

        turno.refresh_from_db()
        self.assertEqual(turno.estado, TurnoCiudadano.Estado.CONFIRMADO)
        self.assertEqual(turno.aprobado_por, self.operador)
        self.assertEqual(turno.notas_backoffice, "Confirmado por backoffice")
        self.assertIsNotNone(turno.fecha_aprobacion)

    def test_rechazar_turno_pendiente_lo_cancela(self):
        turno = self.create_turno()

        rechazar_turno_backoffice(
            turno.pk, self.operador, "Sin cupo disponible"
        )

        turno.refresh_from_db()
        self.assertEqual(turno.estado, TurnoCiudadano.Estado.CANCELADO_SISTEMA)
        self.assertEqual(turno.notas_backoffice, "Sin cupo disponible")
        self.assertEqual(turno.aprobado_por, self.operador)

    def test_completar_turno_falla_si_no_esta_confirmado(self):
        turno = self.create_turno()

        with self.assertRaises(TurnoActionError):
            completar_turno_backoffice(turno)
