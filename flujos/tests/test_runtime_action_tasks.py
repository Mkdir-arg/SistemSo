from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import Mock, patch

from flujos.interfaces.module_api import cancelar_instancia_inscripcion
from flujos.models import Flujo, TareaFlujo, VersionFlujo
from flujos.runtime import FlowRuntime
from legajos.models import Ciudadano
from legajos.models_programas import InscripcionPrograma, Programa


class FlowRuntimeActionTasksTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='runtime-flow-user',
            password='clave-segura-123',
            is_staff=True,
        )
        self.ciudadano = Ciudadano.objects.create(
            dni='30199887',
            nombre='Julia',
            apellido='Paz',
            genero=Ciudadano.Genero.FEMENINO,
            email='julia.paz@example.com',
        )
        self.programa = Programa.objects.create(
            codigo='PROG-RUNTIME-001',
            nombre='Programa Runtime',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        self.inscripcion = InscripcionPrograma.objects.create(
            ciudadano=self.ciudadano,
            programa=self.programa,
            estado=InscripcionPrograma.Estado.PENDIENTE,
        )
        self.flujo = Flujo.objects.create(
            programa=self.programa,
            nombre='Flujo Runtime',
        )
        self.version = VersionFlujo.objects.create(
            flujo=self.flujo,
            estado=VersionFlujo.Estado.PUBLICADA,
            definicion={
                'nodos': [
                    {'id': 'inicio', 'tipo': 'inicio', 'nombre': 'Inicio', 'config': {}},
                    {
                        'id': 'revision_manual',
                        'tipo': 'accion_humana',
                        'nombre': 'Revision manual',
                        'config': {'descripcion': 'Revisar documentacion'},
                    },
                    {'id': 'fin', 'tipo': 'fin', 'nombre': 'Fin', 'config': {}},
                ],
                'transiciones': [
                    {'desde': 'inicio', 'hasta': 'revision_manual', 'condicion': None},
                    {'desde': 'revision_manual', 'hasta': 'fin', 'condicion': None},
                ],
            },
            creado_por=self.user,
        )

        self.programa_email = Programa.objects.create(
            codigo='PROG-RUNTIME-EMAIL',
            nombre='Programa Runtime Email',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        self.inscripcion_email = InscripcionPrograma.objects.create(
            ciudadano=self.ciudadano,
            programa=self.programa_email,
            estado=InscripcionPrograma.Estado.PENDIENTE,
        )
        self.flujo_email = Flujo.objects.create(
            programa=self.programa_email,
            nombre='Flujo Runtime Email',
        )
        VersionFlujo.objects.create(
            flujo=self.flujo_email,
            estado=VersionFlujo.Estado.PUBLICADA,
            definicion={
                'schema_version': 4,
                'nodos': [
                    {'id': 'inicio', 'tipo': 'inicio', 'nombre': 'Inicio', 'config': {}},
                    {
                        'id': 'notificar',
                        'tipo': 'accion_email',
                        'nombre': 'Notificar ciudadano',
                        'config': {
                            'email': {
                                'to': ['{{ ciudadano.email }}'],
                                'subject': 'Alta en {{ programa.nombre }}',
                                'body': 'Hola {{ ciudadano.nombre_completo }}',
                            },
                        },
                    },
                    {'id': 'fin', 'tipo': 'fin', 'nombre': 'Fin', 'config': {}},
                ],
                'transiciones': [
                    {'desde': 'inicio', 'hasta': 'notificar', 'condicion': None},
                    {'desde': 'notificar', 'hasta': 'fin', 'condicion': None},
                ],
            },
            creado_por=self.user,
        )

        self.programa_http = Programa.objects.create(
            codigo='PROG-RUNTIME-HTTP',
            nombre='Programa Runtime HTTP',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        self.inscripcion_http = InscripcionPrograma.objects.create(
            ciudadano=self.ciudadano,
            programa=self.programa_http,
            estado=InscripcionPrograma.Estado.PENDIENTE,
        )
        self.flujo_http = Flujo.objects.create(
            programa=self.programa_http,
            nombre='Flujo Runtime HTTP',
        )
        VersionFlujo.objects.create(
            flujo=self.flujo_http,
            estado=VersionFlujo.Estado.PUBLICADA,
            definicion={
                'schema_version': 4,
                'nodos': [
                    {'id': 'inicio', 'tipo': 'inicio', 'nombre': 'Inicio', 'config': {}},
                    {
                        'id': 'sincronizar',
                        'tipo': 'accion_http',
                        'nombre': 'Sincronizar API',
                        'config': {
                            'http': {
                                'method': 'POST',
                                'url': 'https://example.com/api/flujo',
                                'headers': [
                                    {'key': 'Content-Type', 'value': 'application/json'},
                                ],
                                'body': '{"dni": "{{ ciudadano.dni }}"}',
                                'timeout_seconds': 10,
                            },
                        },
                    },
                    {'id': 'fin_ok', 'tipo': 'fin', 'nombre': 'Fin OK', 'config': {}},
                    {'id': 'fin_error', 'tipo': 'fin', 'nombre': 'Fin Error', 'config': {}},
                ],
                'transiciones': [
                    {'desde': 'inicio', 'hasta': 'sincronizar', 'condicion': None},
                    {
                        'desde': 'sincronizar',
                        'hasta': 'fin_ok',
                        'condicion': {'campo': 'acciones.sincronizar.ok', 'operador': '==', 'valor': True},
                    },
                    {'desde': 'sincronizar', 'hasta': 'fin_error', 'condicion': None},
                ],
            },
            creado_por=self.user,
        )

    def test_iniciar_crea_tarea_pendiente_para_accion_humana(self):
        instancia = FlowRuntime.iniciar(self.inscripcion)

        self.assertEqual(instancia.nodo_actual, 'revision_manual')
        tarea = instancia.tareas.get()
        self.assertEqual(tarea.estado, TareaFlujo.Estado.PENDIENTE)
        self.assertEqual(tarea.nodo_id, 'revision_manual')
        self.assertEqual(tarea.nombre, 'Revision manual')

    def test_avanzar_resuelve_tarea_pendiente_al_salir_de_accion_humana(self):
        instancia = FlowRuntime.iniciar(self.inscripcion)
        tarea = instancia.tareas.get()

        instancia = FlowRuntime.avanzar(instancia, datos={}, usuario=self.user)

        tarea.refresh_from_db()
        instancia.refresh_from_db()
        self.assertEqual(instancia.estado, instancia.Estado.COMPLETADA)
        self.assertEqual(tarea.estado, TareaFlujo.Estado.RESUELTA)
        self.assertEqual(tarea.resuelto_por, self.user)
        self.assertIsNotNone(tarea.fecha_resolucion)

    def test_cancelar_instancia_cancela_tareas_pendientes(self):
        instancia = FlowRuntime.iniciar(self.inscripcion)
        tarea = instancia.tareas.get()

        cancelar_instancia_inscripcion(
            inscripcion=self.inscripcion,
            usuario=self.user,
            motivo='Baja manual de prueba',
        )

        tarea.refresh_from_db()
        instancia.refresh_from_db()
        self.assertEqual(instancia.estado, instancia.Estado.CANCELADA)
        self.assertEqual(tarea.estado, TareaFlujo.Estado.CANCELADA)
        self.assertEqual(tarea.resuelto_por, self.user)

    def test_avanzar_acumula_datos_en_la_instancia(self):
        programa = Programa.objects.create(
            codigo='PROG-RUNTIME-002',
            nombre='Programa Runtime Datos',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        inscripcion = InscripcionPrograma.objects.create(
            ciudadano=self.ciudadano,
            programa=programa,
            estado=InscripcionPrograma.Estado.PENDIENTE,
        )
        flujo = Flujo.objects.create(
            programa=programa,
            nombre='Flujo Runtime Datos',
        )
        VersionFlujo.objects.create(
            flujo=flujo,
            estado=VersionFlujo.Estado.PUBLICADA,
            definicion={
                'nodos': [
                    {'id': 'inicio', 'tipo': 'inicio', 'nombre': 'Inicio', 'config': {}},
                    {'id': 'revision_manual', 'tipo': 'accion_humana', 'nombre': 'Revision manual', 'config': {}},
                    {'id': 'fin_aprobado', 'tipo': 'fin', 'nombre': 'Fin aprobado', 'config': {}},
                    {'id': 'fin_rechazado', 'tipo': 'fin', 'nombre': 'Fin rechazado', 'config': {}},
                ],
                'transiciones': [
                    {'desde': 'inicio', 'hasta': 'revision_manual', 'condicion': None},
                    {
                        'desde': 'revision_manual',
                        'hasta': 'fin_aprobado',
                        'condicion': {'campo': 'aprobado', 'operador': '==', 'valor': True},
                    },
                    {
                        'desde': 'revision_manual',
                        'hasta': 'fin_rechazado',
                        'condicion': {'campo': 'aprobado', 'operador': '==', 'valor': False},
                    },
                ],
            },
            creado_por=self.user,
        )

        instancia = FlowRuntime.iniciar(inscripcion)
        instancia = FlowRuntime.avanzar(
            instancia,
            datos={'aprobado': True, 'observacion': 'Apto para continuar'},
            usuario=self.user,
        )

        instancia.refresh_from_db()
        self.assertEqual(instancia.nodo_actual, 'fin_aprobado')
        self.assertEqual(instancia.datos['aprobado'], True)
        self.assertEqual(instancia.datos['observacion'], 'Apto para continuar')

    @patch('flujos.infrastructure.runtime_actions.send_mail')
    def test_iniciar_ejecuta_accion_email_y_completa_flujo(self, send_mail_mock):
        send_mail_mock.return_value = 1

        instancia = FlowRuntime.iniciar(self.inscripcion_email)

        instancia.refresh_from_db()
        send_mail_mock.assert_called_once()
        self.assertEqual(instancia.estado, instancia.Estado.COMPLETADA)
        self.assertEqual(instancia.nodo_actual, 'fin')
        self.assertTrue(instancia.datos['acciones']['notificar']['ok'])
        self.assertEqual(instancia.datos['acciones']['notificar']['to'], [self.ciudadano.email])

    @patch('flujos.infrastructure.runtime_actions.requests.request')
    def test_iniciar_ejecuta_accion_http_y_evalua_condicion_anidada(self, request_mock):
        response_mock = Mock()
        response_mock.ok = True
        response_mock.status_code = 200
        response_mock.reason = 'OK'
        response_mock.text = '{"ok": true}'
        response_mock.headers = {'Content-Type': 'application/json'}
        response_mock.json.return_value = {'ok': True}
        request_mock.return_value = response_mock

        instancia = FlowRuntime.iniciar(self.inscripcion_http)

        instancia.refresh_from_db()
        request_mock.assert_called_once()
        self.assertEqual(instancia.estado, instancia.Estado.COMPLETADA)
        self.assertEqual(instancia.nodo_actual, 'fin_ok')
        self.assertTrue(instancia.datos['acciones']['sincronizar']['ok'])
        self.assertEqual(instancia.datos['acciones']['sincronizar']['status_code'], 200)

    @patch('flujos.infrastructure.runtime_actions.requests.request')
    def test_iniciar_accion_http_no_ok_sigue_transicion_por_defecto(self, request_mock):
        response_mock = Mock()
        response_mock.ok = False
        response_mock.status_code = 500
        response_mock.reason = 'Server Error'
        response_mock.text = '{"ok": false}'
        response_mock.headers = {'Content-Type': 'application/json'}
        response_mock.json.return_value = {'ok': False}
        request_mock.return_value = response_mock

        instancia = FlowRuntime.iniciar(self.inscripcion_http)

        instancia.refresh_from_db()
        self.assertEqual(instancia.estado, instancia.Estado.COMPLETADA)
        self.assertEqual(instancia.nodo_actual, 'fin_error')
        self.assertFalse(instancia.datos['acciones']['sincronizar']['ok'])
        self.assertEqual(instancia.datos['acciones']['sincronizar']['status_code'], 500)