from django.contrib.auth.models import User
from django.test import TestCase

from flujos.models import Flujo, VersionFlujo
from flujos.runtime import FlowRuntime
from legajos.models import Ciudadano
from legajos.models_programas import InscripcionPrograma, Programa


class FlowRuntimeCondicionesTests(TestCase):
    """Cubre el fix de espacios sobrantes al evaluar condiciones de transicion."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='runtime-condiciones-user',
            password='clave-segura-123',
            is_staff=True,
        )
        self.ciudadano = Ciudadano.objects.create(
            dni='30199888',
            nombre='Marta',
            apellido='Diaz',
            genero=Ciudadano.Genero.FEMENINO,
            email='marta.diaz@example.com',
        )

    def _crear_inscripcion_con_flujo(self, *, codigo, valor_condicion):
        programa = Programa.objects.create(
            codigo=codigo,
            nombre=f'Programa {codigo}',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        inscripcion = InscripcionPrograma.objects.create(
            ciudadano=self.ciudadano,
            programa=programa,
            estado=InscripcionPrograma.Estado.PENDIENTE,
        )
        flujo = Flujo.objects.create(programa=programa, nombre=f'Flujo {codigo}')
        VersionFlujo.objects.create(
            flujo=flujo,
            estado=VersionFlujo.Estado.PUBLICADA,
            definicion={
                'nodos': [
                    {'id': 'inicio', 'tipo': 'inicio', 'nombre': 'Inicio', 'config': {}},
                    {'id': 'revision', 'tipo': 'accion_humana', 'nombre': 'Revision', 'config': {}},
                    {'id': 'fin_ok', 'tipo': 'fin', 'nombre': 'Fin OK', 'config': {}},
                    {'id': 'fin_otro', 'tipo': 'fin', 'nombre': 'Fin otro', 'config': {}},
                ],
                'transiciones': [
                    {'desde': 'inicio', 'hasta': 'revision', 'condicion': None},
                    {
                        'desde': 'revision',
                        'hasta': 'fin_ok',
                        'condicion': {'campo': 'aprobado', 'operador': '==', 'valor': valor_condicion},
                    },
                    {'desde': 'revision', 'hasta': 'fin_otro', 'condicion': None},
                ],
            },
            creado_por=self.user,
        )
        return inscripcion

    def test_dato_con_espacio_sobrante_matchea_condicion_sin_espacio(self):
        inscripcion = self._crear_inscripcion_con_flujo(
            codigo='PROG-COND-001',
            valor_condicion='true',
        )
        instancia = FlowRuntime.iniciar(inscripcion)

        instancia = FlowRuntime.avanzar(instancia, datos={'aprobado': 'true '}, usuario=self.user)

        self.assertEqual(instancia.nodo_actual, 'fin_ok')

    def test_operador_in_strippea_cada_item_de_la_lista(self):
        inscripcion = self._crear_inscripcion_con_flujo(
            codigo='PROG-COND-002',
            valor_condicion=['aprobado', 'aprobado_con_reservas'],
        )
        instancia = FlowRuntime.iniciar(inscripcion)

        instancia = FlowRuntime.avanzar(
            instancia,
            datos={'aprobado': ' aprobado'},
            usuario=self.user,
        )

        self.assertEqual(instancia.nodo_actual, 'fin_ok')

    def test_valor_no_string_no_se_modifica(self):
        inscripcion = self._crear_inscripcion_con_flujo(
            codigo='PROG-COND-003',
            valor_condicion=True,
        )
        instancia = FlowRuntime.iniciar(inscripcion)

        instancia = FlowRuntime.avanzar(instancia, datos={'aprobado': True}, usuario=self.user)

        self.assertEqual(instancia.nodo_actual, 'fin_ok')
