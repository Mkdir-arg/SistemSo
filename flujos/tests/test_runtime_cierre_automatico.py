from django.contrib.auth.models import User
from django.test import TestCase

from flujos.models import Flujo, VersionFlujo
from flujos.runtime import FlowRuntime
from legajos.models import Ciudadano
from legajos.models_programas import InscripcionPrograma, Programa


class FlowRuntimeCierreAutomaticoTests(TestCase):
    """Cubre el cierre automatico de InscripcionPrograma en programas UN_SOLO_ACTO."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='runtime-cierre-user',
            password='clave-segura-123',
            is_staff=True,
        )
        self.ciudadano = Ciudadano.objects.create(
            dni='30199889',
            nombre='Carla',
            apellido='Rios',
            genero=Ciudadano.Genero.FEMENINO,
            email='carla.rios@example.com',
        )

    def _crear_inscripcion(self, *, codigo, naturaleza, estado=InscripcionPrograma.Estado.PENDIENTE):
        programa = Programa.objects.create(
            codigo=codigo,
            nombre=f'Programa {codigo}',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
            naturaleza=naturaleza,
        )
        inscripcion = InscripcionPrograma.objects.create(
            ciudadano=self.ciudadano,
            programa=programa,
            estado=estado,
        )
        flujo = Flujo.objects.create(programa=programa, nombre=f'Flujo {codigo}')
        VersionFlujo.objects.create(
            flujo=flujo,
            estado=VersionFlujo.Estado.PUBLICADA,
            definicion={
                'nodos': [
                    {'id': 'inicio', 'tipo': 'inicio', 'nombre': 'Inicio', 'config': {}},
                    {'id': 'revision', 'tipo': 'accion_humana', 'nombre': 'Revision', 'config': {}},
                    {'id': 'fin', 'tipo': 'fin', 'nombre': 'Fin', 'config': {}},
                ],
                'transiciones': [
                    {'desde': 'inicio', 'hasta': 'revision', 'condicion': None},
                    {'desde': 'revision', 'hasta': 'fin', 'condicion': None},
                ],
            },
            creado_por=self.user,
        )
        return inscripcion

    def test_un_solo_acto_cierra_inscripcion_al_llegar_a_fin(self):
        inscripcion = self._crear_inscripcion(
            codigo='PROG-CIERRE-001',
            naturaleza=Programa.Naturaleza.UN_SOLO_ACTO,
        )
        instancia = FlowRuntime.iniciar(inscripcion)

        FlowRuntime.avanzar(instancia, datos={}, usuario=self.user)

        inscripcion.refresh_from_db()
        self.assertEqual(inscripcion.estado, InscripcionPrograma.Estado.CERRADO)
        self.assertIn('Cierre automático', inscripcion.motivo_cierre)
        self.assertIsNotNone(inscripcion.fecha_cierre)

    def test_persistente_no_cierra_inscripcion_al_llegar_a_fin(self):
        inscripcion = self._crear_inscripcion(
            codigo='PROG-CIERRE-002',
            naturaleza=Programa.Naturaleza.PERSISTENTE,
        )
        instancia = FlowRuntime.iniciar(inscripcion)

        FlowRuntime.avanzar(instancia, datos={}, usuario=self.user)

        inscripcion.refresh_from_db()
        self.assertEqual(inscripcion.estado, InscripcionPrograma.Estado.PENDIENTE)
        self.assertEqual(inscripcion.motivo_cierre, '')

    def test_naturaleza_none_no_cierra_inscripcion(self):
        inscripcion = self._crear_inscripcion(
            codigo='PROG-CIERRE-003',
            naturaleza=None,
        )
        instancia = FlowRuntime.iniciar(inscripcion)

        FlowRuntime.avanzar(instancia, datos={}, usuario=self.user)

        inscripcion.refresh_from_db()
        self.assertEqual(inscripcion.estado, InscripcionPrograma.Estado.PENDIENTE)

    def test_inscripcion_ya_dada_de_baja_no_se_sobreescribe(self):
        inscripcion = self._crear_inscripcion(
            codigo='PROG-CIERRE-004',
            naturaleza=Programa.Naturaleza.UN_SOLO_ACTO,
        )
        instancia = FlowRuntime.iniciar(inscripcion)

        inscripcion.estado = InscripcionPrograma.Estado.DADO_DE_BAJA
        inscripcion.motivo_cierre = 'Baja manual previa'
        inscripcion.save(update_fields=['estado', 'motivo_cierre'])

        FlowRuntime.avanzar(instancia, datos={}, usuario=self.user)

        inscripcion.refresh_from_db()
        self.assertEqual(inscripcion.estado, InscripcionPrograma.Estado.DADO_DE_BAJA)
        self.assertEqual(inscripcion.motivo_cierre, 'Baja manual previa')
